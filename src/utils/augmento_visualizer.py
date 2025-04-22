from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import plotly.graph_objects as go, plotly.express as px

class AugmentoVisualizer:
    def __init__(self, df, time_col='datetime'):
        self.df = df.copy()
        self.df[time_col] = pd.to_datetime(self.df[time_col])
        self.df.set_index(time_col, inplace=True)

    def plot_time_series(self, cols, freq='D'):
        """Line charts for given cols; can resample by freq."""
        resampled = self.df[cols].resample(freq).mean()
        return px.line(resampled, title=f"{cols} over time ({freq})")

    def plot_rolling(self, col, window=24):
        """Rolling mean & std."""
        series = self.df[col]
        roll_mean = series.rolling(window).mean()
        roll_std  = series.rolling(window).std()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=series.index, y=series, name=col))
        fig.add_trace(go.Scatter(x=roll_mean.index, y=roll_mean, name=f"{window}‐pt mean"))
        fig.add_trace(go.Scatter(x=roll_std.index, y=roll_std, name=f"{window}‐pt std"))
        fig.update_layout(title=f"Rolling stats for {col}")
        return fig

    def plot_candlestick(self, price_df):
        """Assumes columns ['open','high','low','close']"""
        return go.Figure(data=[go.Candlestick(
            x=price_df.index,
            open=price_df['open'],
            high=price_df['high'],
            low=price_df['low'],
            close=price_df['close']
        )])

    def plot_box(self, cols):
        df = self.df[cols].reset_index().melt(id_vars='datetime')
        return px.box(df, x='variable', y='value', title="Boxplots")

    def plot_scatter(self, x_col, y_col):
        return px.scatter(self.df, x=x_col, y=y_col, trendline='ols')

    def plot_acf_pacf(self, col, lags=40):
        fig_acf = plot_acf(self.df[col].dropna(), lags=lags)
        fig_pacf = plot_pacf(self.df[col].dropna(), lags=lags)
        return fig_acf, fig_pacf

    def decompose(self, col, model='additive', period=None):
        sd = seasonal_decompose(self.df[col].dropna(), model=model, period=period)
        return sd.trend, sd.seasonal, sd.resid
