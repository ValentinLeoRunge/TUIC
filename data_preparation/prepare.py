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
    yesterday = (pd.Timestamp.today() - pd.Timedelta(days=1)).normalize()
    portfolio_stocks = {}

    for index, row in input_file.iterrows():
        ticker = row['ticker']
        start = row['buy_in_date']
        shares_actual = row['shares']

        df = yf.download(ticker, start = start, end = yesterday, interval ='1d', auto_adjust=True)
        if df.empty:
            print(f"No data found for {ticker}. Please check the ticker symbol or the date range.")
            continue

        # clean up the DataFrame
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        df.columns = df.columns.droplevel('Ticker')
        df.rename(columns={'Date': 'date', 'Price': 'price', 'Close': 'close', 'High': 'high', 'Low': 'low', 'Open': 'open', 'Volume': 'volume'}, inplace=True)

        # Calculate shares owned to correct for different share amounts in yfinance and input file
        shares_calculated = row['buy_in_amount'] / df.loc[0, 'close'].item()
        df['shares_calculated'] = shares_calculated
        df['shares_actual'] = shares_actual

        df = calculate_additional_metrics(df)

        # Safe portfolio stock data to portfolio_investments folder
        relative_path = f"/data/portfolio_investments/"
        file_path = os.path.join(absolute_path + relative_path)
        os.makedirs(file_path, exist_ok=True)
        df.to_csv(file_path + f"{ticker}.csv", index=False)

        portfolio_stocks[ticker] = df
    
    return portfolio_stocks

def calculate_additional_metrics(df):
    df['relative_daily_return'] = df['close'].pct_change()
    df['relative_cumulative_return'] = (1 + df['relative_daily_return']).cumprod() - 1
    df['asset_value_EoP'] = (df['shares_calculated'] * df['close']).round(2)
    df['absolute_daily_return'] = df['asset_value_EoP'].diff()
    df['asset_value_BoP'] = df['asset_value_EoP'].shift(1).fillna(0)
    

    # Reorder columns
    df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'shares_calculated', 'shares_actual', 'relative_daily_return', 'relative_cumulative_return', 'absolute_daily_return', 'asset_value_BoP', 'asset_value_EoP']]
    return df

def load_benchmarks(absolute_path, benchmarks_ticker, model_start_date):
    yesterday = (pd.Timestamp.today() - pd.Timedelta(days=1)).normalize()
    benchmarks = {}
    start_date_str = model_start_date.strftime('%Y-%m-%d')

    for ticker in benchmarks_ticker:
        df = yf.download(ticker, start=start_date_str, end=yesterday, interval='1d', auto_adjust=True)
        if df.empty:
            print(f"No data found for benchmark {ticker}. Please check the ticker symbol or the date range.")
            continue

        # clean up the DataFrame
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d', errors='coerce')
        # df.columns = df.columns.droplevel('Ticker')
        df.rename(columns={'Date': 'date', 'Price': 'price', 'Close': 'close', 'High': 'high', 'Low': 'low', 'Open': 'open', 'Volume': 'volume'}, inplace=True)

        # calculate additional metrics
        df['relative_daily_return'] = df['close'].pct_change()
        df['relative_cumulative_return'] = (1 + df['relative_daily_return']).cumprod() - 1

        df.columns = df.columns.droplevel('Ticker')

        # Safe to CSV file
        relative_path = f"/data/benchmarks/"
        file_path = os.path.join(absolute_path + relative_path)
        os.makedirs(file_path, exist_ok=True)
        df.to_csv(file_path + f"{benchmarks_ticker.get(ticker)}({ticker}).csv", index=False)

        benchmarks[ticker] = df
    
    return benchmarks
