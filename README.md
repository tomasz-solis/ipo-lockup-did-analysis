# IPO Lockup Expiration Effects  
## A Staggered Difference-in-Differences Analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Research question**  
Do IPO lockup expirations cause stock price declines?

**Method**  
Staggered Difference-in-Differences with two-way fixed effects  

---

## Project Structure
```
ipo-lockup-did-analysis/
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/                    # Original data (gitignored)
│   └── processed/              # Cleaned datasets
│       ├── tech_ipos_curated.csv
│       └── stock_prices_ipo_adjusted.csv
│
├── notebooks/
│   ├── 01_data_collection.ipynb      # IPO list + stock downloads
│   ├── 02_did_analysis.ipynb         # Main DiD analysis
│   └── 03_robustness.ipynb           # Sensitivity tests
│
└── outputs/
    ├── figures/                # Charts
    │   ├── 02_event_study.png
    │   ├── 03_treatment_effects_time_windows.png
    │   ├── 04_treatment_effects_company_size.png
    │   └── 05_placebo_tests.png
    └── results/                # Results tables
        ├── did_main_results.csv
        ├── event_study_results.csv
        └── robustness_results.csv
```

---

## Quickstart

### 1. Clone Repository
```bash
git clone <repo-url>
cd ipo-lockup-did-analysis
```

### 2. Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

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
# 3. notebooks/03_robustness.ipynb
```
---

## Data 

**Sample**  
71 tech IPOs (2018–2024)  

**Distribution by year**
- 2018: 14
- 2019: 21
- 2020: 19
- 2021: 21
- 2022–2024: 7

**Source**  
Yahoo Finance via the `yfinance` API

**Inclusion criteria**
- Technology sector (e.g. cloud, fintech, e-commerce)
- IPO date between 2018 and 2024
- Publicly traded with available daily price data
- Standard 180-day lockup period
- IPO date through IPO + 365 days

**Total observations**
- 17,802 daily price points

**Market adjustment**
- Returns computed as abnormal returns relative to the S&P 500 (SPY)

---

## Summary of findings

**Headline result:**  
Average stock prices increase by **+0.45%** (p=0.0004) following lockup expiration. This contradicts the common belief that lockups mechanically lead to price declines due to insider selling.

**Heterogeneity**
- **Large IPOs:** +0.63% (p<0.001)
- **Small IPOs:** +0.12% (p=0.46, not significant)

**Key caveat**  
Placebo tests show significant effects at several *fake* lockup dates. This suggests the estimated effect may reflect broader IPO lifecycle dynamics rather than a clean, lockup-specific causal effect.

**Interpretation**  
Lockup expirations appear to be largely anticipated and priced in. By Day 180, expected insider selling is unlikely to represent new information. Alternatively, the result may reflect survivorship: IPOs that make it to Day 180 without collapsing tend to be stronger firms.

---

## Background

IPO insiders are typically restricted from selling shares for **180 days** following the offering. The conventional narrative is straightforward: when the lockup expires, insider selling pressure enters the market and prices fall.

This project asks a narrower question:  
**Does the lockup expiration itself cause a price change, once broader market dynamics and firm-level differences are accounted for?**

---

## Methodology

### Why staggered Difference-in-Differences

**Initial approach:** Regression Discontinuity Design around Day 180.

**Issue identified:**  
The 180-day mark coincides with very different macro environments across IPOs signals:

- Snowflake (IPO Sept 2020) → lockup in March 2021 (COVID bull market)
- Rivian (IPO Nov 2021) → lockup in May 2022 (rate hikes, tech selloff)

RDD requires the cutoff to be the only meaningful discontinuity. That assumption does not hold here.

**Chosen approach:** Staggered DiD with two-way fixed effects, which allows:
- control for **time-varying macro shocks** (calendar fixed effects)
- control for **time-invariant firm quality** (company fixed effects)

### Model specification

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

### Identification logic

- Within-firm comparison: pre- vs post-lockup
- Calendar fixed effects absorb market-wide shocks
- Parallel trends validated (pre-trend test p=0.43)

### Core logic

- Compare the same IPO’s stock performance **before** lockup expiration (Days 1–180) and **after** expiration (Days 181–365)
- Control for **calendar time** using date fixed effects, absorbing macro shocks such as COVID, monetary policy shifts, and broad market movements
- Control for **time-invariant firm characteristics** using company fixed effects

### Key assumption

- **Parallel trends:** In the absence of lockup expiration, pre- and post-period returns would have followed similar trajectories

This assumption is supported by a pre-trend test (p = 0.43), indicating no statistically detectable divergence prior to expiration.

---

## Reading the outputs

The analysis is intentionally comparative. No single statistic is sufficient.

- **Expected value:** Average outcome across plausible futures
- **Downside risk:** Exposure to unfavorable outcomes when recovery is slow or costly
- **Regret:** Cost of choosing an option that underperforms the best alternative
- **Win rate:** Frequency with which an option performs best

All metrics should be interpreted together.

---

## Example decision context

The included case reflects a common situation in mature products:
- persistent issues in part of the system
- pressure to continue shipping
- limited capacity
- no safe way to experiment before committing

The analysis compares multiple realistic options, including doing nothing, each with different downside and reversibility profiles.

The case is written to be understandable without reading the code.

---

## Results

### Main specification

```
Treatment effect (β₁): +0.4545%
Standard error: 0.1289%
95% CI: [+0.20%, +0.71%]
P-value: 0.0004
```

**Statistical significance:** Yes  
**Economic magnitude:** Small (≈0.45% vs ~4.5% daily volatility)

Stock prices increase by 0.45% in the post-lockup period compared to pre-lockup, after controlling for market conditions and company characteristics.

---

### Parallel trends check

Pre-lockup trends are flat (p=0.43), supporting the DiD identifying assumption.

![Parallel Trends](outputs/figures/01_rdd_estimate_vs_true_effect.png)

- Pre-trend slope: −0.006% per day  
- P-value: 0.430  

No statistically significant pre-trend is detected in the pre-lockup window (Days −30 to −1), supporting the DiD identifying assumption.

---

### Event study

![Event Study](outputs/figures/02_event_study.png)

The event-time profile shows:
- No sharp discontinuity at Day 180
- A gradual post-period drift rather than an immediate jump

This pattern is consistent with anticipatory pricing rather than a discrete lockup shock.

---

## Robustness checks

### Alternative lockup windows

![Treatment Effects by Window](outputs/figures/03_treatment_effects_time_windows.png)

| Lockup day | Effect | P-value | Significant |
|-----------:|-------:|--------:|:-----------:|
| Day 90     | −0.23% | 0.030   | Yes |
| Day 150    | +0.33% | 0.009   | Yes |
| **Day 180** | **+0.45%** | **0.0004** | **Yes** |
| Day 210    | +0.38% | 0.002   | Yes |
| Day 270    | +0.10% | 0.445   | No |

Effects concentrate around Days 150–210 and attenuate outside that range.

---

### Company size heterogeneity

![Treatment Effects by Size](outputs/figures/04_treatment_effects_company_size.png)

| Group | Effect | P-value | Significant |
|-------|-------:|--------:|:-----------:|
| **Large IPOs** | **+0.63%** | **<0.001** | **Yes** |
| Small IPOs | +0.12% | 0.457 | No |

The estimated effect is driven by large IPOs, consistent with more efficient price discovery in liquid, analyst-covered stocks.

---

### Placebo tests

![Placebo Tests](outputs/figures/05_placebo_tests.png)

Significant effects appear at multiple fake lockup dates (Days 60, 90, 240).

**Implication**
- If lockup expiration were the sole causal driver, effects would concentrate at Day 180
- The observed pattern suggests broader IPO lifecycle dynamics rather than a clean lockup-specific shock

As a result, causal attribution should be interpreted with caution.

---

## Discussion

### What the evidence supports

- Lockup expiration is unlikely to be a negative surprise.
- Expected insider selling appears priced in well before Day 180.
- The average effect, even if real, is economically small.
- Lockup expiration is disclosed at IPO and likely priced in well before Day 180.

### What the evidence does *not* support

- A clean, isolated causal effect of lockup expiration on prices.
- A tradeable strategy based on lockup timing alone.

### Practical takeaway

Markets appear reasonably efficient with respect to lockup information. Investment decisions are better driven by fundamentals than by lockup mechanics.

---

## Strengths

- Controls for macro shocks via time fixed effects
- Controls for firm-specific heterogeneity via company fixed effects
- Uses staggered treatment timing across 71 IPOs
- Explicitly tests identifying assumptions

## Limitations

- Placebo results weaken causal interpretation
- Insider selling volume is unobserved
- Effect size is small relative to volatility and transaction costs
- Sample limited to tech IPOs, 2018–2024
- Survivorship effects: Firms that remain viable through the first six months may represent a stronger subset.

---

## References

- Cunningham, *Causal Inference: The Mixtape*
- Alves, *Causal Inference in Python*

---

## Contact

**Tomasz Solis**  
- [LinkedIn](https://www.linkedin.com/in/tomaszsolis/)  
- [GitHub](https://github.com/tomasz-solis)

---

## License

MIT License. Free to use for learning and research with attribution.

---

## Portfolio context

Part of a broader causal inference learning sequence:

1. Regression Discontinuity — Free Shipping Threshold Effects  
2. Difference-in-Differences — Marketing Campaign Impact  
3. **Staggered DiD — IPO Lockups (this project)**  
4. Synthetic Control — upcoming

**Status:** Complete  
**Last updated:** 2025-12-02