# IPO Lockup Expiration Effects: Staggered DiD Analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Summary

**Question**: Do IPO lockup expirations crash stock prices?

**Answer**: No. Analysis of 71 tech IPOs (2018-2024) finds prices *rise* +0.45% (p<0.001) when lockups expire on Day 180.

**Why it matters**: If you're timing IPO trades around lockup dates, stop. Markets price this in months ahead. The "lockup crash" narrative from 1990s studies (Field & Hanka 2001: -1.5%) doesn't hold in modern data.

**Caveat**: Placebo tests show significant effects at fake dates too, suggesting the pattern reflects general IPO lifecycle dynamics rather than discrete lockup-specific shocks. Requires deeper investigation.

---

## Key Findings

### Main Result
- **TWFE DiD**: +0.45% abnormal return (SE: 0.13%, p<0.001)
- **Economic magnitude**: 10% of daily volatility (~4.5%) - effectively noise
- **Direction**: Contradicts conventional wisdom and academic literature from 1990s

### Heterogeneity
- **Large IPOs**: +0.63% (p<0.001) - liquid names with efficient price discovery
- **Small IPOs**: +0.12% (p=0.46, n.s.) - too illiquid to detect effects
- Effect concentrated in large-cap, high-volume IPOs

### Identification Problem
- 50% of placebo lockup dates (Days 60, 90, 120, etc.) show significant effects
- Suggests estimated effect captures general IPO trajectory, not lockup-specific shock
- Alternative explanation: Survivorship (making it to Day 180 = positive signal)
- **This is an identification failure**, not a clean causal estimate

---

## So What? (Business Implications)

### For Traders
**Don't bother timing lockup expirations**. The effect is:
- Tiny (0.45% vs 4.5% daily noise)
- Already priced in
- Opposite direction from what people expect
- Smaller than typical bid-ask spread + commissions

### For Portfolio Managers
- Lockup calendars aren't a source of alpha
- IPOs reaching Day 180 are survivors (weak ones crashed or delisted already)
- Positive selection effect dominates any insider selling pressure
- Focus on fundamentals, not calendar games

### Why This Contradicts Old Studies
Academic papers from 1990s-2000s found -1% to -3% lockup effects:
- **Field & Hanka (2001)**: -1.5% on expiration day
- **Brav & Gompers (2003)**: Volume spikes but minimal price impact

**Possible explanations for +0.45% vs -1.5%**:
1. **Market efficiency improved** - Lockup dates in prospectus, easily priced in now
2. **Sample differences** - Tech IPOs 2020s vs broad 1990s sample
3. **Time period** - QE era (2018-2021) created different dynamics
4. **Survivorship** - My sample only includes IPOs that *made it* to Day 180

Still figuring out the best way to explain the placebo test failures - might just be general lifecycle effects rather than lockup-specific.

### What I'd Do Next (If I Had More Time/Data/Money)
1. Extend to all sectors - tech might be special (need healthcare, industrials, etc.)
2. Scrape SEC Form 4 for actual insider selling data (tried this, gave up - APIs are expensive)
3. Test if effect varies by VC backing (strong vs weak VCs)
4. Compare to other "scheduled" events (option expirations, earnings)
5. Time-varying analysis: Did effect change post-COVID? Post-rate-hikes?

---

## Methodology

### Identification Strategy

Standard two-way fixed effects (TWFE) difference-in-differences:

```
Y_it = β₁·Post_it + α_i + γ_t + ε_it
```

- `Y_it`: Market-adjusted return for IPO i at date t
- `Post_it`: Indicator for Days_Since_IPO > 180
- `α_i`: Company fixed effects (controls for firm quality)
- `γ_t`: Date fixed effects (controls for macro shocks - Fed, COVID, etc.)
- `β₁`: Treatment effect (what we estimate)
- Standard errors: Clustered by company (accounts for serial correlation)

### Why Modern Methods Matter

Classic TWFE can be biased in staggered settings when treatment effects are heterogeneous (Goodman-Bacon 2021). IPOs hit Day 180 at different calendar times, so I also implement:

1. **Goodman-Bacon decomposition** - Shows TWFE uses some already-treated units as controls ("forbidden comparisons")
2. **Callaway-Sant'Anna** - Avoids problematic comparisons, provides robust estimate

**Note**: C-S not fully applicable here since all IPOs eventually get treated (no never-treated control group). Results should be interpreted as descriptive/predictive rather than strictly causal.

### Parallel Trends
- **Test**: Linear pre-trend from Days -30 to -1
- **Result**: Slope = -0.011% per day (p=0.43)
- **Conclusion**: No significant pre-trend detected

But placebo tests suggest parallel trends might not hold globally across the full IPO lifecycle.

---

## Data

**Source**: Yahoo Finance (yfinance API)

**Sample**:
- 71 technology IPOs (cloud, fintech, e-commerce, SaaS)
- IPO dates: 2018-01-01 to 2024-06-30
- 17,802 daily observations
- Time window: IPO date through IPO + 365 days
- 82% of initial 87 (16 dropped due to delisting, acquisition, or missing data)

**Variables**:
```
Abnormal_Return = Stock_Return - SPY_Return
Post_Lockup = 1 if Days_Since_IPO > 180
```

Market adjustment using S&P 500 removes macro shocks (COVID crash, Fed policy, tech selloff).

**Descriptive stats**:

| Variable | Mean | SD | Min | Max |
|----------|------|-----|-----|-----|
| Abnormal Return (%) | 0.03 | 4.48 | -47.5 | 75.8 |
| Days Since IPO | 182.5 | 105.2 | 0 | 365 |
| Post-Lockup (%) | 51% | - | - | - |

---

## Results

### Baseline Estimates

| Estimator | Effect | SE | P-value | 95% CI |
|-----------|--------|-----|---------|--------|
| TWFE DiD | +0.45% | 0.13% | 0.0004 | [0.20%, 0.71%] |
| Event Study (Day 0) | +0.42% | 0.19% | 0.025 | [0.05%, 0.79%] |
| Callaway-Sant'Anna | +0.43% | 0.15% | 0.003 | [0.15%, 0.72%] |

Consistent across methods. Magnitude stable.

### By Company Size (Market Cap Proxy)

| Size | Effect | SE | P-value |
|------|--------|----|---------|
| Large | +0.63% | 0.15% | <0.001 *** |
| Medium | +0.31% | 0.15% | 0.042 ** |
| Small | +0.12% | 0.16% | 0.457 |

Effect concentrates in liquid, high-volume IPOs with efficient price discovery.

### By Market Regime

| Period | Effect | SE | P-value |
|--------|--------|----|---------|
| Bull (2018-2019) | +0.52% | 0.19% | 0.008 *** |
| COVID (2020-2021) | +0.38% | 0.16% | 0.021 ** |
| Bear (2022-2024) | +0.29% | 0.22% | 0.187 |

Weaker effects in bear markets (prices already depressed).

### Placebo Tests (PROBLEM)

Tested effects at fake lockup dates (60, 90, 120, 240, 270, 300):
- **3 out of 6** show significant effects (p<0.05)
- Day 120: +0.33% (p=0.009)
- Day 240: +0.38% (p=0.002)

**Interpretation**: Effect at Day 180 is not uniquely special. Suggests:
1. U-shaped IPO return trajectory (early pop, mid-sag, late recovery)
2. Survivorship (weak IPOs fail before Day 180)
3. Gradual information incorporation over first year

**Bottom line**: Causal interpretation is weak. More likely picking up general lifecycle pattern.

---

## Limitations

1. **Identification**: Placebo tests fail. Effect may not be causal.
2. **Mechanism unobserved**: No insider selling volume data (need SEC Form 4 scraping)
3. **Economic significance**: 0.45% < transaction costs for retail traders
4. **Sample**: Tech only. May not generalize to other sectors.
5. **Period**: 2018-2024 includes unusual market conditions (COVID, QE, rate hikes, tech bubble)
6. **Survivorship**: Only IPOs that made it to Day 180 included (biases results upward)

---

## Project Structure

```
ipo-lockup-did-analysis/
├── README.md
├── QUICKSTART.md
├── requirements.txt
├── data/
│   ├── raw/tech_ipos_curated.csv              # 87 IPO metadata
│   └── processed/stock_prices_ipo_adjusted.csv # 17,802 obs
├── src/                                       # Reusable modules
│   ├── data_loader.py
│   ├── estimators.py                          # TWFE, event study
│   └── modern_did.py                          # Goodman-Bacon, Callaway-Sant'Anna
├── tests/
│   └── test_estimators.py
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_did_analysis.ipynb                  # Main results
│   ├── 03_robustness.ipynb                    # Placebo tests, heterogeneity
│   └── 04_advanced_analysis.ipynb             # Modern DiD methods
└── outputs/
    ├── figures/
    └── results/
```

---

## Quick Start

```bash
# Setup
git clone <repo-url>
cd ipo-lockup-did-analysis
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 1: CLI (fastest)
python run_analysis.py --quick
# Output: Effect: +0.4545% (p=0.0004)

# Option 2: Python API
python -c "
from src.data_loader import IPODataLoader
from src.estimators import TWFEEstimator

loader = IPODataLoader()
lockup_panel = loader.load_stock_data()
result = TWFEEstimator().estimate(lockup_panel)
print(f'Effect: {result.coefficient:.4f}% (p={result.p_value:.4f})')
"

# Option 3: Jupyter notebooks
jupyter notebook
# Run 01 → 02 → 03 → 04 in order
```

See [QUICKSTART.md](QUICKSTART.md) for details.

### CLI Usage

```bash
python run_analysis.py                  # Full analysis
python run_analysis.py --quick          # TWFE only
python run_analysis.py --ticker SNOW    # Single IPO
```

---

## Technical Details

### Why TWFE Might Be Biased Here

In staggered DiD, TWFE implicitly uses already-treated units as controls for late-treated units. If treatment effects evolve over time (e.g., early 2020 IPO lockups different from late 2021), this creates bias.

**Goodman-Bacon decomposition** shows 50% of TWFE weight comes from "problematic" comparisons (later-treated vs earlier-treated as control).

**Modern estimators** (Callaway-Sant'Anna, Sun-Abraham) fix this by:
1. Never using already-treated units as controls
2. Estimating group-time specific ATTs
3. Aggregating with appropriate weights

**Result**: C-S gives +0.43% vs TWFE +0.45% → bias appears minimal here.

### Parallel Trends Test

Pre-treatment period (Days -30 to -1):
```python
from scipy.stats import linregress
linregress(days_to_lockup, abnormal_return)
# Slope: -0.011% per day, p=0.43 → No significant trend
```

However, visual inspection shows some noise. Combined with placebo test failures, parallel trends assumption is questionable.

### Sample Attrition

16 IPOs (18%) dropped:
- 5 delisted before Day 180
- 4 acquired before Day 180
- 7 data unavailable

**Survivorship concern**: Sample only includes IPOs that *survived* to lockup. Survivorship itself may drive the positive effect (making it to Day 180 = good news).

Can't test this without data on failed IPOs.

---

## Known Issues / Future Work

- [ ] Placebo tests partially fail (3 out of 6 fake dates show significance) - suggests identification might be weak, need to think through this more
- [ ] Sample is tech-only - would love to add healthcare, industrials, consumer goods but manual data collection takes forever
- [ ] No actual insider selling data (need to scrape SEC Form 4, which is a pain - see `notebooks/scratch/trying_to_scrape_form4.py`)
- [ ] Test coverage incomplete (~40% - see TODOs in test files)
- [ ] Some notebook cells take 30+ seconds to run (linearmodels with time FE is slow)
- [ ] Volume-weighted DiD doesn't work well (tried it, large IPOs dominate - see `notebooks/scratch/`)
- [ ] Sector heterogeneity analysis incomplete (too few IPOs per sector)

Pull requests welcome! Or just open an issue if you find bugs.

---

## References

**Modern DiD Methods**:
- Goodman-Bacon (2021). *Journal of Econometrics*, 225(2), 254-277.
- Callaway & Sant'Anna (2021). *Journal of Econometrics*, 225(2), 200-230.
- TODO: cite that Roth et al paper on pre-trends (2023 or 2024? can't remember)

**IPO Lockups**:
- Field & Hanka (2001). *Journal of Finance*, 56(2), 471-500.
- Brav & Gompers (2003). *Journal of Financial Economics*, 68(3), 413-437.

**Econometrics**:
- Angrist & Pischke (2009). *Mostly Harmless Econometrics*. Princeton.
- Cunningham (2021). *Causal Inference: The Mixtape*. Yale.

---

## Contact

**Author**: Tomasz Solis
**GitHub**: [github.com/tomasz-solis](https://github.com/tomasz-solis)
**LinkedIn**: [linkedin.com/in/tomaszsolis](https://www.linkedin.com/in/tomaszsolis/)

---

## License

MIT License
