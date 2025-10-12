import os

import numpy as np
import pandas as pd
import datetime as dt
import statsmodels.api as sm
import matplotlib.pyplot as plt

def calculate_sharpe_ratio(portfolio_df, risk_free_rate=0.02, periods_per_year=252):

    start_date = portfolio_df['date'].min() + dt.timedelta(days=1)
    end_date = portfolio_df['date'].max()

    # get the relative daily return
    portfolio_returns = portfolio_df.loc[(portfolio_df['date'] >= start_date) & (portfolio_df['date'] <= end_date), ['date','relative_daily_return']]

    # compute the daily risk-free rate
    daily_risk_free_rate = risk_free_rate / periods_per_year

    # calculate daily excess returns
    excess_returns = portfolio_returns['relative_daily_return'] - daily_risk_free_rate

    # find mean and standard deviation of these daily excess returns
    mean_excess_return = excess_returns.mean()
    std_excess_return  = excess_returns.std()

    # compute the daily Sharpe ratio
    daily_sharpe = mean_excess_return / std_excess_return

    # annualize the Sharpe ratio by multiplying with sqrt(252)
    sharpe_ratio = daily_sharpe * np.sqrt(periods_per_year)

    return sharpe_ratio