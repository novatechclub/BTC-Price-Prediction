from statsmodels.tsa.stattools import adfuller, kpss
import numpy as np

class AugmentoPreprocessor:
    def __init__(self, df, time_col='datetime'):
        self.df = df.copy().set_index(time_col)
    
    def stationarity_tests(self, col):
        a_res = adfuller(self.df[col].dropna())
        k_res = kpss(self.df[col].dropna(), nlags='auto')
        return {
            'adf_stat': a_res[0], 'adf_p': a_res[1],
            'kpss_stat': k_res[0], 'kpss_p': k_res[1]
        }

    def difference(self, col, periods=1):
        self.df[f"{col}_diff{periods}"] = self.df[col].diff(periods)
        return self

    def make_lag(self, col, lags=[1,24,168]):
        for l in lags:
            self.df[f"{col}_lag{l}"] = self.df[col].shift(l)
        return self

    def rolling_features(self, col, windows=[3,24,168]):
        for w in windows:
            self.df[f"{col}_roll_mean{w}"] = self.df[col].rolling(w).mean()
            self.df[f"{col}_roll_std{w}"]  = self.df[col].rolling(w).std()
        return self

    def fourier_terms(self, col, period, K=3):
        t = np.arange(len(self.df))
        for k in range(1, K+1):
            self.df[f"{col}_sin{k}"] = np.sin(2*np.pi*k*t/period)
            self.df[f"{col}_cos{k}"] = np.cos(2*np.pi*k*t/period)
        return self

    def drop_na(self):
        self.df.dropna(inplace=True)
        return self

    def get_processed(self):
        return self.df.reset_index()
