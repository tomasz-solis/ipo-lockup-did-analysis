# Quick Start

Run the analysis in 5 minutes.

## TL;DR

**Finding**: IPO lockup expirations → +0.45% price increase (p<0.001), not the -1% to -3% crash from old studies.

**Problem**: Placebo tests fail. Effect probably reflects IPO lifecycle, not lockup causality.

**Implication**: Don't trade around lockup dates. Markets price this in months ahead.

---

## Setup

```bash
git clone <repo-url>
cd ipo-lockup-did-analysis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Requirements**: Python 3.10+, pandas, numpy, scipy, statsmodels, linearmodels, plotly, yfinance

---

## Run Analysis (Three Ways)

### 1. CLI Tool (Fastest)

```bash
# Full analysis
python run_analysis.py

# Quick TWFE only (5 seconds)
python run_analysis.py --quick

# Single IPO
python run_analysis.py --ticker SNOW
```

**Output**:
```
Loading data...
Loaded: 17,802 obs, 71 IPOs

Running TWFE DiD...

Main Result:
  Effect:   +0.4545%
  Std Err:  0.1289%
  P-value:  0.0004
  95% CI:   [0.2019%, 0.7072%]

✓ Statistically significant increase
```

### 2. Python One-liner

```bash
python -c "from src.data_loader import IPODataLoader; from src.estimators import TWFEEstimator; r = TWFEEstimator().estimate(IPODataLoader().load_stock_data()); print(f'Effect: {r.coefficient:.4f}%, p={r.p_value:.4f}')"
```

### 3. Python API (Recommended)

```python
from src.data_loader import IPODataLoader
from src.estimators import TWFEEstimator, EventStudyEstimator
from src.modern_did import GoodmanBacon

# Load data
loader = IPODataLoader()
df = loader.load_stock_data(market_adjusted=True)
df_clean = loader.prepare_panel_data(df)

print(f"{len(df_clean):,} observations, {df_clean['Ticker'].nunique()} IPOs")

# TWFE DiD
twfe = TWFEEstimator()
result = twfe.estimate(df_clean)

print(f"\nTWFE Estimate: {result.coefficient:.4f}%")
print(f"Std Error: {result.std_error:.4f}%")
print(f"P-value: {result.p_value:.4f}")
print(f"Significant: {result.is_significant()}")

# Event study
es = EventStudyEstimator()
event_results = es.estimate(df_clean, pre_window=30, post_window=30)
print(f"\nEvent study: {len(event_results)} time periods")

# Goodman-Bacon decomposition
df_clean['Treatment_Time'] = df_clean.groupby('Ticker')['Days_Since_IPO'].transform(
    lambda x: (x > 180).idxmax() if (x > 180).any() else np.inf
)
gb = GoodmanBacon(df_clean, 'Abnormal_Return', 'Ticker', 'Days_Since_IPO', 'Treatment_Time')
decomp = gb.decompose()
print(f"\nGoodman-Bacon: {len(decomp)} 2x2 comparisons")
```

### 4. Jupyter Notebooks (Most Detail)

```bash
jupyter notebook
```

Run in order:
1. **01_data_collection.ipynb** - Data loading, market adjustment, descriptive stats
2. **02_did_analysis.ipynb** - Main TWFE results, event study, parallel trends
3. **03_robustness.ipynb** - Alternative windows, heterogeneity, placebo tests
4. **04_advanced_analysis.ipynb** - Goodman-Bacon decomposition, modern methods

---

## Quick Results Summary

Without running anything:

| Finding | Value | Interpretation |
|---------|-------|----------------|
| **Main Effect** | +0.45% (p<0.001) | Contradicts "lockup crash" narrative |
| **Economic Sig** | 10% of daily vol | Essentially noise for trading |
| **Large IPOs** | +0.63% (p<0.001) | Liquid names show stronger effect |
| **Small IPOs** | +0.12% (n.s.) | Too illiquid to detect |
| **Placebo Tests** | 50% significant | **Identification problem** |

**Bottom line**: Effect exists but probably not causal. Markets efficient. Don't trade around lockups.

---

## Common Issues

### Data Not Loading

If you see "Data file not found", you probably skipped running notebook 01. Data collection takes ~10min to download everything from yfinance, grab coffee while it runs.

**Pro tip**: Use the CLI tool first (`python run_analysis.py --quick`) to make sure everything works before diving into notebooks.

### Import Errors

If running from `notebooks/` directory and getting import errors:
```python
import sys
sys.path.append('..')
```

Or set PYTHONPATH (more permanent):
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/ipo-lockup-did-analysis"
```

### Plotly Not Rendering in Jupyter

This happens sometimes, especially on older Jupyter versions:
```bash
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension
```

If still not working, try restarting Jupyter kernel.

### Module Reload (if editing source code)

When you edit files in `src/` while Jupyter is running:
```python
import importlib
import src.estimators
importlib.reload(src.estimators)
```

### Notebook Cells Taking Forever

Some cells (especially TWFE with time FE) can take 30-60 seconds. That's normal - linearmodels is slow with large panel datasets. Be patient or use `--quick` flag with CLI tool.

---

## Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Single test
pytest tests/test_estimators.py::test_twfe_estimator_runs -v
```

---

## Project Structure

```
ipo-lockup-did-analysis/
├── src/                # Reusable Python modules
│   ├── data_loader.py  # Data loading + preprocessing
│   ├── estimators.py   # TWFE DiD, event study
│   └── modern_did.py   # Goodman-Bacon, Callaway-Sant'Anna
├── notebooks/          # Analysis notebooks (run 01 → 04)
├── tests/              # Unit tests
├── data/               # Raw + processed data
└── outputs/            # Figures + results
```

---

## Next Steps

1. **Read [README.md](README.md)** for full methodology and findings
2. **Run notebooks** (01 → 04) for detailed analysis and visualizations
3. **Check `notebooks/scratch/`** to see failed experiments (volume weighting, sector analysis, etc.)
4. **Look at tests** to understand how estimators work
5. **Extend analysis** (if you're interested):
   - Add non-tech IPOs (would need to manually curate more data - tedious)
   - Scrape SEC Form 4 for actual insider selling (tried this, gave up - see scratch/)
   - Test if effect varies by VC backing
   - Build dashboard for upcoming lockups

---

## Key Takeaways

### For Traders
- Don't trade lockup expirations - effect is tiny (0.45%) and opposite direction from what you'd expect
- Already priced in by the time lockup expires

### For Analysts
- Good example of modern DiD methods in practice (Goodman-Bacon, Callaway-Sant'Anna)
- Shows why placebo tests matter - they partially failed here, which is a red flag
- Be honest about limitations: "effect exists but identification is questionable"

### For Portfolio Managers
- Lockup calendars aren't alpha
- Survivorship effect probably dominates (making it to Day 180 = you didn't implode)
- Focus on fundamentals, not calendar games

---

## Contact

**Questions?** See [README.md](README.md) or reach out via [LinkedIn](https://www.linkedin.com/in/tomaszsolis/).
