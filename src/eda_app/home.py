import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ------------------------------
# Data Processing
# ------------------------------
def load_data(data_url):
    """Loads Bitcoin sentiment dataset and processes it."""
    df = pd.read_csv(data_url)
    df['date'] = pd.to_datetime(df['date'])
    return df

# ------------------------------
# Visualization Components
# ------------------------------
def create_gauge_chart(latest_sentiment):
    """Creates a gauge chart for Bitcoin sentiment."""
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_sentiment,
        title={"text": "Bitcoin Sentiment"},
        gauge={"axis": {"range": [0, 1]}}
    ))

def create_time_series_chart(df):
    """Creates a time series chart for Bitcoin price and sentiment sources."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['btc_price'], mode='lines', name='XBTUSD', line=dict(color='white')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['bitcointalk'], mode='lines', name='Bitcointalk', line=dict(color='yellow')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['reddit'], mode='lines', name='Reddit', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['twitter'], mode='lines', name='Twitter', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['sentiment_score'], mode='lines', name='Sentiment Score', line=dict(color='orange')))
    
    fig.update_layout(
        plot_bgcolor='black', paper_bgcolor='black',
        font_color='white',
        title_text='Bitcoin Sentiment vs. Price',
        xaxis_title='Date', yaxis_title='Sources'
    )
    return fig

# ------------------------------
# Streamlit App Layout
# ------------------------------
def main():
    """Main function to render the Streamlit dashboard."""
    st.title("Bitcoin Sentiment Dashboard")
    
    data_url = "https://www.augmento.ai/bitcoin-sentiment/"
    df = load_data(data_url)
    
    latest_sentiment = df.iloc[-1]['sentiment_score']
    gauge_chart = create_gauge_chart(latest_sentiment)
    time_series_chart = create_time_series_chart(df)
    
    st.plotly_chart(gauge_chart)
    st.plotly_chart(time_series_chart)

if __name__ == '__main__':
    main()
