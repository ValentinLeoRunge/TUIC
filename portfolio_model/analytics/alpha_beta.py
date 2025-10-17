import os
import pandas as pd
import datetime as dt
import statsmodels.api as sm
import matplotlib.pyplot as plt


def calculate_portfolio_alpha_beta(portfolio_df, benchmark_dict, benchmark):
    benchmark_df = benchmark_dict[benchmark]

    start_date = portfolio_df['date'].min() + dt.timedelta(days=1)
    end_date = portfolio_df['date'].max()

    portfolio_returns = portfolio_df.loc[(portfolio_df['date'] >= start_date) & (portfolio_df['date'] <= end_date), ['date','relative_daily_return']]
    benchmark_returns = benchmark_df.loc[(benchmark_df['date'] >= start_date) & (benchmark_df['date'] <= end_date), ['date','relative_daily_return']]

    merged_returns = pd.merge(
        portfolio_returns,
        benchmark_returns,
        on='date',
        suffixes=('_portfolio', '_benchmark')
    )

    # Linear OLS regression with statsmodels.api
    X = merged_returns['relative_daily_return_benchmark']
    y = merged_returns['relative_daily_return_portfolio']
    X = sm.add_constant(X)  # fügt Intercept (alpha) hinzu

    model = sm.OLS(y, X).fit()
    alpha = model.params['const']
    beta = model.params['relative_daily_return_benchmark']
    r_squared = model.rsquared

    return alpha, beta, r_squared