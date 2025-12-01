# IPO Lockup Expiration Effects: A Staggered Difference-in-Differences Analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Research Question:** Do IPO lockup expirations cause stock price declines?

**Method:** Staggered Difference-in-Differences with two-way fixed effects  
**Sample:** 71 tech IPOs (2018-2024)  
**Data:** 17,874 daily stock price observations

---

## Key Findings

> **[To be filled after analysis]**
> 
> Stock prices [increase/decrease/show no change] by X% in the post-lockup period compared to pre-lockup, controlling for market conditions and company characteristics.

---

## Background

When tech companies go public, insiders (founders, employees, venture capitalists) are typically restricted from selling their shares for **180 days**—the "lockup period." This SEC-mandated restriction prevents immediate dumping of insider shares that could destabilize the newly public stock.

**Conventional wisdom:** When lockups expire at Day 180, insider selling pressure floods the market → stock price drops.

**But markets are forward-looking.** If everyone knows the lockup expires predictably, shouldn't prices already reflect this?

This project uses causal inference methods to rigorously test whether lockup expirations actually cause stock price changes.

---

## Methodology

### Why Staggered Difference-in-Differences?

**Initial plan:** Regression Discontinuity Design (RDD) around the 180-day cutoff.

**Problem identified:** RDD requires the cutoff to be the ONLY discontinuity. However:
- Snowflake IPO (Sept 2020) → Day 180 in **March 2021** (COVID bull market peak)
- Rivian IPO (Nov 2021) → Day 180 in **May 2022** (Fed tightening, tech crash)

Different IPOs hit Day 180 at different calendar dates with drastically different macro environments. This violates RDD's continuity assumption.

**Solution:** **Staggered DiD** explicitly controls for:
- **Time-varying shocks** (COVID, Fed policy, market sentiment) via **time fixed effects**
- **Time-invariant company quality** (good vs bad IPOs) via **company fixed effects**

### Model Specification
```
Abnormal_Return_it = β₀ + β₁·Post_Lockup_it + α_i + γ_t + ε_it

Where:
- Abnormal_Return_it: Stock return for IPO i at time t, minus S&P 500 return
- Post_Lockup_it: 1 if Days_Since_IPO > 180, 0 otherwise
- α_i: Company fixed effects (71 IPOs)
- γ_t: Calendar date fixed effects (controls for macro)
- β₁: Treatment effect (what we're estimating)

Standard errors clustered at company level.
```

### Identification Strategy

**Within-company comparison:**
- Compare same IPO's performance pre-lockup (Days 1-179) vs post-lockup (Days 181-365)
- Control for calendar time (removes COVID, Fed policy, market-wide shocks)
- Assumption: Parallel trends (tested via event study)

---

## Project Structure
```
ipo-lockup-did-analysis/
├── README.md
├── requirements.txt
├── setup_structure.sh
│
├── data/
│   ├── raw/                    # Original data (gitignored)
│   └── processed/              # Cleaned datasets
│       ├── tech_ipos_curated.csv
│       ├── stock_prices_ipo.csv
│       └── stock_prices_ipo_adjusted.csv
│
├── notebooks/
│   ├── 01_data_collection.ipynb      # IPO list + stock downloads
│   ├── 02_did_analysis.ipynb         # Main DiD analysis
│   └── 03_robustness_checks.ipynb    # Sensitivity tests
│
├── src/
│   ├── __init__.py
│   ├── data_utils.py           # Data loading & preprocessing
│   ├── did_analysis.py         # DiD estimation functions
│   └── visualization.py        # Plotting utilities
│
└── outputs/
    ├── figures/                # Publication-ready charts
    │   ├── event_study.html
    │   └── treatment_timing.html
    └── results/                # Regression tables
        └── did_results.csv
```

---

## Quickstart

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/ipo-lockup-did-analysis.git
cd ipo-lockup-did-analysis
```

### 2. Install Dependencies
```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Run Analysis
```bash
# Open Jupyter
jupyter notebook

# Run notebooks in order:
# 1. notebooks/01_data_collection.ipynb
# 2. notebooks/02_did_analysis.ipynb
# 3. notebooks/03_robustness_checks.ipynb
```

---

## Data

### IPO Sample

**Source:** Manually curated from public sources (IPO Scoop, NASDAQ, SEC filings)

**Criteria:**
- Tech sector (cloud, fintech, e-commerce, social, etc.)
- IPO date: 2018-2024
- Publicly traded (stock price data available)
- 180-day standard lockup period

**Final sample:** 71 IPOs with complete data

**Distribution by year:**
- 2018: 14 IPOs
- 2019: 21 IPOs
- 2020: 19 IPOs
- 2021: 21 IPOs (COVID boom)
- 2022-2024: 7 IPOs

### Stock Price Data

**Source:** Yahoo Finance via `yfinance` API

**Window:** IPO date to IPO date + 365 days

**Observations:** 17,874 daily price points

**Market adjustment:** All returns calculated as abnormal returns vs S&P 500 (SPY)

---

## Key Results

### Main Specification

**[To be filled after analysis]**
```
Treatment Effect (β₁): X.XX%
Standard Error: X.XX%
95% CI: [X.XX%, X.XX%]
P-value: 0.XXX

Interpretation: Stock prices [increase/decrease] by X.XX% 
in the post-lockup period, on average.
```

### Event Study

**Visual evidence of treatment effect timing:**

![Event Study Plot](outputs/figures/event_study.html)

**Parallel trends:** [Pass/Fail] - Pre-lockup coefficients show [parallel/non-parallel] trends.

---

## Robustness Checks

- [ ] **Different time windows:** 30-day, 60-day, 90-day post-lockup
- [ ] **Exclude outliers:** Drop IPOs with >100% price change
- [ ] **Sector heterogeneity:** Separate effects for fintech vs cloud vs e-commerce
- [ ] **IPO quality:** Large vs small offerings
- [ ] **Time period:** Pre-COVID (2018-2019) vs COVID (2020-2021) vs post-COVID (2022-2024)

---

## Investment Implications

**[To be filled based on results]**

**If negative effect found:**
> Investors may benefit from selling IPO shares before Day 180 or waiting to buy until after lockup-induced selling pressure subsides.

**If no effect found:**
> Market efficiently prices lockup risk. Lockup expiration is a non-event for diversified investors.

**If heterogeneous effects:**
> Effect depends on [company quality / sector / market conditions]. Strategy should be conditional.

---

## Methodological Notes

### Advantages of Staggered DiD

1. **Controls for macro shocks:** Time fixed effects absorb COVID, Fed policy, market sentiment
2. **Controls for selection:** Company fixed effects remove time-invariant quality differences
3. **Uses all data:** Leverages treatment timing variation (generalizable across time periods)
4. **Testable assumptions:** Parallel trends can be visually and statistically tested

### Limitations

1. **Lockup variation:** Analysis assumes 180-day lockup for all (some have 90 or 365 days—excluded)
2. **Insider selling data:** We observe price effects, not actual selling volume
3. **Anticipation effects:** Markets may price in lockup before Day 180 (addressed via event study)
4. **External validity:** Results apply to tech IPOs 2018-2024; may not generalize to other sectors/periods

---

## References

**Primary learning resources:**
- *Causal Inference: The Mixtape* by Scott Cunningham (main textbook)
- *Causal Inference in Python* by Matheus Facure Alves

### IPO Lockup Research

- Field, L. C., & Hanka, G. (2001). The Expiration of IPO Share Lockups. *The Journal of Finance*.
- Bradley, D. J., et al. (2001). The Quiet Period Goes Out with a Bang. *The Journal of Finance*.

---

## Contributing

This is a personal learning project, but feedback is welcome!

**Found an issue?**
- Open a GitHub issue
- Suggest improvements via pull request

**Want to extend the analysis?**
- Try alternative DiD estimators (Callaway-Sant'Anna, Sun-Abraham)
- Add trading volume as outcome
- Analyze other sectors (biotech, cleantech)

---

## Contact

**Tomasz Solis**
- Email: tomasz.solis@gmail.com
- LinkedIn: [linkedin.com/in/tomaszsolis](https://www.linkedin.com/in/tomaszsolis/)
- GitHub: [github.com/tomasz-solis](https://github.com/tomasz-solis)

---

## License

MIT License - feel free to use for learning/research with attribution.

---

## Portfolio Context

This project is part of my causal inference learning journey:

1. **RDD Analysis** - [Free Shipping Threshold Effects](https://github.com/tomasz-solis/rdd-free-shipping)
2. **Simple DiD** - [Marketing Campaign Impact](https://github.com/tomasz-solis/marketing-campaign-causal-impact)
3. **Staggered DiD** - *This project* (IPO Lockups)
4. **SCM** - Upcoming (searching for appropriate single-unit treatment)

**Learning progression:** Simple methods → Complex applications → Methodological adaptation

**Key skill demonstrated:** Recognizing when a method doesn't fit and pivoting appropriately (originally planned RDD, identified violations, switched to DiD).

---

**Last Updated:** 2025-12-01
**Status:** Analysis in Progress 🚧