# ts_analysis/pca_analysis.py

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import pandas as pd

def standardize_df(df):
    scaler = StandardScaler()
    return pd.DataFrame(scaler.fit_transform(df), index=df.index, columns=df.columns)

def apply_pca(df, n_components=2):
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(df)
    return pd.DataFrame(components, index=df.index, columns=[f'PC{i+1}' for i in range(n_components)]), pca.explained_variance_ratio_
