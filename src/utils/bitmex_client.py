import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class BitmexClient:
    BASE_URL = "https://www.bitmex.com/api/v1"
    ASSETS_DIR = Path("app_assets/bitmex_client_assets")

    def __init__(self, log_level=logging.INFO):
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, level):
        logger = logging.getLogger("BitmexClient")
        logger.setLevel(level)
        if not logger.handlers:
            sh = logging.StreamHandler()
            sh.setLevel(level)
            sh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            logger.addHandler(sh)
        return logger

    def _generate_time_chunks(self, start_dt, end_dt, bin_size, max_count):
        bin_minutes = {
            "1m": 1,
            "5m": 5,
            "1h": 60,
            "1d": 1440
        }[bin_size]

        chunk_size = timedelta(minutes=bin_minutes * max_count)
        current = start_dt
        ranges = []

        while current < end_dt:
            next_time = min(current + chunk_size, end_dt)
            ranges.append((current, next_time))
            current = next_time

        return ranges

    def load_topic_column_names(self, source: str = "bitmex"):
        return {
            0: f"{source}_open",
            1: f"{source}_high",
            2: f"{source}_low",
            3: f"{source}_close",
            4: f"{source}_volume",
            5: f"{source}_vwap",
            6: f"{source}_turnover",
            7: f"{source}_homeNotional",
            8: f"{source}_foreignNotional",
            9: f"{source}_trades",
            10: f"{source}_lastSize"
        }


    def fetch_bucketed_data(
        self,
        start_date,
        end_date,
        symbol="XBTUSD",
        bin_size="1h",
        max_per_request=750,
        max_workers=6
    ):
        start_dt = pd.to_datetime(start_date, utc=True)
        end_dt = pd.to_datetime(end_date, utc=True)

        self.logger.info(f"Fetching BitMEX data from {start_dt} to {end_dt} in parallel using {max_workers} threads.")
        time_ranges = self._generate_time_chunks(start_dt, end_dt, bin_size, max_per_request)

        def fetch_chunk(start_dt, end_dt):
            params = {
                "symbol": symbol,
                "binSize": bin_size,
                "count": max_per_request,
                "partial": False,
                "startTime": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endTime": end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            self.logger.info(f"Thread fetching: {params['startTime']} → {params['endTime']}")
            try:
                r = requests.get(f"{self.BASE_URL}/trade/bucketed", params=params, timeout=10)
                r.raise_for_status()
                data = r.json()

                for row in data:
                    ts = row["timestamp"]
                    row["datetime"] = pd.to_datetime(ts, utc=False)
                    row["t_epoch"] = int(pd.to_datetime(ts).timestamp())
                    row["symbol"] = symbol
                    row["bin_size"] = bin_size
                    row["exchange"] = "bitmex"

                return pd.DataFrame(data)

            except Exception as e:
                self.logger.error(f"Failed to fetch {start_dt} → {end_dt}: {e}")
                return pd.DataFrame()

        all_dataframes = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_chunk, start, end): (start, end) for (start, end) in time_ranges
            }

            for future in as_completed(futures):
                df = future.result()
                s, e = futures[future]
                if not df.empty:
                    all_dataframes.append(df)
                    self.logger.info(f"✅ Loaded {len(df)} rows from {s} → {e}")
                else:
                    self.logger.warning(f"⚠️ Empty result for {s} → {e}")

        if not all_dataframes:
            raise RuntimeError("No data collected from BitMEX.")

        final_df = pd.concat(all_dataframes).sort_values("datetime").reset_index(drop=True)
        return final_df
