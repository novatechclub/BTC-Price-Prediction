import pandas as pd
import numpy as np
import polars as pl
from datetime import datetime


class NTCTapDataMetaModel:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._convert_possible_datetimes()
        self.df_features = self.df.columns.tolist()

    def _convert_possible_datetimes(self):
        for col in self.df.select_dtypes(include=["object", "string"]).columns:
            try:
                sample = self.df[col].dropna().iloc[:10]
                parsed = pd.to_datetime(sample, utc=True, errors="raise")
                self.df[col] = pd.to_datetime(self.df[col], utc=True, errors="coerce")
            except Exception:
                continue

    def summarize(self, feature=None):
        if feature:
            return self._summarize_feature(self.df[feature])
        else:
            summary = {}
            for col in self.df.columns:
                summary[col] = self._summarize_feature(self.df[col])
            self.summary = summary
            return summary

    def _summarize_feature(self, col_data):
        col_summary = {
            "dtype": self._general_type(col_data),
            "unique_values": int(col_data.nunique()),
            "missing_values": int(col_data.isna().sum()),
            "examples": col_data.dropna().unique()[:10].tolist()
        }

        if pd.api.types.is_numeric_dtype(col_data):
            col_summary.update({
                "min": col_data.min(),
                "max": col_data.max(),
                "mean": col_data.mean(),
                "median": col_data.median(),
                "std": col_data.std(),
                "25%": col_data.quantile(0.25),
                "75%": col_data.quantile(0.75)
            })
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            col_summary.update({
                "start": col_data.min(),
                "end": col_data.max(),
                "range_days": (col_data.max() - col_data.min()).days
            })

        return col_summary

    def _general_type(self, series):
        if pd.api.types.is_string_dtype(series):
            return "string"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_numeric_dtype(series):
            return "float" if pd.api.types.is_float_dtype(series) else "integer"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif series.apply(lambda x: isinstance(x, list)).any():
            return "list"
        elif series.apply(lambda x: isinstance(x, dict)).any():
            return "dictionary"
        else:
            return "unknown"


class DataMetaModelPolars(NTCTapDataMetaModel):
    def __init__(self, df: pl.DataFrame):
        self.df = df.clone()
        self._convert_possible_datetimes()
        self.df_features = self.df.columns

    def _convert_possible_datetimes(self):
        """
        Detect and convert string columns to datetime in a Polars DataFrame.
        """
        for col in self.df.columns:
            if self.df[col].dtype == pl.Utf8:
                try:
                    # Try parsing a sample
                    parsed = self.df[col].limit(10).drop_nulls().str.strptime(pl.Datetime, strict=True)
                    # Apply conversion
                    self.df = self.df.with_columns(
                        self.df[col].str.strptime(pl.Datetime, strict=False).alias(col)
                    )
                except pl.ComputeError:
                    continue

    def summarize(self, feature=None):
        if feature:
            return self._summarize_feature(self.df[feature])
        else:
            return {col: self._summarize_feature(self.df[col]) for col in self.df.columns}

    def _summarize_feature(self, series: pl.Series):
        summary = {
            "dtype": str(series.dtype),
            "unique_values": series.n_unique(),
            "missing_values": series.null_count(),
            "examples": [
                self._format_datetime(val) for val in series.drop_nulls().limit(10)
            ],
        }

        if series.dtype.is_numeric():
            summary.update({
                "min": series.min(),
                "max": series.max(),
                "mean": series.mean(),
                "median": series.median(),
                "mode": series.mode().to_list()[0] if series.mode().len() > 0 else None,
                "std": series.std(),
                "25%-quantile": series.quantile(0.25, "nearest"),
                "75%-quantile": series.quantile(0.75, "nearest"),
            })
        elif series.dtype.is_temporal():
            start = series.min()
            end = series.max()
            summary.update({
                "start": self._format_datetime(start),
                "end": self._format_datetime(end),
                "range_days": (end - start).days
            })

        return summary

    def _format_datetime(self, val):
        if isinstance(val, datetime):
            return val.isoformat()
        return val