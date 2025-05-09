# ts_analysis/visualization.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

def plot_time_series(df, columns, title="Time Series Plot"):
    df[columns].plot(figsize=(12, 6), title=title)
    plt.xlabel("Time")
    plt.ylabel("Values")
    plt.show()

def rolling_stats(df, window=24):
    return df.rolling(window=window).mean()

def plot_autocorrelation(df, column, lags=40):
    plot_acf(df[column].dropna(), lags=lags)
    plt.show()

def plot_pacf_custom(df, column, lags=40):
    plot_pacf(df[column].dropna(), lags=lags)
    plt.show()
