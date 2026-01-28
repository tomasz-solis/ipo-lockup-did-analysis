#!/usr/bin/env python3
"""
Quick CLI to run IPO lockup analysis.

Usage:
    python run_analysis.py                  # Full analysis
    python run_analysis.py --quick          # Just TWFE estimate
    python run_analysis.py --ticker SNOW    # Single IPO
"""
import argparse
from src.data_loader import IPODataLoader
from src.estimators import TWFEEstimator, EventStudyEstimator


def main():
    parser = argparse.ArgumentParser(description='Run IPO lockup DiD analysis')
    parser.add_argument('--quick', action='store_true', help='Quick TWFE only')
    parser.add_argument('--ticker', type=str, help='Analyze single ticker')
    parser.add_argument('--no-charts', action='store_true', help='Skip plotting')
    args = parser.parse_args()

    # Load data
    print("Loading data...")
    loader = IPODataLoader()

    try:
        lockup_panel = loader.load_stock_data(market_adjusted=True)
    except FileNotFoundError:
        print("ERROR: Data files not found. Run notebook 01_data_collection.ipynb first.")
        return

    panel_clean = loader.prepare_panel_data(lockup_panel)

    if args.ticker:
        panel_clean = panel_clean[panel_clean['Ticker'] == args.ticker.upper()]
        if len(panel_clean) == 0:
            print(f"ERROR: Ticker {args.ticker} not found")
            print(f"Available tickers: {', '.join(sorted(lockup_panel['Ticker'].unique()[:10]))}...")
            return

    print(f"Loaded: {len(panel_clean):,} obs, {panel_clean['Ticker'].nunique()} IPOs\n")

    # TWFE estimate
    print("Running TWFE DiD...")
    twfe = TWFEEstimator()
    twfe_result = twfe.estimate(panel_clean)

    print(f"\nMain Result:")
    print(f"  Effect:   {twfe_result.coefficient:+.4f}%")
    print(f"  Std Err:  {twfe_result.std_error:.4f}%")
    print(f"  P-value:  {twfe_result.p_value:.4f}")
    print(f"  95% CI:   [{twfe_result.ci_lower:.4f}%, {twfe_result.ci_upper:.4f}%]")

    if twfe_result.is_significant():
        direction = "increase" if twfe_result.coefficient > 0 else "decrease"
        print(f"\n✓ Statistically significant {direction}")
    else:
        print(f"\n✗ Not statistically significant")

    if args.quick:
        return

    # Event study
    print("\nRunning event study...")
    es = EventStudyEstimator()
    event_results = es.estimate(panel_clean, pre_window=30, post_window=30)
    print(f"  Estimated {len(event_results)} event-time coefficients")

    # Summary stats
    print(f"\nData summary:")
    print(f"  Mean abnormal return: {panel_clean['Abnormal_Return'].mean():.4f}%")
    print(f"  Std dev: {panel_clean['Abnormal_Return'].std():.4f}%")
    print(f"  Pre-lockup obs: {(panel_clean['Post_Lockup']==0).sum():,}")
    print(f"  Post-lockup obs: {(panel_clean['Post_Lockup']==1).sum():,}")

    print("\nDone!")


if __name__ == '__main__':
    main()
