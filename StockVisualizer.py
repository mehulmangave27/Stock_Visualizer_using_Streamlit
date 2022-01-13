import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf
import cufflinks as cf
import datetime

st.title("S&P 500 Stock Visualising App")

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price**
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
* **Copyright:** @ ET-C Batch 1 Group 3
""")

st.sidebar.header("Company Sector Inputs")

# Web Scraping the S&P 500 data
@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header=0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby("GICS Sector")

# Sidebar sector selection
sorted_sector_unique = sorted(df["GICS Sector"].unique())
selected_sector = st.sidebar.multiselect("Sector", sorted_sector_unique, sorted_sector_unique)

st.sidebar.subheader('Query parameters')
start_date = st.sidebar.date_input("Start date", datetime.date(2019, 1, 1))
end_date = st.sidebar.date_input("End date", datetime.date(2021, 1, 31))

# Getting Ticker List in Dropdown
ticker_list = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')
tickerSymbol = st.sidebar.selectbox('Stock ticker', ticker_list) # Select ticker symbol

tickerData = yf.Ticker(tickerSymbol) # Get ticker data
tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)  #get the historical prices for this ticker

# Filtering data
df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

st.header("Displaying Companies in Selected Sector")
st.write("Data Dimension: " + str(df_selected_sector.shape[0]) + " rows and " + str(df_selected_sector.shape[1]) + " columns")
st.dataframe(df_selected_sector)

# Download S&P 500 Data
def file_download(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(file_download(df_selected_sector), unsafe_allow_html=True)

data = yf.download(
    tickers=list(df_selected_sector[:10].Symbol),
    period="ytd",
    interval="1d",
    group_by="ticker",
    auto_adjust= True,
    prepost= True,
    threads = True,
    proxy= None
)

# Plotting Closing Price


if st.sidebar.button("Get Info"):
    string_logo = '<img src=%s>' % tickerData.info['logo_url']
    st.markdown(string_logo, unsafe_allow_html=True)

    string_name = tickerData.info['longName']
    st.header('**%s**' % string_name)

    string_summary = tickerData.info['longBusinessSummary']
    st.info(string_summary)

    st.header('**Ticker data**')
    st.write(tickerDf)

#if st.sidebar.button("Show Plot"):
 #   st.header("Stock Closing Prices: " + tickerSymbol)
  #  price_plot(tickerSymbol)
    
if st.sidebar.button("Bollinger Bands Graph"):
    st.header('**Bollinger Bands**')
    qf=cf.QuantFig(tickerDf,title='First Quant Figure',legend='top',name='GS')
    qf.add_bollinger_bands()
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)