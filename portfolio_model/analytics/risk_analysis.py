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

def calculate_sortino_ratio(portfolio_df, risk_free_rate=0.02, periods_per_year=252):
    start_date = portfolio_df['date'].min() + dt.timedelta(days=1)
    end_date = portfolio_df['date'].max()

    # get the relative daily return
    portfolio_returns = portfolio_df.loc[
        (portfolio_df['date'] >= start_date) & (portfolio_df['date'] <= end_date), ['date', 'relative_daily_return']]

    # compute the daily risk-free rate
    daily_risk_free_rate = risk_free_rate / periods_per_year

    # calculate daily excess returns
    excess_returns = portfolio_returns['relative_daily_return'] - daily_risk_free_rate

    mean_excess_return = excess_returns.mean()

    downside_diff = np.minimum(excess_returns, 0)
    downside_volatility = np.sqrt(np.mean(downside_diff**2))

    daily_sortino = mean_excess_return / downside_volatility

    sortino_ratio = daily_sortino * np.sqrt(periods_per_year)

    return sortino_ratio

def calculate_max_drawdown(portfolio_df):
    cumulative_returns = 1 + portfolio_df['relative_cumulative_return']

    running_max = cumulative_returns.expanding().max()

    drawdown = (cumulative_returns - running_max) / running_max

    max_drawdown = drawdown.min()

    max_dd_date = drawdown.idxmin()

    peak_value = running_max.loc[max_dd_date]
    peak_date = cumulative_returns[:max_dd_date].idxmax()

    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown * 100,
        'peak_date': portfolio_df.loc[peak_date, 'date'] if peak_date in portfolio_df.index else None,
        'trough_date': portfolio_df.loc[max_dd_date, 'date'] if max_dd_date in portfolio_df.index else None
    }

def calculate_value_at_risk(portfolio_df, risk_free_rate=0.02, periods_per_year=252):
    return 0

def calculate_conditional_value_at_risk(portfolio_df, risk_free_rate=0.02, periods_per_year=252):
    return 0