import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class BaseTimeSeriesAnalyzer(ABC):
    """
    Abstract base class for standardized time series analysis.
    Specialized analyzers should extend this class and implement abstract methods.
    """

    def __init__(self, df: pd.DataFrame, time_col: str, freq: str = None):
        """
        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe containing time series data.
        time_col : str
            Name of the datetime column.
        freq : str, optional
            Frequency string for resampling (e.g., 'H', 'D', 'W').
        """
        if time_col not in df.columns:
            raise ValueError(f"Time column '{time_col}' not found in dataframe")
        self.df = df.copy()
        self.time_col = time_col
        self.freq = freq
        self._prepare_index()

    def _prepare_index(self):
        """Convert time column to datetime and set as index, optionally resample."""
        self.df[self.time_col] = pd.to_datetime(self.df[self.time_col])
        self.df.set_index(self.time_col, inplace=True)
        if self.freq:
            self.df = self.df.asfreq(self.freq)

    def wrangle(self, preprocess_funcs: dict = None) -> pd.DataFrame:
        """
        Apply basic preprocessing functions to columns before analysis.

        Parameters
        ----------
        preprocess_funcs : dict, optional
            Mapping of column names to transformation functions.

        Returns
        -------
        pd.DataFrame
            Preprocessed dataframe.
        """
        df = self.df.copy()
        if preprocess_funcs:
            for col, func in preprocess_funcs.items():
                if col in df:
                    df[col] = df[col].apply(func)
                else:
                    raise KeyError(f"Column '{col}' not found for preprocessing")
        return df

    @abstractmethod
    def analyze(self):
        """
        Perform the full analysis workflow.
        Must be implemented by subclasses.
        """
        pass

    def summary(self) -> dict:
        """
        Return a high-level summary of the analyzed data (e.g., stationarity test results).
        Subclasses can override to provide custom summaries.
        """
        return {}
