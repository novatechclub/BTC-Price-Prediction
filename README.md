
# **Bitcoin Price Prediction using Social Sentiment Analysis**

## **Objective**


The mission of this project is to **predict Bitcoin prices** by leveraging **social sentiment analysis**. By analyzing historical Bitcoin prices alongside sentiment data from social platforms, this project aims to uncover potential correlations between public sentiment and market movements, thereby enhancing predictive accuracy. It has been inspired by existing works about [ Stock Price Predictions with LSTM Neural Networks and Twitter Sentiment](http://www.iapress.org/index.php/soic/article/view/1202) from Thormann, M.-L. et. al. (2021).

---

## **Project Outline**

1. **Data Collection**
   - BTC Price Data: Historical Bitcoin prices sourced from [Crypto Currencies Daily Prices - BTC.csv](https://www.kaggle.com/datasets/svaningelgem/crypto-currencies-daily-prices/data?select=BTC.csv).
   - Social Sentiment Data: Collected from [Augmento AI](https://www.augmento.ai/), focusing on social sentiment trends in cryptocurrency discussions.

2. **Data Analysis & Preprocessing**
   - Clean and preprocess the BTC price data.
   - Explore and understand the sentiment data, including sentiment categories and their respective trends.
   - Build an Interactive Streamlit App to interact with the data and potentially extend it by adding an Agent Assistant.

3. **Feature Engineering**
   - Combine BTC price data with sentiment data.
   - Create relevant features to enhance predictive performance.
   - Potentially use [tsfresh](https://tsfresh.readthedocs.io/en/latest/) and [Featuretools by Alteryx](https://featuretools.alteryx.com/en/stable/) to enhance and extract features.

4. **Modeling & Prediction**
   - Utilize LSTM (Long Short-Term Memory) neural networks for time series prediction.
   - Benchmark advanced architectures such as [TabPFN](https://github.com/PriorLabs/TabPFN) or other architectures such as [Time Series Transformer](https://huggingface.co/docs/transformers/model_doc/time_series_transformer).
   - Evaluate model performance using performance metrics.

5. **Visualization & Insights**
   - Visualize Bitcoin price trends over time.
   - Showcase sentiment analysis results and their potential impact on Bitcoin prices.

---

## **Visual Representation**
*Placeholder for visual image of Bitcoin price over time.*

---

## **Tech Stack**

- **Programming Language**: Python
- **Machine Learning Framework**: TensorFlow/Keras
- **Data Analysis & Visualization**: Pandas, NumPy, Matplotlib, Seaborn
- **Web Scraping & API Integration**: BeautifulSoup, Requests
- **Natural Language Processing**: NLTK, SpaCy
- **Deep Learning Models**: LSTM Neural Networks

---

## **Data Sources**

1. **BTC Price Data**
   - [Crypto Currencies Daily Prices - BTC.csv](https://www.kaggle.com/datasets/svaningelgem/crypto-currencies-daily-prices/data?select=BTC.csv)

2. **Social Sentiment Data**
   - Source: [Augmento AI](https://www.augmento.ai/)
   - **Data Download Instructions**:
     1. Visit the [Augmento website](https://www.augmento.ai/).
     2. Click on **‘Data Download’** to retrieve the dataset.
     3. The download includes BTC sentiment data and a detailed presentation on sentiment categories.

---

## **Notebook for Reference**

- **Notebook**: [Bitcoin Price Prediction using LSTM](https://www.kaggle.com/code/meetnagadia/bitcoin-price-prediction-using-lstm/notebook)
- **Video Guide**: [Watch the explanatory video](https://www.youtube.com/watch?time_continue=10&v=p-QY7JNGD60&embeds_referring_euri=https%3A%2F%2Fwww.kaggleusercontent.com%2F&source_ve_path=MjM4NTE) for additional insights into the notebook's content and approach.

---

## **AI Topic Modeling for Social Sentiment Data**

To better understand the **social sentiment dataset**, the following AI-based topic modeling diagram from Augmento highlights the **Sentiments** analyzed in the data:




*Click on the image to view it in full resolution.*

<img src="https://www.augmento.ai/wp-content/uploads/2019/06/Sentiments-and-topics-measured-by-Augmento-s-AI.jpg" alt="Sentiment Graph" width="auto"/>

---

## **Next Steps**

1. **Review GitHub Notebook in our Repository**
    - Go through the notebook covered in the online session.
    - Get comfortable with the content and identify any gaps in understanding.

2. **Download BTC Price and Sentiment Data**
    - Ensure successful retrieval of both datasets.
    - Store the data in an organized format for preprocessing.

3. **Explore & Understand Data**
    - Investigate the data structure, key features, and missing values.
    - Dive deeper into the sentiment data to understand its columns and their meaning.

---

## **Contributors**

| Name          | Role                         |
| ------------- | ----------------------------- |
| [Antonius Jonas Greiner](https://www.linkedin.com/in/antoniusjgreiner/)   | Data Scientist & Department Lead  |
| [Luc Marcel Pellinger](https://www.linkedin.com/in/luc-pellinger/) | Data Scientist & Team Lead                   |
| [Benedikt Tremmel](https://www.linkedin.com/in/benedikt-tremmel-55a119283/) | Data Scientist & Team Lead                 |
| [Ali Hamzeh](https://www.linkedin.com/in/alihamzeh/) | Data Scientist                |

---

## **References**

1. [Crypto Currencies Daily Prices - BTC.csv](https://www.kaggle.com/datasets/svaningelgem/crypto-currencies-daily-prices/data?select=BTC.csv) - Historical BTC price data.
2. [Augmento AI](https://www.augmento.ai/) - Social sentiment data for cryptocurrency.
3. [Bitcoin Price Prediction using LSTM](https://www.kaggle.com/code/meetnagadia/bitcoin-price-prediction-using-lstm/notebook) - Reference notebook for LSTM implementation.
4. [Video Guide](https://www.youtube.com/watch?time_continue=10&v=p-QY7JNGD60&embeds_referring_euri=https%3A%2F%2Fwww.kaggleusercontent.com%2F&source_ve_path=MjM4NTE) - Detailed video explanation of the notebook.

---

## **Kanban Board**

### **To Do**
- Data Collection & Preprocessing
- Feature Engineering
- Model Architecture Design

### **In Progress**
- Data Analysis & Visualization
- Model Training (LSTM)

### **Review**
- Model Performance Evaluation
- Code Review & Refactoring

### **Done**
- Project Outline & Objective Definition
- Data Source Identification

---

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
