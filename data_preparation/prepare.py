import os
import pandas as pd
import yfinance as yf
import datetime as dt


def load_inputs(absolute_path):
    input_file = pd.read_excel(os.path.join(absolute_path, 'data', 'inputs.xlsx'))
    input_file['buy_in_date'] = pd.to_datetime(input_file['buy_in_date'], format='%d.%m.%Y', errors='coerce')
    return input_file

def load_portfolio_investments(absolute_path, input_file):
    # prepare dateformat for yfinance
    if input_file['buy_in_date'].isnull().any():
        print("Warning: Some dates could not be parsed. Please check the input file.")
    input_file['buy_in_date'] = input_file['buy_in_date'].dt.strftime('%Y-%m-%d')

    # Extrakt stock data from yfinance
    today = pd.Timestamp.today().normalize()
    portfolio_stocks = {}

    for index, row in input_file.iterrows():
        ticker = row['ticker']
        start = row['buy_in_date']
        shares_owned = row['shares']

        df = yf.download(ticker, start = start, end = today, interval ='1d')
        if df.empty:
            print(f"No data found for {ticker}. Please check the ticker symbol or the date range.")
            continue

        # clean up the DataFrame
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        df.columns = df.columns.droplevel('Ticker')
        df.rename(columns={'Date': 'date', 'Price': 'price', 'Close': 'close', 'High': 'high', 'Low': 'low', 'Open': 'open', 'Volume': 'volume'}, inplace=True)

        df = calculate_additional_metrics(df, shares_owned)

        # df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        
        # Safe portfolio stock data to portfolio_investments folder
        relative_path = f"/data/portfolio_investments/"
        file_path = os.path.join(absolute_path + relative_path)
        os.makedirs(file_path, exist_ok=True)
        df.to_csv(file_path + f"{ticker}.csv", index=False)

        portfolio_stocks[ticker] = df
    
    return portfolio_stocks

def calculate_additional_metrics(df, shares_owned):
    df['shares_owned'] = shares_owned
    df['daily_return'] = df['close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
    df['MSMIF_position'] = (shares_owned * df['close']).round(2)
    return df
