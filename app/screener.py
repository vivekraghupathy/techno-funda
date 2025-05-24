import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator
import json

def fetch_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetch stock data for a given ticker symbol.
    Args:
        ticker (str): Stock ticker symbol.
        period (str): Data period (default is '1y').
        interval (str): Data interval (default is '1d').
    Returns:
        pd.DataFrame: DataFrame containing stock data.  
    """
    df=ticker.history(period="1y", interval="1d", auto_adjust=True).reset_index()
    print(f"Fetched data for {ticker}:")
    df.dropna(inplace=True)
    return df

def get_relative_strength(ticker_data,index_return, rs_period,stock_ticker):
    """
    Calculate the relative strength of a stock compared to an index.
    Args:   
        ticker_data (pd.DataFrame): DataFrame containing stock data.
        index_return (float): Return of the index to compare against.
        rs_period (int): Period over which to calculate relative strength.  
    Returns:
        float: Relative strength value.
    """
    try:
        ticker_returns = ticker_data['Close'].iloc[-1]/ticker_data['Close'].iloc[rs_period]
        rs = ticker_returns / index_return
        return rs - 1
    except Exception as e:
        print(f"Error calculating relative strength for {stock_ticker}: {e}")
        return 0

def get_ema(ticker_data, period, ticker):
    """
    Calculate the Exponential Moving Average (EMA) for a given stock ticker.
    Args:
        ticker_data (pd.DataFrame): DataFrame containing stock data.
        period (int): Period for the EMA calculation.
        ticker (str): Stock ticker symbol.
    Returns:
        tuple: Last EMA value and the EMA value 21 days before.
    """
    try:
        ema = EMAIndicator(ticker_data['Close'], window=period)
        df = ema.ema_indicator()
        return df.iloc[-1], df.iloc[-21]  # Return the last EMA value
    except Exception as e:
        print(f"Error calculating EMA for {ticker}: {e}")
        return 0 , 0

def get_tickers():
    """
    Get a list of stock ticker symbols from the NIFTY50 index.
    Returns:
        list: List of stock ticker symbols.
    """
    df = pd.read_csv('app/data/NIFTY500_List.csv')
    symbol_list = df['Symbol'].apply(lambda x: x + '.NS').to_list()
    return symbol_list

def get_52WH(df):
    """
    Calculate the 52-week high for a given stock ticker.
    Args:
        df (pd.DataFrame): DataFrame containing stock data.     
    Returns:
        pd.DataFrame: DataFrame with an additional column for the 52-week high. 
    """
    df['high_52W'] = df.Close.rolling(window=200).max()
    return df

def get_fundamentals(ticker):
    """
    Fetch and calculate fundamental metrics for a given stock ticker.
    Args:
        ticker (str): Stock ticker symbol.  
    Returns:
        dict: Dictionary containing fundamental metrics.
    """
    eps_df = ticker.get_income_stmt(freq='quarterly',pretty=True).loc['Diluted EPS'].sort_index()
    revenue_df = ticker.get_income_stmt(freq='quarterly',pretty=True).loc['Total Revenue'].sort_index()
    qoq_eps_change = round((eps_df.iloc[-1]/eps_df.iloc[-2] - 1)*100,2)
    qoq_revenue_change = round((revenue_df.iloc[-1]/revenue_df.iloc[-2] - 1)*100,2)
    yoy_eps_change = round((eps_df.iloc[-1]/eps_df.iloc[-5] - 1)*100,2)
    yoy_revenue_change = round((revenue_df.iloc[-1]/revenue_df.iloc[-5] - 1)*100,2)
    results = {
        'QoQ EPS': qoq_eps_change,
        'QoQ Sales': qoq_revenue_change,
        'YoY EPS': yoy_eps_change,
        'YoY Sales': yoy_revenue_change
    }
    return results

def read_config():
    """
    Read configuration settings from a JSON file.
    Returns:
        dict: Configuration settings.
    """
    try:
        with open('app/data/config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Configuration file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from configuration file.")
        return {}

def write_config(config):
    """
    Write configuration settings to a JSON file.
    Args:
        config (dict): Configuration settings to write.
    """
    try:
        with open('app/data/config.json', 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error writing configuration file: {e}")