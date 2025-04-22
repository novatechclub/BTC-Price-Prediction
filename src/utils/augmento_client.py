#augmento_client.py


import os
import requests
import json
import logging
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import networkx as nx
#import random
import sys
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


class AugmentoAPIClient:
    BASE_URL = "https://api.augmento.ai/v0.1"

    def __init__(self, base_path=".", log_level=logging.INFO):
        self.base_path = Path(base_path).resolve()
        self.assets_dir = self.base_path / "app_assets" / "augmento_client_assets"
        self.summary_file = self.assets_dir / "augmento_api_summary.json"
        self.log_file = self.assets_dir / "augmento_client.log"

        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger(log_level)

        self.logger.info("Initializing AugmentoAPIClient...")

        if self.summary_file.exists():
            self.logger.info(f"Summary file exists at {self.summary_file}. Loading from file.")
            self.summary_data = self._load_summary()
        else:
            self.logger.info("Summary file not found. Fetching data from API...")
            try:
                self.summary_data = self._build_summary()
                self._save_summary()
                self.logger.info("Summary data fetched and saved successfully.")
            except Exception as e:
                self.logger.error(f"Failed to initialize summary: {e}", exc_info=True)
                raise

    def _setup_logger(self, log_level):
        logger = logging.getLogger("AugmentoAPIClient")
        logger.setLevel(log_level)

        # Avoid duplicate handlers
        if not logger.handlers:
            # File logging
            fh = logging.FileHandler(self.log_file, mode='w')
            fh.setLevel(log_level)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)

            # Stream to notebook/stdout
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(log_level)
            sh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(sh)

        return logger

    def _build_summary(self):
        self.logger.info("Fetching API data for summary...")
        raw_topics = self._get_topics()
        categorized_topics = self._categorize_topics_flat(raw_topics)
    
        return {
            "Datetime": self._get_datetime(),
            "Sources": self._get_sources(),
            "Coins": self._get_coins(),
            "Bin_sizes": self._get_bin_sizes(),
            "Topics": {
                "raw_topics": raw_topics,
                "categorized_topics": categorized_topics
            }
        }
    
    
    @staticmethod
    def _categorize_topics_flat(raw_topics):
        """
        Simplified topic categorization:
        - Sentiment_Topics grouped by known emotional categories
        - Everything else in Other_Topics
        """
        sentiment_mapping = {
            "FOMO": [11],
            "Uncertain": [28],
            "Hopeful": [42],
            "Positive": [38, 91, 23, 39, 75, 42],
            "Negative": [26, 6, 85, 54, 53, 1, 14, 73, 92]
        }

        # Make int keys → name
        id_to_name = {int(k): v for k, v in raw_topics.items()}

        sentiment_topics = {}
        used_ids = set()

        for sentiment_group, ids in sentiment_mapping.items():
            sentiment_topics[sentiment_group] = {
                str(i): id_to_name[i] for i in ids if i in id_to_name
            }
            used_ids.update(ids)

        # Other_Topics = all not in sentiment
        other_topics = {
            str(i): name for i, name in id_to_name.items() if i not in used_ids
        }

        return {
            "Other_Topics": other_topics,
            "Sentiment_Topics": sentiment_topics
        }
   
    def _fetch_data(self, endpoint):
        url = f"{self.BASE_URL}{endpoint}"
        self.logger.debug(f"Requesting {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.logger.info(f"Fetched {endpoint} successfully.")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {endpoint}: {e}", exc_info=True)
            raise

    def _get_datetime(self):
        return self._fetch_data("/datetime")

    def _get_sources(self):
        return self._fetch_data("/sources")

    def _get_coins(self):
        return self._fetch_data("/coins")

    def _get_bin_sizes(self):
        return self._fetch_data("/bin_sizes")

    def _get_topics(self):
        return self._fetch_data("/topics")

    def _save_summary(self):
        with open(self.summary_file, "w") as f:
            json.dump(self.summary_data, f, indent=4)
        self.logger.info(f"Summary saved to {self.summary_file}")

    def _load_summary(self):
        with open(self.summary_file, "r") as f:
            return json.load(f)

    def get_summary(self):
        return self.summary_data
    
    def load_topic_column_names(self, source: str = "twitter"):
        with open(self.summary_file, "r") as f:
            metadata = json.load(f)

        raw_topics = metadata["Topics"]["raw_topics"]
        topic_columns = {
            int(idx): f"{source}_{name.lower().replace('/', '_').replace(' ', '_')}".replace("-", "_").replace("(", "").replace(")", "")
            for idx, name in raw_topics.items()
        }
        return topic_columns

    def _fetch_data_range(self, start_dt, end_dt, topic_columns, source="twitter", coin="bitcoin", bin_size="1H"):
        url = f"{self.BASE_URL}/events/aggregated"
        params = {
            "source": source,
            "coin": coin,
            "bin_size": bin_size,
            "count_ptr": 1000,
            "start_ptr": 0,
            "start_datetime": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_datetime": end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            rows = []
            for item in data:
                row = {
                    "datetime": item["datetime"],
                    "t_epoch": item["t_epoch"],
                    "coin_type": coin,          # <-- Injecting additional metadata here
                    "source": source,           # <-- Injecting additional metadata here
                    "bin_size": bin_size        # <-- Injecting additional metadata here
                }
                for i, count in enumerate(item["counts"]):
                    column_name = topic_columns.get(i, f"{source}_unknown_{i}")
                    row[column_name] = count
                rows.append(row)
            return pd.DataFrame(rows)
        except Exception as e:
            self.logger.error(f"Failed to fetch data from {start_dt} to {end_dt}: {e}")
            return pd.DataFrame()

    def download_full_dataset(
        self,
        start_date="2016-11-01 23:00:00",
        end_date="2025-02-01 00:00:01",
        source="twitter",
        coin="bitcoin",
        bin_size="1H",  # NEW
        max_workers=10
    ):
        self.source = source
        self.coin = coin
        self.bin_size = bin_size.upper()
        self.start_date = start_date
        self.end_date = end_date
        topic_columns = self.load_topic_column_names(source=source)

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        # Filename format
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")
        filename = self.assets_dir / f"{source}_{bin_size}_{start_str}_{end_str}.parquet"

        # Caching logic
        if filename.exists():
            self.logger.info(f"Cached file found at {filename}. Loading instead of downloading.")
            return pd.read_parquet(filename)

        # Build list of month ranges
        monthly_ranges = []
        current = start
        while current < end:
            next_month = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
            monthly_ranges.append((current, min(next_month, end)))
            current = next_month

        self.logger.info(f"Starting download from {start_date} to {end_date} using {max_workers} threads.")

        all_dataframes = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._fetch_data_range, start, end, topic_columns, source, coin, bin_size): (start, end)
                for start, end in monthly_ranges
            }

            for future in as_completed(futures):
                time_range = futures[future]
                try:
                    df = future.result()
                    if not df.empty:
                        all_dataframes.append(df)
                        self.logger.info(f"Loaded data from {time_range[0]} to {time_range[1]} with {len(df)} rows.")
                    else:
                        self.logger.warning(f"No data returned for range {time_range[0]} to {time_range[1]}.")
                except Exception as e:
                    self.logger.error(f"Failed to fetch data for range {time_range}: {e}")

        if not all_dataframes:
            raise RuntimeError("No data collected. Aborting.")

        final_df = pd.concat(all_dataframes).sort_values("datetime").reset_index(drop=True)
        final_df.to_parquet(filename, index=False)

        self.logger.info(f"Final dataset saved to {filename} with shape {final_df.shape}.")

        self.last_df = final_df


        return final_df

    def get_session_metadata(self):
        return {
            "source": self.source,
            "coin": self.coin,
            "bin_size": self.bin_size,
            "start_date": self.start_date,
            "end_date": self.end_date
        }


    
