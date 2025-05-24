import streamlit as st
import pandas as pd
from app.screener import fetch_stock_data, get_relative_strength, get_ema, get_tickers, get_52WH, get_fundamentals
import yfinance as yf
from curl_cffi import requests
session = requests.Session(impersonate="chrome")

st.title("SmartScreener - Minervini Style")

index_ticker = "^NSEI"  # Nifty 50 Index
rs_period = 100  # Relative Strength period

# Fetch index data and calculate index return
index = yf.Ticker(index_ticker,session=session)
index_data = fetch_stock_data(index)
index_return = index_data['Close'].iloc[-1] / index_data['Close'].iloc[-rs_period]

#Get tickers from predefined list
tickers = get_tickers()

print("refreshing data...")
print("Tickers fetched:", len(tickers))

results = []
for stock_ticker in tickers:
    result_dict = {}
    stock_ticker = stock_ticker.strip().upper()
    ticker = yf.Ticker(stock_ticker,session=session)
    df = fetch_stock_data(ticker)
    if not df.empty:

        # Calculate Relative Strength
        rs = get_relative_strength(df, index_return, rs_period, stock_ticker)
        result_dict['Ticker'] = stock_ticker
        result_dict['RS'] = rs
        result_dict['Close'] = df['Close'].iloc[-1]

        # Calculate EMA 50
        ema_50, ema_50_before = get_ema(df, 50, stock_ticker)

        # Calculate EMA 200
        ema_200, ema_200_before = get_ema(df, 200, stock_ticker)

        # Get 52W HIGH Close
        df = get_52WH(df)
        if df['Close'].iloc[-1] == df['high_52W'].iloc[-1]:
            result_dict['New High'] = "Y"
        
        if rs > 0 and ema_50 > ema_200 and ema_200 > ema_200_before:
            results.append(result_dict)

st.subheader("Stocks Passing Minervini Filters")
st.write(pd.DataFrame(results))