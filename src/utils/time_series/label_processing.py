# ts_analysis/label_processing.py

import pandas as pd
import matplotlib.pyplot as plt

def create_binary_return_label(df, price_col, horizon=1):
    df['return'] = df[price_col].pct_change(periods=horizon).shift(-horizon)
    df['label'] = (df['return'] > 0).astype(int)
    return df

def plot_label_distribution(df, label_col='label'):
    counts = df[label_col].value_counts()
    counts.plot(kind='bar', title='Label Distribution')
    plt.xlabel('Label')
    plt.ylabel('Count')
    plt.show()
    return counts
