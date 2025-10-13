# streamlit_app.py
# TUIC Portfolio Model - Structure Skeleton (placeholders only)
# Run with: streamlit run streamlit_app.py
from os import write

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

class TUICPortfolioApp:
    def __init__(self, portfolio_df=None, sharpe_ratio=None, max_dd_info=None, alpha_beta_table=None):
        self.title = "TUIC Portfolio Model"
        self.portfolio_df = portfolio_df
        self.sharpe_ratio = sharpe_ratio
        self.max_dd_info = max_dd_info
        self.alpha_beta_table = alpha_beta_table
        self.placeholder_table = pd.DataFrame({
            "Ticker": ["AAA", "BBB", "CCC"],
            "Shares": [10, 20, 30],
            "Weight": [0.2, 0.3, 0.5]
        })
    
    def _draw_circle(self):
        fig, ax = plt.subplots()
        c = Circle((0.5, 0.5), 0.45, fill=True)
        ax.add_patch(c)
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return fig

    def _draw_line_icon(self):
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 6)
        y = np.array([3, 4, 2.5, 5, 4.2, 6])
        ax.plot(x, y)
        ax.axhline(y.min()-1)
        ax.axis('off')
        return fig

    def header(self):
        st.set_page_config(page_title=self.title, layout="wide")
        st.title(self.title)
        st.write(" ")

    def portfolio_card(self, title_text="Portfolio Info: Stock tickers, shares in portfolio ..."):
        left, spacer, right = st.columns([2, 1, 5])
        with left:
            st.pyplot(self._draw_circle())
            st.write(" ")
        with right:
            st.pyplot(self._draw_line_icon())
            st.subheader(title_text)
            with st.expander("Show placeholder portfolio table"):
                st.dataframe(self.placeholder_table, use_container_width=True)

    def risk_factors(self):
        st.markdown("### Risk Factors")
        if self.sharpe_ratio:
            st.metric("Sharpe Ratio (ann.)", f"{self.sharpe_ratio:.2f}")
        if self.alpha_beta_table:
            df = pd.DataFrame(self.alpha_beta_table)
            st.dataframe(df, use_container_width=True)

    def risk_factors2(self):
        st.markdown("**Risk factors: sharpe ratios, information ratios, volatilities ...**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sharpe (ann.)", "1.23")
        with col2:
            st.metric("Info Ratio", "0.67")
        with col3:
            st.metric("Vol (ann.)", "12.3%")
        st.write(" ")

    def simulation(self):
        st.markdown("**Smilutaion of the portfolio: input of money and new stocks**")  # keep user's label
        amount = st.number_input("Amount to invest (placeholder)", min_value=0, value=1000, step=100)
        tickers = st.text_input("New tickers (comma-separated, placeholder)", value="DDD, EEE")
        st.button("Run Simulation (placeholder)")
        st.caption("Simulation outputs would be displayed here (charts / tables).")

    def stress_testing(self):
        st.markdown("**Stress testing: input field**")
        scenario = st.text_area("Define stress scenario (placeholder)",
                                value="e.g., -10% equity shock; +100 bps rates; +50 bps credit spreads")
        st.button("Apply Stress (placeholder)")
        st.caption("Stressed P&L / drawdown tables and charts would appear here.")

    def risk_measures(self):
        st.markdown("**VaR, CVaR**")
        cols = st.columns(2)
        with cols[0]:
            st.metric("VaR (95%, 1d)", "−2.5%")
        with cols[1]:
            st.metric("CVaR (95%, 1d)", "−3.8%")
        st.pyplot(self._draw_line_icon())

    def second_row_portfolio_card(self, title_text="Portfolio Info: Stock tickers, shares in portfolio ..."):
        left, spacer, right = st.columns([2, 1, 5])
        with left:
            st.pyplot(self._draw_circle())
            st.write(" ")
        with right:
            st.pyplot(self._draw_line_icon())
            st.subheader(title_text)
            st.caption("Additional portfolio block (placeholder)")        

    def run(self):
        self.header()

        # First section
        self.portfolio_card()
        self.risk_factors()
        self.simulation()

        # Second section
        self.second_row_portfolio_card()
        self.stress_testing()
        self.risk_measures()


if __name__ == "__main__":
    import os
    import pandas as pd
    import numpy as np
    import yfinance as yf
    from datetime import datetime, timedelta

    from data_preparation import prepare
    from portfolio_model import generate_portfolio
    from portfolio_model.analytics import alpha_beta
    from scipy.stats import linregress

    from portfolio_model.analytics import risk_analysis
    from streamlit_app import TUICPortfolioApp

    absolute_path = os.getcwd()

    # --- Load & process data ---
    input_file = prepare.load_inputs(absolute_path)
    portfolio_investments_dict = prepare.load_portfolio_investments(absolute_path, input_file)

    model_start_date = datetime(1990, 1, 1)
    benchmarks_ticker = {
        'IEUS': 'MSCI_Europe_Small_Cap',
        'EUMD.L': 'MSCI_Europe_Mid_Cap',
        'IWVL.L': 'MSCI_World_Value_Factor',
        'EXW1.DE': 'Eurostoxx_50',
        'EXSA.DE': 'Eurostoxx_600',
        'SWDA.L': 'MSCI_World',
        'FEZ': 'Eurostoxx_50',
        'IEUR': 'Eurostoxx_600',
        'URTH': 'MSCI_World'
    }

    benchmarks_dict = prepare.load_benchmarks(absolute_path, benchmarks_ticker, model_start_date)
    portfolio_df = generate_portfolio.aggregate_portfolio_investments(portfolio_investments_dict, absolute_path)

    # --- Calculate metrics ---
    results = []
    for ticker, benchmark_name in benchmarks_ticker.items():
        alpha, beta = alpha_beta.calculate_portfolio_alpha_beta(portfolio_df, benchmarks_dict, ticker)
        annualized_alpha = (1 + alpha) ** 252 - 1
        results.append({"Benchmark": benchmark_name, "Alpha (ann.)": annualized_alpha, "Beta": beta})

    sharpe_ratio = risk_analysis.calculate_sharpe_ratio(portfolio_df, 0.02, 252)
    max_dd_info = risk_analysis.calculate_max_drawdown(portfolio_df)

    # --- Launch the Streamlit app ---
    app = TUICPortfolioApp(
        portfolio_df=portfolio_df,
        sharpe_ratio=sharpe_ratio,
        max_dd_info=max_dd_info,
        alpha_beta_table=results
    )
    app.run()
