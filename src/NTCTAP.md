
# 🔍 Augmento.ai Strategy Overview

Augmento.ai leverages a **topic-based sentiment analysis model** that dissects online conversations from **Twitter, Bitcointalk, and Reddit**. These discussions are categorized into specific **sentiment-driven topics**, which help identify behavioral trends in the crypto community.

## 🧠 Sentiment Topics

<img src="Assets/augmento_topics.png" alt="Augmento Sentiment Topics" width="600" />

## ⚙️ How It Works

1. **Social Sentiment Monitoring**  
   Scrapes and analyzes data from Reddit, Twitter, Bitcointalk, etc., to detect Bitcoin-related discussions.

2. **Topic Detection**  
   Each message is classified into one or more of **90+ fine-grained topics** (e.g., *Bullish*, *Hodling*, *Hacks*, *FUD_theme*).

3. **Real-Time Trend Analysis**  
   Tracks frequency and trends of topics over time, detecting correlation with market behavior.

4. **Market Signals**  
   Patterns in certain topics (e.g., *FOMO*, *Buying*, *Bullish*) may act as early indicators of market moves.

---

# 🪐 Development Strategy

A breakdown of the project structure with associated components:

| ✅ | Class / Module | Purpose |
|----|----------------|---------|
| ✅ | `NTCTapAugmentoClient` | Builds and structures raw data from Augmento |
| ✅ | `NTCTapDataWrangler` | Aggregates and formats larger datasets |
| ✅ | `NTCTapDataMetaModel` | Analyzes and extracts Dataset related Meta Information about included features |
| ⏳ | `NTCTapVisualizer` | Generates visuals for time series analysis |
| ⏳ | `NTCTapExperimentModeller` | Builds and evaluates models on the dataset |
| ⏳ | `NTCTapPreprocessor` | Prepares data for time series classification |
| ⏳ | `NTCTapModelInterpretor` | Implements strategies for model interpretability |
| ⏳ | `NTCTapStreamlitApp` | Web interface to present insights and visualizations |

---

# 📈🧠 Time Series Analysis Summary

**Multivariate time series** data (e.g., market prices, sentiment signals) often feature high dimensionality and temporal dependencies. This analysis uncovers patterns like **autocorrelation**, **seasonality**, and **trends** that may inform predictive modeling.

## 🎯 Goal  
Explore the underlying structure and behavior of the time series data to enable effective **feature engineering** for classifiers and other experiments.

## 📥 Input  
- Engineered sentiment features  
- Bitcoin market data  
- Combined sentiment-market features  

---

## 📋 Analysis Steps

### 0. 🧹 Data Wrangling  
Enhance `DataWrangling` class to prepare structured time series datasets.

---

### 1. 📊 Feature Behavior Over Time  
- Line charts & moving averages  
- Class-wise trend visualization  
- Candlestick charts, box plots, scatterplots  
- Autocorrelation plots  

---

### 2. 📉 Stationarity & Trend Analysis  
- **Tests**: ADF, KPSS  
- **Transformations**: Differencing, decomposition  
- **Advanced**: Fourier Transform, STL

---

### 3. 🔍 Explanatory Analysis  
Understand inter-variable relationships and potential causality.

---

### 4. 🔁 Autocorrelation  
- **ACF/PACF plots** to identify seasonal/lagged dependencies  
- Inform lag-based features or model structure

---

### 5. 🧪 Time Series Feature Engineering  
Use [Featuretools – Time Series Guide](https://featuretools.alteryx.com/en/stable/guides/time_series.html)

---

### 6. 🧬 Feature Distribution Analysis

---

### 7. 🧮 PCA for Time Series  
[Read more](https://medium.com/@heyamit10/principal-component-analysis-for-time-series-99a5d5eddac9)

- Sliding Window PCA  
- Dynamic PCA (e.g., Recursive PCA, DMD)  
- Frequency-Based PCA  

> Requires: Standardization, missing value handling, and trend/seasonality removal

---

### 8. 🎯 Label Preprocessing  
- Target label creation  
- Label distribution analysis & class balance

---

### 9. 🚨 Anomaly Detection  
Explore unusual behavior patterns across time or labels

---

### 10. 📦 Time Series Dataset Creation  
- Tabular + advanced time series datasets  
- Feature types:  
  - *Statistical*: mean, std, skew, kurtosis  
  - *Temporal*: lag features, rolling windows  
  - *Frequency*: FFT, wavelets  
  - *Shape*: slopes, peaks, AUC  
  - *Domain-specific*: custom patterns

---

### 11. 🧾 Baseline Statistical Dataset  
Generate basic benchmark datasets for initial model training.

---

## 📁 Output  
A suite of structured datasets:
- Raw to processed
- Stationary and feature-transformed
- Categorically enriched for modeling tasks
