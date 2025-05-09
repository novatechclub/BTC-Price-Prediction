# ts_analysis/decomposition.py

from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

def decompose_series(series, model='additive', freq=None):
    result = seasonal_decompose(series.dropna(), model=model, period=freq)
    result.plot()
    plt.show()
    return result
