# ts_analysis/stationarity.py

from statsmodels.tsa.stattools import adfuller, kpss

def adf_test(series):
    result = adfuller(series.dropna())
    return {
        "ADF Statistic": result[0],
        "p-value": result[1],
        "Used Lag": result[2],
        "n_obs": result[3],
        "Critical Values": result[4]
    }

def kpss_test(series):
    statistic, p_value, lags, crit = kpss(series.dropna(), regression='c')
    return {
        "KPSS Statistic": statistic,
        "p-value": p_value,
        "Used Lags": lags,
        "Critical Values": crit
    }
