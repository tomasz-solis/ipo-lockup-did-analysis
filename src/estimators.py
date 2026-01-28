"""
DiD estimators for IPO lockup analysis.

NOTE: Initially tried WLS with volume weights but it overweighted large IPOs
and made results worse. Sticking with unweighted + clustered SEs.

# Also tried:
# - Fixed effects with Fama-MacBeth SEs - too conservative
# - Quantile regression for robustness - didn't help much
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from linearmodels.panel import PanelOLS
from dataclasses import dataclass
import warnings


@dataclass
class DiDResult:
    """Container for DiD estimation results."""
    coefficient: float
    std_error: float
    t_stat: float
    p_value: float
    ci_lower: float
    ci_upper: float
    n_obs: int
    n_entities: int
    r_squared: float
    estimator: str

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if result is statistically significant."""
        return self.p_value < alpha

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'coefficient': self.coefficient,
            'std_error': self.std_error,
            't_stat': self.t_stat,
            'p_value': self.p_value,
            'ci_lower': self.ci_lower,
            'ci_upper': self.ci_upper,
            'n_obs': self.n_obs,
            'n_entities': self.n_entities,
            'r_squared': self.r_squared,
            'estimator': self.estimator
        }


class TWFEEstimator:
    """Standard TWFE DiD with two-way fixed effects.

    Can be biased in staggered settings (Goodman-Bacon 2021) - use modern
    estimators for robustness check.
    """

    def __init__(self, entity_var: str = 'Ticker', time_var: str = 'Date'):
        self.entity_var = entity_var
        self.time_var = time_var

    def estimate(
        self,
        data: pd.DataFrame,
        outcome: str = 'Abnormal_Return',
        treatment: str = 'Post_Lockup',
        controls: Optional[list] = None
    ) -> DiDResult:
        """Run TWFE DiD regression."""
        # TODO: Consider bootstrap SEs (clustered might be too conservative)
        # TODO: Add option for robust vs clustered SEs
        # TODO: Add weights parameter for WLS (tried this, doesn't work well - see scratch notebook)
        # FIXME: Should probably add option to not use time FE (for small samples)

        # Check we actually have the required columns
        required_cols = [self.entity_var, self.time_var, outcome, treatment]
        missing = [c for c in required_cols if c not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = data[[self.entity_var, self.time_var, outcome, treatment]].copy()
        if controls:
            df = data[[self.entity_var, self.time_var, outcome, treatment] + controls].copy()

        df = df.dropna()
        # print(f"DEBUG: After dropna, {len(df)} obs from {df[self.entity_var].nunique()} entities")

        if len(df) == 0:
            raise ValueError("No data left after dropping NAs - check your input data")

        df_panel = df.set_index([self.entity_var, self.time_var])

        exog_vars = [treatment]
        if controls:
            exog_vars.extend(controls)

        # Sanity check - make sure treatment actually varies
        if df_panel[treatment].nunique() < 2:
            raise ValueError(f"Treatment variable '{treatment}' doesn't vary - can't estimate anything!")

        # Tried using WLS with volume weights - made results unstable
        # Unweighted is more conservative anyway

        # Attempted Fama-MacBeth SEs but way too conservative
        # def _fama_macbeth_se(returns, treatment):
        #     # Cross-sectional regression each period, then average coeffs
        #     # SEs = std of time-series of coefficients
        #     # Problem: Way too wide CIs, kills all significance
        #     pass

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Clustered SEs - took forever to figure out the right syntax
                # linearmodels docs are... not great
                model = PanelOLS(
                    dependent=df_panel[outcome],
                    exog=df_panel[exog_vars],
                    entity_effects=True,
                    time_effects=True,
                    check_rank=False
                )
                results = model.fit(cov_type='clustered', cluster_entity=True)
        except Exception as e:
            # print(f"DEBUG: Panel regression failed - {str(e)}")
            raise RuntimeError(f"TWFE regression failed: {str(e)}. Check your panel structure.") from e

        # Extract results
        coef = results.params[treatment]
        se = results.std_errors[treatment]
        t_stat = coef / se
        p_val = results.pvalues[treatment]
        ci_lower = coef - 1.96 * se
        ci_upper = coef + 1.96 * se

        return DiDResult(
            coefficient=coef,
            std_error=se,
            t_stat=t_stat,
            p_value=p_val,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            n_obs=int(results.nobs),
            n_entities=df[self.entity_var].nunique(),
            r_squared=results.rsquared_within,
            estimator='TWFE'
        )


class EventStudyEstimator:
    """Event study with dynamic treatment effects by period."""

    def __init__(
        self,
        entity_var: str = 'Ticker',
        time_var: str = 'Date',
        event_time_var: str = 'Days_To_Lockup'
    ):
        self.entity_var = entity_var
        self.time_var = time_var
        self.event_time_var = event_time_var

    def estimate(
        self,
        data: pd.DataFrame,
        outcome: str = 'Abnormal_Return',
        pre_window: int = 30,
        post_window: int = 30,
        omit_period: int = -1
    ) -> pd.DataFrame:
        """Estimate event study coefficients."""
        # Check event time variable exists
        if self.event_time_var not in data.columns:
            raise ValueError(f"Event time variable '{self.event_time_var}' not found in data")

        # Filter to event window
        df = data[
            data[self.event_time_var].between(-pre_window, post_window)
        ].copy()

        if len(df) == 0:
            raise ValueError(f"No data in event window [{-pre_window}, {post_window}] - check your event_time_var")

        # Create event time dummies
        event_times = sorted(df[self.event_time_var].unique())
        event_times = [t for t in event_times if t != omit_period]
        # print(f"DEBUG: Creating dummies for {len(event_times)} event periods")

        # TODO: Add option to bin event times (eg -30 to -20, -20 to -10, etc) for cleaner plots
        # TODO: Return absorbed variable list so user knows which periods got dropped

        if len(event_times) == 0:
            raise ValueError(f"No event time periods found (omit_period={omit_period})")

        for t in event_times:
            df[f'event_{t}'] = (df[self.event_time_var] == t).astype(int)

        # Set up panel
        df_panel = df.set_index([self.entity_var, self.time_var])

        # Run regression with event time dummies
        dummy_vars = [f'event_{t}' for t in event_times]

        # NOTE: drop_absorbed=True needed because time FE + event dummies create collinearity
        # Some coefficients will be absorbed - that's expected
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = PanelOLS(
                    dependent=df_panel[outcome],
                    exog=df_panel[dummy_vars],
                    entity_effects=True,
                    time_effects=True,
                    drop_absorbed=True,  # Critical for avoiding collinearity issues
                    check_rank=False
                )
                results = model.fit(cov_type='clustered', cluster_entity=True)
        except Exception as e:
            # Ugh, this happens when FE absorb everything. Usually means data issue.
            raise RuntimeError(f"Event study regression failed: {str(e)}") from e

        # Extract coefficients (skip ones that got absorbed by FE)
        # NOTE: Some vars will be absorbed - that's expected with time FE
        coeffs = []
        for t in event_times:
            var_name = f'event_{t}'
            if var_name in results.params.index:
                coeffs.append({
                    'event_time': t,
                    'coefficient': results.params[var_name],
                    'std_error': results.std_errors[var_name],
                    'p_value': results.pvalues[var_name]
                })
            else:
                # Variable was absorbed by fixed effects
                coeffs.append({
                    'event_time': t,
                    'coefficient': np.nan,
                    'std_error': np.nan,
                    'p_value': np.nan
                })

        # Add omitted period
        coeffs.append({
            'event_time': omit_period,
            'coefficient': 0.0,
            'std_error': 0.0,
            'p_value': np.nan
        })

        df_coeffs = pd.DataFrame(coeffs).sort_values('event_time')
        df_coeffs['ci_lower'] = df_coeffs['coefficient'] - 1.96 * df_coeffs['std_error']
        df_coeffs['ci_upper'] = df_coeffs['coefficient'] + 1.96 * df_coeffs['std_error']

        return df_coeffs


def test_parallel_trends(
    data: pd.DataFrame,
    outcome: str = 'Abnormal_Return',
    time_var: str = 'Days_To_Lockup',
    pre_window: Tuple[int, int] = (-30, -1)
) -> Dict:
    """Test for pre-trends in pre-treatment period."""
    from scipy import stats

    df_pre = data[data[time_var].between(pre_window[0], pre_window[1])].copy()

    if len(df_pre) == 0:
        return {
            'slope': np.nan,
            'p_value': np.nan,
            'passes': False,
            'message': 'No pre-treatment data available'
        }

    # Simple linear regression of outcome on time
    result = stats.linregress(df_pre[time_var], df_pre[outcome])

    return {
        'slope': result.slope,
        'p_value': result.pvalue,
        'passes': result.pvalue > 0.05,
        'message': 'No significant pre-trend' if result.pvalue > 0.05 else 'Significant pre-trend detected'
    }
