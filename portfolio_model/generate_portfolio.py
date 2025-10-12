import os
import pandas as pd
import datetime as dt

def aggregate_portfolio_investments(portfolio_investments, absolute_path):
    # Aggregate all portfolio investments into a single DataFrame
    aggregated_df = pd.DataFrame()
    for ticker, df in portfolio_investments.items():
        aggregated_df = pd.concat([aggregated_df, df], ignore_index=True)

    # Group the rows by date and calculated weighted performance over all portfolio investments
    portfolio_df = aggregated_df.groupby('date').agg(
        portfolio_value_BoP=('asset_value_BoP', 'sum'),
        portfolio_value_EoP=('asset_value_EoP', 'sum'),
        absolute_daily_return = ('absolute_daily_return', 'sum')
    ).reset_index()

    # Calculate returns (what happens when beginning of balance is zero?)
    portfolio_df['relative_daily_return'] = portfolio_df['absolute_daily_return'] / portfolio_df['portfolio_value_BoP']
    portfolio_df['relative_cumulative_return'] = (1 + portfolio_df['relative_daily_return']).cumprod() - 1

    # Reorder columns
    portfolio_df = portfolio_df[['date', 'relative_daily_return', 'relative_cumulative_return','absolute_daily_return','portfolio_value_BoP', 'portfolio_value_EoP']]
    
    # Save to CSV
    relative_path = f"/data/"
    file_path = os.path.join(absolute_path + relative_path)
    os.makedirs(file_path, exist_ok=True)
    portfolio_df.to_csv(file_path + f"portfolio.csv", index=False)
    
    return portfolio_df