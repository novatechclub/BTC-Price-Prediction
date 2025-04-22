# utils/data_cleaner.py

import pandas as pd

class DataCleaner:
    """
    A helper class to manage preprocessing of session DataFrames.

    Usage:
        cleaner = DataCleaner(df)
        cleaner.select_columns([...])                # choose which columns to keep
               .add_filter('col', lambda s: s > 0)    # chain any number of per‑column filters
        cleaned_df = cleaner.get_cleaned()
    """

    def __init__(self, df: pd.DataFrame):
        # keep an untouched copy of the original
        self._original = df.copy()
        # mapping: column_name -> boolean‐mask function
        self._filters = {}
        # if not None, list of columns to keep
        self._keep_cols: list[str] | None = None

    def select_columns(self, columns: list[str] | None):
        """
        Specify exactly which columns to keep.
        Pass None to reset to all columns.
        """
        self._keep_cols = list(columns) if columns is not None else None
        return self

    def add_filter(self, column: str, func: callable):
        """
        Add a filter function for one column.
        `func` should take a pd.Series and return a boolean Series.
        """
        self._filters[column] = func
        return self

    def clear_filters(self):
        """Drop all filters, but keep any column selection."""
        self._filters.clear()
        return self

    def reset(self):
        """Reset both column selection and filters to start over."""
        self._filters.clear()
        self._keep_cols = None
        return self

    def get_cleaned(self) -> pd.DataFrame:
        """
        Apply the current column selection and all filters to the original DataFrame,
        and return the result.
        """
        df = self._original.copy()

        # 1) Column selection
        if self._keep_cols is not None:
            # only keep those that actually exist
            cols = [c for c in self._keep_cols if c in df.columns]
            df = df[cols]

        # 2) Per‑column filters
        for col, func in self._filters.items():
            if col in df.columns:
                mask = func(df[col])
                df = df[mask]

        return df
