# ts_analysis/data_wrangling.py

import pandas as pd

class DataWrangling:
    def __init__(self, df: pd.DataFrame, datetime_col: str = "timestamp"):
        self.df = df.copy()
        self.datetime_col = datetime_col
        self._prepare()

    def _prepare(self):
        self.df[self.datetime_col] = pd.to_datetime(self.df[self.datetime_col])
        self.df.set_index(self.datetime_col, inplace=True)
        self.df.sort_index(inplace=True)

    def resample_data(self, freq='D'):
        return self.df.resample(freq).mean()

    def fill_missing(self, method='ffill'):
        return self.df.fillna(method=method)

    def get_features_and_target(self, target_col: str):
        X = self.df.drop(columns=[target_col])
        y = self.df[target_col]
        return X, y
