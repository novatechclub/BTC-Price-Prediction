# augmento_datawrangler.py

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

    def load_dataset(self, filepath, name=None):
        path = Path(filepath)
        if not name:
            name = path.stem

        if path.suffix == ".csv":
            df = pd.read_csv(path, parse_dates=True)
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported format: {path.suffix}")

        self.datasets[name] = df
        self.metadata[name] = {
            "rows": df.shape[0],
            "columns": df.columns.tolist(),
            "path": str(path.resolve())
        }

        return df

    def join_datasets(self, keys=["datetime"], how="inner"):
        if len(self.datasets) < 2:
            raise ValueError("Need at least 2 datasets to join.")

        dfs = list(self.datasets.values())
        names = list(self.datasets.keys())

        df = dfs[0]
        for i in range(1, len(dfs)):
            df = pd.merge(
                df, dfs[i], on=keys, how=how,
                suffixes=("", f"_{names[i]}")
            )

        self.joined_df = df
        return df

    def get_metadata(self):
        return self.metadata

    def get_joined(self):
        return self.joined_df
