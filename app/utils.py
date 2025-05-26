import yfinance as yf
import json
import pandas as pd
from datetime import date

def get_stock_data(stock_ticker, session=None):
    """
    Fetch stock data for a given ticker symbol using yfinance.
    Args:
        stock_ticker (str): Stock ticker symbol.
        session (yfinance.Session, optional): Custom session for yfinance requests.
    Returns:
        pd.DataFrame: DataFrame containing stock data for the last year.
    """
    ticker = yf.Ticker(stock_ticker,session=session)
    df=ticker.history(period="1y", interval="1d", auto_adjust=True).reset_index()
    print(f"Fetched data for {ticker}:")
    df.dropna(inplace=True)
    return df

def get_tickers():
    """
    Get a list of stock ticker symbols from the NIFTY50 index.
    Returns:
        list: List of stock ticker symbols.
    """
    df = pd.read_csv('app/data/NIFTY500_List.csv')
    symbol_list = df['Symbol'].apply(lambda x: x + '.NS').to_list()
    return symbol_list

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