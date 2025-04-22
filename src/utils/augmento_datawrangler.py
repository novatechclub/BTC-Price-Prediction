# utils/augmento_datawrangler.py

from pathlib import Path
import pandas as pd
from datetime import datetime


class AugmentoDataWrangler:
    def __init__(self):
        self.datasets = {}
        self.metadata = {}
        self.joined_df = None

    def import_from_session(self, dataset_list):
        for item in dataset_list:
            name = item["name"]
            df = item["df"]
            self.datasets[name] = df
            self.metadata[name] = {
                "rows": df.shape[0],
                "columns": df.columns.tolist(),
                "imported_at": datetime.now().isoformat(),
                "path": f"[session:{name}]"
            }
        return self

    def load_dataset(self, filepath, name=None):
        path = Path(filepath)
        if not name:
            name = path.stem

        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, parse_dates=True)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported format: {path.suffix}")

        self.datasets[name] = df
        self.metadata[name] = {
            "rows": df.shape[0],
            "columns": df.columns.tolist(),
            "path": str(path.resolve())
        }
        return self

#    def join_datasets(self, keys=["datetime"], how="inner") -> pd.DataFrame:
#        """
#        Join all loaded datasets on the given keys and return the resulting DataFrame.
#        Raises if fewer than two datasets are loaded.
#        """
#        if len(self.datasets) < 2:
#            raise ValueError("Need at least 2 datasets to join.")
#
#        dfs   = list(self.datasets.values())
#        names = list(self.datasets.keys())
#
#        # start with the first DataFrame
#        df = dfs[0]
#        for i in range(1, len(dfs)):
#            df = pd.merge(
#                df,
#                dfs[i],
#                on=keys,
#                how=how,
#                suffixes=("", f"_{names[i]}")
#            )
#
#        self.joined_df = df
#        return df                  # ← was `return self` before

    def join_datasets(self, keys=["datetime"], how="inner") -> pd.DataFrame:
        """
        Join all loaded datasets on the given keys (coercing any tz‑aware or object
        columns to naive datetimes) and return the resulting DataFrame.
        Raises if fewer than two datasets are loaded.
        """
        if len(self.datasets) < 2:
            raise ValueError("Need at least 2 datasets to join.")

        dfs   = list(self.datasets.values())
        names = list(self.datasets.keys())

        # Helper to normalize a single df's key columns
        def _normalize_keys(df, keys):
            for k in keys:
                if k not in df.columns:
                    continue
                series = df[k]
                # If tz‑aware datetime, drop tz
                if pd.api.types.is_datetime64_any_dtype(series):
                    if series.dt.tz is not None:
                        df[k] = series.dt.tz_convert("UTC").dt.tz_localize(None)
                # If object, try parsing to datetime
                elif pd.api.types.is_object_dtype(series):
                    try:
                        df[k] = pd.to_datetime(series)
                    except (ValueError, TypeError):
                        pass
            return df

        # Start with a copy of the first dataset
        left = dfs[0].copy()
        left = _normalize_keys(left, keys)

        for i, right_orig in enumerate(dfs[1:], start=1):
            right = right_orig.copy()
            right = _normalize_keys(right, keys)

            left = pd.merge(
                left,
                right,
                on=keys,
                how=how,
                suffixes=("", f"_{names[i]}")
            )

        self.joined_df = left
        return left


    def get_metadata(self):
        return self.metadata

    def get_joined(self):
        return self.joined_df

    # --- Column-level operations ---
    def drop_columns(self, dataset_name: str, columns: list[str]):
        df = self.datasets.get(dataset_name)
        if df is not None:
            df.drop(columns=columns, inplace=True, errors='ignore')
            if dataset_name in self.metadata:
                self.metadata[dataset_name]['columns'] = df.columns.tolist()
                self.metadata[dataset_name]['rows']    = df.shape[0]
        return self

    def rename_column(self, dataset_name: str, old_name: str, new_name: str):
        df = self.datasets.get(dataset_name)
        if df is not None and old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)
            if dataset_name in self.metadata:
                cols = self.metadata[dataset_name]['columns']
                self.metadata[dataset_name]['columns'] = [
                    (new_name if c == old_name else c) for c in cols
                ]
        return self

    def select_columns(self, dataset_name: str, columns: list[str]):
        df = self.datasets.get(dataset_name)
        if df is not None:
            valid_cols = [c for c in columns if c in df.columns]
            self.datasets[dataset_name] = df.loc[:, valid_cols].copy()
            if dataset_name in self.metadata:
                self.metadata[dataset_name]['columns'] = valid_cols
                self.metadata[dataset_name]['rows']    = self.datasets[dataset_name].shape[0]
        return self

    # --- Row-level operations ---
    def filter_rows_by_range(self, dataset_name: str, column: str, start, end):
        df = self.datasets.get(dataset_name)
        if df is None or column not in df.columns:
            return self

        series = df[column]
        # Datetime
        if pd.api.types.is_datetime64_any_dtype(series) or \
           pd.api.types.is_timedelta64_dtype(series):
            series = pd.to_datetime(series)
            mask   = series.between(start, end)
        # Numeric
        elif pd.api.types.is_numeric_dtype(series):
            mask = series.between(start, end)
        # Object/String
        elif pd.api.types.is_object_dtype(series) or \
             pd.api.types.is_string_dtype(series):
            try:
                mask = series.isin(start)
            except Exception:
                return self
        else:
            return self

        filtered = df.loc[mask].copy()
        self.datasets[dataset_name] = filtered
        if dataset_name in self.metadata:
            self.metadata[dataset_name]['rows'] = filtered.shape[0]
        return self

    def sample(self, dataset_name: str, frac: float = 0.1, random_state: int = None):
        df = self.datasets.get(dataset_name)
        if df is None:
            return self
        sampled = df.sample(frac=frac, random_state=random_state)
        self.datasets[dataset_name] = sampled
        if dataset_name in self.metadata:
            self.metadata[dataset_name]['rows'] = sampled.shape[0]
        return self
