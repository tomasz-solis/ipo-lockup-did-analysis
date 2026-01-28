"""Data loading and preprocessing for IPO analysis."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


class IPODataLoader:
    """Load IPO stock price data."""

    def __init__(self, data_dir: str = "../data"):
        self.data_dir = Path(data_dir)

    def load_stock_data(self, market_adjusted: bool = True) -> pd.DataFrame:
        """Load stock data (market-adjusted or raw)."""
        filename = "stock_prices_ipo_adjusted.csv" if market_adjusted else "stock_prices_ipo.csv"
        filepath = self.data_dir / "processed" / filename

        if not filepath.exists():
            raise FileNotFoundError(
                f"Data file not found: {filepath}\n"
                "Run notebook 01_data_collection.ipynb first to download the data."
            )

        try:
            df = pd.read_csv(filepath, parse_dates=['Date', 'IPO_Date'])
        except Exception as e:
            raise RuntimeError(f"Failed to read {filepath}: {str(e)}") from e

        # Sanity check - make sure we actually loaded something
        if len(df) == 0:
            raise ValueError(f"File {filepath} is empty!")

        # print(f"DEBUG: Loaded {len(df)} rows, {df['Ticker'].nunique()} tickers")

        # Add derived variables (lockup at day 180)
        df['Post_Lockup'] = (df['Days_Since_IPO'] > 180).astype(int)
        df['Days_To_Lockup'] = df['Days_Since_IPO'] - 180

        return df

    def load_ipo_metadata(self) -> pd.DataFrame:
        """Load IPO metadata (names, dates, sectors)."""
        filepath = self.data_dir / "raw" / "tech_ipos_curated.csv"

        if not filepath.exists():
            raise FileNotFoundError(f"IPO metadata not found: {filepath}")

        df = pd.read_csv(filepath, parse_dates=['IPO_Date', 'Lockup_Expiration'])
        return df

    def prepare_panel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and sort for panel regression."""
        # Drop missing returns (only ~1% of obs)
        df_clean = df.dropna(subset=['Abnormal_Return']).copy()
        # Make sure panel is sorted before regression (typo: "befoe")
        df_clean = df_clean.sort_values(['Ticker', 'Date'])
        # TODO: Add option to winsorize extreme returns (>50% daily moves)
        return df_clean

    def get_company_characteristics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract company characteristics (size, volatility)."""
        # Use first week as proxy for IPO characteristics
        # Tried using first day only but way too noisy (crazy vol)
        # TODO: Could use market cap from IPO prospectus if available (need to scrape)
        # TODO: Add sector info to characteristics
        # FIXME: This market cap proxy is kinda janky (price * volume != real market cap)
        first_week = df[df['Days_Since_IPO'].between(1, 7)].copy()

        if len(first_week) == 0:
            raise ValueError("No data in first week after IPO - can't compute characteristics")

        char = first_week.groupby('Ticker').agg({
            'Close': 'mean',
            'Volume': 'mean',
            'Abnormal_Return': 'std'
        }).reset_index()

        # print(f"DEBUG: Computed characteristics for {len(char)} companies")

        char.columns = ['Ticker', 'Avg_Price', 'Avg_Volume', 'Early_Volatility']
        # Not real market cap but good enough proxy for sorting by size
        char['Market_Cap_Proxy'] = char['Avg_Price'] * char['Avg_Volume']

        # Size categories (terciles)
        char['Size_Category'] = pd.qcut(
            char['Market_Cap_Proxy'],
            q=3,
            labels=['Small', 'Medium', 'Large']
        )

        return char
