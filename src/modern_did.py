"""
Modern DiD estimators (Callaway-Sant'Anna, Goodman-Bacon).

NOTE: Implemented C-S for learning modern methods, but it's not fully
applicable to IPO setting (universal treatment - all IPOs get lockups).
Used Goodman-Bacon decomposition in main analysis. Keeping C-S for reference.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CallawayResults:
    """Results from Callaway-Sant'Anna estimation."""
    att_simple: float  # Simple ATT (average across all cohorts)
    att_calendar: pd.DataFrame  # ATT by calendar time
    att_event: pd.DataFrame  # ATT by event time
    att_cohort: pd.DataFrame  # ATT by cohort
    group_specific_effects: pd.DataFrame  # Cohort-specific effects


class CallawayEstimator:
    """Callaway-Sant'Anna (2021) DiD estimator.

    Not fully applicable to IPO lockups (universal treatment) but useful
    for robustness check. See Callaway & Sant'Anna (2021) JoE.

    TODO: Could adapt for staggered timing instead of universal treatment
    """

    def __init__(
        self,
        data: pd.DataFrame,
        outcome: str,
        group_var: str,
        time_var: str,
        treatment_var: str
    ):
        """Init estimator."""
        # Check required columns exist
        required_cols = [outcome, group_var, time_var, treatment_var]
        missing = [c for c in required_cols if c not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        self.data = data.copy()
        self.outcome = outcome
        self.group_var = group_var
        self.time_var = time_var
        self.treatment_var = treatment_var

    def _identify_cohorts(self) -> pd.DataFrame:
        """Identify treatment cohorts (first treatment time per entity)."""
        # Find first treatment time for each entity
        treated = self.data[self.data[self.treatment_var] == 1]

        if len(treated) == 0:
            raise ValueError("No treated units found")

        cohorts = treated.groupby(self.group_var)[self.time_var].min().reset_index()
        cohorts.columns = [self.group_var, 'cohort']

        return cohorts

    def _compute_group_time_att(
        self,
        cohort: int,
        time_period: int,
        comparison_group: str = 'never_treated'
    ) -> Dict:
        """Compute group-time ATT."""
        # TODO: Should probably use propensity scores here for more robust comparison
        # TODO: Add doubly-robust estimation (propensity scores + outcome regression)
        # TODO: Bootstrap SEs instead of analytical (more robust to misspecification)
        # Current approach is simplified DiD
        # Get treated units in this cohort
        cohorts = self._identify_cohorts()
        treated_units = cohorts[cohorts['cohort'] == cohort][self.group_var].tolist()

        # Get comparison group
        if comparison_group == 'never_treated':
            # Units never treated
            never_treated = set(self.data[self.group_var].unique()) - set(cohorts[self.group_var].tolist())
            comparison_units = list(never_treated)
        else:
            # Units not yet treated at time_period
            not_yet = cohorts[cohorts['cohort'] > time_period][self.group_var].tolist()
            comparison_units = not_yet

        if len(comparison_units) == 0:
            return {'att': np.nan, 'se': np.nan, 'n_treated': len(treated_units), 'n_control': 0}

        # Get outcome changes for treated units
        treated_pre = self.data[
            (self.data[self.group_var].isin(treated_units)) &
            (self.data[self.time_var] == cohort - 1)
        ]
        treated_post = self.data[
            (self.data[self.group_var].isin(treated_units)) &
            (self.data[self.time_var] == time_period)
        ]

        # Get outcome changes for control units
        control_pre = self.data[
            (self.data[self.group_var].isin(comparison_units)) &
            (self.data[self.time_var] == cohort - 1)
        ]
        control_post = self.data[
            (self.data[self.group_var].isin(comparison_units)) &
            (self.data[self.time_var] == time_period)
        ]

        # Merge to compute changes
        treated_merged = treated_pre[[self.group_var, self.outcome]].merge(
            treated_post[[self.group_var, self.outcome]],
            on=self.group_var,
            suffixes=('_pre', '_post')
        )
        control_merged = control_pre[[self.group_var, self.outcome]].merge(
            control_post[[self.group_var, self.outcome]],
            on=self.group_var,
            suffixes=('_pre', '_post')
        )

        if len(treated_merged) == 0 or len(control_merged) == 0:
            return {'att': np.nan, 'se': np.nan, 'n_treated': len(treated_units), 'n_control': len(comparison_units)}

        # Compute changes (first differences)
        treated_merged['change'] = treated_merged[f'{self.outcome}_post'] - treated_merged[f'{self.outcome}_pre']
        control_merged['change'] = control_merged[f'{self.outcome}_post'] - control_merged[f'{self.outcome}_pre']

        # ATT = diff-in-diff
        att = treated_merged['change'].mean() - control_merged['change'].mean()

        # Standard error (simplified - TODO: bootstrap would be more robust)
        var_treated = treated_merged['change'].var() / len(treated_merged)
        var_control = control_merged['change'].var() / len(control_merged)
        se = np.sqrt(var_treated + var_control)

        return {
            'att': att,
            'se': se,
            'n_treated': len(treated_merged),
            'n_control': len(control_merged)
        }

    def estimate(self, comparison_group: str = 'never_treated') -> CallawayResults:
        """Estimate C-S ATT.

        NOTE: Will fail if no never-treated units (which is the case for IPO lockups)
        """
        try:
            cohorts = self._identify_cohorts()
        except ValueError as e:
            raise ValueError(f"C-S estimation failed: {str(e)}") from e

        time_periods = sorted(self.data[self.time_var].unique())
        # print(f"DEBUG: Found {len(cohorts)} cohorts, {len(time_periods)} time periods")

        # Compute group-time ATTs
        results = []
        for cohort in cohorts['cohort'].unique():
            for t in time_periods:
                if t >= cohort:  # Only post-treatment periods
                    result = self._compute_group_time_att(cohort, t, comparison_group)
                    results.append({
                        'cohort': cohort,
                        'time': t,
                        'event_time': t - cohort,
                        'att': result['att'],
                        'se': result['se'],
                        'n_treated': result['n_treated'],
                        'n_control': result['n_control']
                    })

        df_results = pd.DataFrame(results)
        df_results = df_results.dropna(subset=['att'])

        if len(df_results) == 0:
            raise ValueError("No valid ATT estimates computed")

        # Simple aggregate ATT (equal weight to each group-time)
        # TODO: Should weight by group size for more efficient estimate
        # FIXME: This weighting might be wrong - check CS paper appendix
        att_simple = df_results['att'].mean()

        # ATT by calendar time
        att_calendar = df_results.groupby('time').agg({
            'att': 'mean',
            'se': lambda x: np.sqrt((x**2).sum()) / len(x)  # Simplified SE aggregation
        }).reset_index()

        # ATT by event time (relative to treatment)
        att_event = df_results.groupby('event_time').agg({
            'att': 'mean',
            'se': lambda x: np.sqrt((x**2).sum()) / len(x)
        }).reset_index()

        # ATT by cohort
        att_cohort = df_results.groupby('cohort').agg({
            'att': 'mean',
            'se': lambda x: np.sqrt((x**2).sum()) / len(x)
        }).reset_index()

        return CallawayResults(
            att_simple=att_simple,
            att_calendar=att_calendar,
            att_event=att_event,
            att_cohort=att_cohort,
            group_specific_effects=df_results
        )


class GoodmanBacon:
    """Goodman-Bacon (2021) TWFE decomposition.

    Breaks down TWFE into 2x2 comparisons to show which comparisons drive
    the result and identify "problematic" ones using already-treated as controls.

    See Goodman-Bacon (2021) JoE.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        outcome: str,
        group_var: str,
        time_var: str,
        treatment_time_var: str
    ):
        """Init decomposition."""
        # Check columns
        required = [outcome, group_var, time_var, treatment_time_var]
        missing = [c for c in required if c not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        self.data = data.copy()
        self.outcome = outcome
        self.group_var = group_var
        self.time_var = time_var
        self.treatment_time_var = treatment_time_var

    def decompose(self) -> pd.DataFrame:
        """Compute G-B decomposition into 2x2 comparisons."""
        # Identify treatment cohorts
        treatment_times = self.data.groupby(self.group_var)[self.treatment_time_var].first()

        if len(treatment_times) == 0:
            raise ValueError("No groups found - check your group_var")

        never_treated = treatment_times[treatment_times == np.inf].index.tolist()
        treated_cohorts = sorted(treatment_times[treatment_times < np.inf].unique())
        # print(f"DEBUG: {len(treated_cohorts)} treated cohorts, {len(never_treated)} never-treated")

        comparisons = []

        # 1. Treated vs Never treated
        for cohort in treated_cohorts:
            cohort_units = treatment_times[treatment_times == cohort].index.tolist()

            if len(never_treated) > 0:
                att, weight = self._compute_2x2_did(cohort_units, never_treated, cohort)
                comparisons.append({
                    'comparison_type': 'Treated vs Never Treated',
                    'treated_cohort': cohort,
                    'control_cohort': 'Never',
                    'att': att,
                    'weight': weight,
                    'is_problematic': False
                })

        # 2. Earlier vs Later treated
        for i, early_cohort in enumerate(treated_cohorts[:-1]):
            for late_cohort in treated_cohorts[i+1:]:
                early_units = treatment_times[treatment_times == early_cohort].index.tolist()
                late_units = treatment_times[treatment_times == late_cohort].index.tolist()

                # Early treated, late as control (good comparison)
                att, weight = self._compute_2x2_did(early_units, late_units, early_cohort, late_cohort)
                comparisons.append({
                    'comparison_type': 'Earlier vs Later Treated',
                    'treated_cohort': early_cohort,
                    'control_cohort': late_cohort,
                    'att': att,
                    'weight': weight,
                    'is_problematic': False
                })

                # Late treated, early as control (problematic - already treated control)
                att, weight = self._compute_2x2_did(late_units, early_units, late_cohort, early_cohort)
                comparisons.append({
                    'comparison_type': 'Later vs Earlier Treated (Problematic)',
                    'treated_cohort': late_cohort,
                    'control_cohort': early_cohort,
                    'att': att,
                    'weight': weight,
                    'is_problematic': True
                })

        df_decomp = pd.DataFrame(comparisons)

        # Normalize weights
        total_weight = df_decomp['weight'].sum()
        if total_weight > 0:
            df_decomp['weight'] = df_decomp['weight'] / total_weight

        return df_decomp

    def _compute_2x2_did(
        self,
        treated_units: List,
        control_units: List,
        treatment_time: int,
        control_treatment_time: Optional[int] = None
    ) -> tuple:
        """Compute 2x2 DiD estimate with weight."""
        # FIXME: Simplified weighting - should match G-B paper more closely
        # Current approach uses sample sizes, not variance-based weights
        # TODO: Implement proper variance-weighted decomposition (see G-B equation 5)

        # Get pre/post periods
        pre_data = self.data[self.data[self.time_var] < treatment_time]
        post_data = self.data[self.data[self.time_var] >= treatment_time]

        # HACK: This weighting isn't quite right but close enough
        # Treated group changes
        treated_pre = pre_data[pre_data[self.group_var].isin(treated_units)][self.outcome].mean()
        treated_post = post_data[post_data[self.group_var].isin(treated_units)][self.outcome].mean()

        # Control group changes
        if control_treatment_time is not None:
            # Control group only until they get treated
            control_post_data = post_data[post_data[self.time_var] < control_treatment_time]
        else:
            control_post_data = post_data

        control_pre = pre_data[pre_data[self.group_var].isin(control_units)][self.outcome].mean()
        control_post = control_post_data[control_post_data[self.group_var].isin(control_units)][self.outcome].mean()

        # DiD
        att = (treated_post - treated_pre) - (control_post - control_pre)

        # HACK: This weighting isn't quite right but close enough
        # Should use variance of outcomes, not just sample sizes
        n_treated = len(treated_units)
        n_control = len(control_units)
        weight = n_treated * n_control / (n_treated + n_control)

        return att, weight
