"""
Attempt to scrape SEC Form 4 for actual insider selling data.

Goal: Get real insider selling volume, not just lockup dates.
Would let me test the mechanism directly.

Problem: SEC EDGAR API is a pain in the ass.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path

# SEC requires User-Agent header
HEADERS = {
    'User-Agent': 'Tomasz Solis tomaszsolis@gmail.com',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.sec.gov'
}

def get_form4_filings(ticker, cik):
    """
    Get Form 4 filings for a ticker.

    Returns list of filing URLs.
    """
    # Convert ticker to CIK (Central Index Key)
    # This is already annoying - need to look up CIK first

    url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb=&owner=include&count=100'

    try:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(resp.content, 'html.parser')

        # Find filing links
        # This HTML structure is terrible, no proper API
        links = soup.find_all('a', id='documentsbutton')

        return [link['href'] for link in links]

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return []


def parse_form4(filing_url):
    """
    Parse Form 4 to extract transaction data.

    This is where I gave up.
    """
    # Form 4 is XML but super nested and inconsistent
    # Would need to:
    # 1. Parse XML
    # 2. Handle multiple transaction tables
    # 3. Distinguish sales vs purchases
    # 4. Calculate share amounts
    # 5. Match dates to stock prices

    # Total pain, would take days to get right
    pass


# Test with one ticker
# test_filings = get_form4_filings('SNOW', '0001640147')
# print(f"Found {len(test_filings)} Form 4 filings for SNOW")

# Gave up here because:
# 1. Free APIs (FMP, Alpha Vantage) don't have Form 4 data
# 2. Paid APIs (Quiver, etc.) are $200-500/month
# 3. Scraping SEC directly is possible but takes forever
# 4. Would need to build full parser for 71 IPOs

# Decision: Just use lockup dates as proxy for insider selling.
# Not perfect but good enough for this analysis.

# TODO: If this gets traction, might be worth paying for Quiver Quantitative
# They have clean insider trading data via API

print("Abandoned: Use lockup dates instead")
