# IPO Lockup Expiration Effects

This project tests whether IPO lockup expirations create abnormal stock-price
pressure in modern tech IPOs. The common story is that insider selling around Day
180 causes a predictable crash. The data here does not support that simple story.

## Readout

In a sample of 71 technology IPOs from 2018 to 2024, the estimated Day 180 effect is
small and positive: about +0.45% abnormal return. That is statistically detectable
in the baseline model, but economically small relative to daily volatility and
transaction costs.

The stronger finding is a warning about identification. Placebo dates also show
significant effects, which means the Day 180 estimate is probably picking up the IPO
lifecycle rather than a clean lockup-specific shock.

My interpretation: lockup calendars are not a reliable standalone trading signal in
this sample. The evidence is more consistent with gradual market repricing and
survivorship than with a discrete lockup crash.

## Data

- 71 technology IPOs
- IPO dates from 2018-01-01 to 2024-06-30
- 17,802 daily observations
- daily return window from IPO date to IPO + 365 days
- market adjustment against SPY
- source: Yahoo Finance via `yfinance`

The initial curated list has 87 IPOs. Sixteen drop because of delisting, acquisition,
or missing price history.

## Method

The baseline model is a two-way fixed-effects DiD:

```text
abnormal_return_it = beta * post_lockup_it
                   + company_fixed_effect_i
                   + date_fixed_effect_t
                   + error_it
```

Standard errors are clustered by company. I also run an event-study version and a
Callaway-Sant'Anna estimator as a comparison.

The modern DiD checks matter because IPOs reach Day 180 on different calendar dates.
Classic TWFE can use already-treated units as controls when treatment timing is
staggered. That is not just a technical detail; it affects how much causal language
the result can carry.

## Results

| Estimator | Effect | SE | p-value | 95% CI |
|---|---:|---:|---:|---|
| TWFE DiD | +0.45% | 0.13% | 0.0004 | [0.20%, 0.71%] |
| Event study | +0.42% | 0.19% | 0.025 | [0.05%, 0.79%] |
| Callaway-Sant'Anna | +0.43% | 0.15% | 0.003 | [0.15%, 0.72%] |

The estimates line up, but the effect is tiny: roughly one-tenth of average daily
abnormal-return volatility in this sample.

By size:

| Segment | Effect | p-value |
|---|---:|---:|
| Large IPOs | +0.63% | <0.001 |
| Medium IPOs | +0.31% | 0.042 |
| Small IPOs | +0.12% | 0.457 |

The signal is concentrated in larger, more liquid names. That is not what I would
expect if the dominant mechanism were forced insider selling pressure.

## Identification Problem

The placebo tests are the most important part of the project.

Fake lockup dates at Days 60, 90, 120, 240, 270, and 300 produce significant effects
in 3 of 6 cases. Day 180 is therefore not uniquely special.

Plausible explanations:

- IPO returns follow a lifecycle pattern over the first year
- companies that survive to Day 180 are selected on quality
- lockup information is already public and priced in before expiration
- market regime and liquidity dominate any mechanical selling pressure

Because of that, I would not call the baseline estimate a clean causal effect.

## Trading Implication

I would not trade this as a simple short-the-lockup rule. In this sample:

- the sign is opposite the old crash narrative
- the magnitude is small
- placebo dates weaken the causal story
- transaction costs and spread can exceed the estimated effect

A better next step would be to bring in actual insider-sale data from Form 4 filings,
then test whether large observed selling events move prices differently from quiet
lockup expirations.

## Run It

```bash
pip install -r requirements.txt
python run_analysis.py --quick
```

Or run the notebooks in order:

```bash
jupyter notebook notebooks/01_data_collection.ipynb
jupyter notebook notebooks/02_did_analysis.ipynb
jupyter notebook notebooks/03_robustness.ipynb
jupyter notebook notebooks/04_advanced_analysis.ipynb
```

## Repo Map

```text
ipo-lockup-did-analysis/
├── data/
├── notebooks/
├── outputs/
├── run_analysis.py
├── src/
│   ├── data_loader.py
│   ├── estimators.py
│   └── modern_did.py
└── tests/
```

## Limits

This is tech-only and covers an unusual market period: COVID, QE, rate hikes, and a
large tech drawdown. It also lacks observed insider selling volume, which is the
mechanism a lockup thesis actually needs. The safest claim is narrow: in this sample,
Day 180 does not behave like a clean, exploitable lockup-crash event.
