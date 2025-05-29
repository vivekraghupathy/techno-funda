import streamlit as st
import pandas as pd
from app.screener import get_relative_strength, get_ema,  get_52WH
from app.utils import get_stock_data, read_config, write_config, get_tickers

import time

import json
from datetime import date

from curl_cffi import requests
session = requests.Session(impersonate="chrome")

def screen_stocks():
    """
    Screen stocks based on Minervini's criteria.    
    Fetches stock data, calculates relative strength, EMA, and checks for 52-week highs.
    Returns:
        pd.DataFrame: DataFrame containing stocks that pass the screening criteria.
    """
    #Get tickers from predefined list
    tickers = get_tickers()

    print("refreshing data...")
    print("Tickers fetched:", len(tickers))

    results = []
    for stock_ticker in tickers:
        result_dict = {}
        stock_ticker = stock_ticker.strip().upper()
        try:
            df = get_stock_data(stock_ticker, session=session)
        except Exception as e:
            print(f"Error fetching data for {stock_ticker}: {e}")
            time.sleep(10)
            try:
                df = get_stock_data(stock_ticker, session=session)
            except Exception as e:
                print(f"Error fetching data for {stock_ticker} after retry: {e}")
                continue
        
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
            
            tv_link = f"https://in.tradingview.com/chart/?symbol=NSE%3A{stock_ticker.split('.')[0]}"
            result_dict['52W History'] = df['52WH_FLAG'].iloc[-10:].to_list()
            result_dict['TradingView'] = tv_link

            if rs > 0 and ema_50 > ema_200 and ema_200 > ema_200_before:
                results.append(result_dict)

    return pd.DataFrame(results)


def callback():
    """
    Handle click events in the Streamlit app.
    This function is called when a row in the dataframe is selected.
    """
    selected_row = st.session_state.df_results['selection']['rows']
    with st.popover("Open popover"):
        st.markdown(df_results.iloc[selected_row].to_markdown(index=False))


# Streamlit application to screen stocks based on Minervini's criteria
st.title("SmartScreener - Minervini Style")
st.subheader("Stocks Passing Minervini Filters")

index_ticker = "^NSEI"  # Nifty 50 Index
rs_period = 100  # Relative Strength period

# Fetch index data and calculate index return
index_data = get_stock_data(index_ticker)
index_return = index_data['Close'].iloc[-1] / index_data['Close'].iloc[-rs_period]
index_date = index_data.iloc[-1]['Date'].date()

# Read the configuration file
configs = read_config()
refresh_date = configs.get('refresh_date', '2023-10-01')
year,month,day = map(int, refresh_date.split('-'))

# Read the latest index date and decide if a refresh is needed
if index_date.year == year and index_date.month == month and index_date.day == day:
    data_refresh = False
    print("Data is up to date, no refresh required.")
else:
    data_refresh = True
    print("Data needs to be refreshed.")
    configs['refresh_date'] = index_date.strftime("%Y-%m-%d")
    write_config(configs)

# Attempt to read cached results
try:
    df_results = pd.read_csv('app/data/minervini_results.csv')
except FileNotFoundError:
    print("No cached data found, refreshing data.")
    data_refresh = True
except Exception as e:
    print(f"Error reading cached data: {e}")
    data_refresh = True


if data_refresh:
    df_results = screen_stocks()
else:
    df_results = pd.read_csv('app/data/minervini_results.csv')
    print("Using cached data, no refresh required.")

df_results.to_csv('app/data/minervini_results.csv', index=False)

# Display the results in a Streamlit dataframe

event = st.dataframe(df_results, 
                     hide_index= True,
                     on_select=callback,
                     selection_mode='single-row',
                     column_config={"TradingView": st.column_config.LinkColumn("Charts",display_text="View Chart"),
                                    "52W History": st.column_config.BarChartColumn("52W History")
                                    },
                    key="df_results"
                    )
