# ts_analysis/feature_engineering.py

import pandas as pd
import numpy as np
from scipy.fftpack import fft
from scipy.signal import find_peaks
import featuretools as ft


def add_lag_features(df, columns, lags=[1, 2, 3]):
    for col in columns:
        for lag in lags:
            df[f'{col}_lag{lag}'] = df[col].shift(lag)
    return df

def add_fft_features(df, column, top_n=5):
    fft_vals = fft(df[column].dropna())
    fft_abs = np.abs(fft_vals)
    fft_features = pd.Series(fft_abs[:top_n], index=[f"{column}_fft_{i}" for i in range(top_n)])
    return fft_features

def add_slope_feature(df, column, window=5):
    df[f'{column}_slope'] = df[column].rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=False)
    return df

def detect_peaks(df, column, height=None, distance=None):
    peaks, _ = find_peaks(df[column].dropna(), height=height, distance=distance)
    return peaks

def auto_feature_engineering(df, time_index, max_depth=1, agg_primitives=None, trans_primitives=None):
    """
    Automatically generate features using Featuretools.
    
    Parameters:
    - df: pandas DataFrame with a time index column
    - time_index: name of the datetime column
    - max_depth: depth of features to synthesize
    
    Returns:
    - feature_matrix: Transformed DataFrame with new features
    """
    # Ensure time index is datetime
    df = df.copy()
    df[time_index] = pd.to_datetime(df[time_index])

    es = ft.EntitySet(id="time_series_data")
    es = es.add_dataframe(
        dataframe_name="data",
        dataframe=df,
        index="index",
        make_index=True,
        time_index=time_index
    )

    feature_matrix, feature_defs = ft.dfs(
        entityset=es,
        target_dataframe_name="data",
        max_depth=max_depth,
        agg_primitives=agg_primitives,
        trans_primitives=trans_primitives
    )

    return feature_matrix