# ts_analysis/anomaly_detection.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def detect_anomalies_zscore(df, column, threshold=3):
    mean = df[column].mean()
    std = df[column].std()
    z_scores = (df[column] - mean) / std
    anomalies = df[np.abs(z_scores) > threshold]
    return anomalies

def detect_anomalies_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    anomalies = df[(df[column] < Q1 - 1.5 * IQR) | (df[column] > Q3 + 1.5 * IQR)]
    return anomalies

def plot_anomalies(df, column, anomalies):
    plt.figure(figsize=(12, 6))
    plt.plot(df[column], label='Data')
    plt.scatter(anomalies.index, anomalies[column], color='red', label='Anomalies')
    plt.title(f'Anomalies in {column}')
    plt.legend()
    plt.show()
