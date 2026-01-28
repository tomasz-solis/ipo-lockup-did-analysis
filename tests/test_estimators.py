"""
Unit tests for DiD estimators.
"""
import pytest
import pandas as pd
import numpy as np
from src.estimators import TWFEEstimator, EventStudyEstimator, test_parallel_trends


@pytest.fixture
def sample_panel_data():
    """Generate sample panel data for testing."""
    np.random.seed(42)

    tickers = ['A', 'B', 'C', 'D', 'E']
    dates = pd.date_range('2020-01-01', periods=100, freq='D')

    data = []
    for ticker in tickers:
        for date in dates:
            days_since_ipo = (date - pd.Timestamp('2020-01-01')).days
            post_lockup = 1 if days_since_ipo > 50 else 0

            # Simulate return with small treatment effect
            abnormal_return = np.random.normal(0, 1) + post_lockup * 0.5

            data.append({
                'Ticker': ticker,
                'Date': date,
                'Days_Since_IPO': days_since_ipo,
                'Days_To_Lockup': days_since_ipo - 50,
                'Post_Lockup': post_lockup,
                'Abnormal_Return': abnormal_return
            })

    return pd.DataFrame(data)


def test_twfe_estimator_runs(sample_panel_data):
    """Test that TWFE estimator runs without errors."""
    estimator = TWFEEstimator()
    result = estimator.estimate(sample_panel_data)

    assert result is not None
    assert hasattr(result, 'coefficient')
    assert hasattr(result, 'p_value')
    assert result.n_obs > 0


def test_twfe_detects_treatment_effect(sample_panel_data):
    """Test that TWFE can detect a known treatment effect."""
    estimator = TWFEEstimator()
    result = estimator.estimate(sample_panel_data)

    # Should detect positive effect (we added 0.5 to treated periods)
    assert result.coefficient > 0
    # Should be statistically significant with this sample size
    assert result.p_value < 0.05


def test_event_study_estimator_runs(sample_panel_data):
    """Test that event study estimator runs."""
    estimator = EventStudyEstimator()
    results = estimator.estimate(sample_panel_data, pre_window=20, post_window=20)

    assert len(results) > 0
    assert 'event_time' in results.columns
    assert 'coefficient' in results.columns


def test_parallel_trends_test(sample_panel_data):
    """Test parallel trends testing function."""
    # Use only pre-treatment data
    pre_data = sample_panel_data[sample_panel_data['Post_Lockup'] == 0]

    result = test_parallel_trends(pre_data, pre_window=(-30, -1))

    assert 'slope' in result
    assert 'p_value' in result
    assert 'passes' in result
    assert isinstance(result['passes'], bool)


def test_twfe_with_no_treatment_variation():
    """Test that estimator handles edge case of no treatment variation."""
    data = pd.DataFrame({
        'Ticker': ['A', 'B'] * 10,
        'Date': pd.date_range('2020-01-01', periods=20),
        'Post_Lockup': [0] * 20,  # No treatment
        'Abnormal_Return': np.random.normal(0, 1, 20)
    })

    estimator = TWFEEstimator()

    # Should handle gracefully (may raise or return null result)
    try:
        result = estimator.estimate(data)
        # If it returns, check it's sensible
        assert result is not None
    except (ValueError, KeyError):
        # Acceptable to raise error for invalid input
        pass


def test_did_result_dataclass():
    """Test DiDResult dataclass functionality."""
    from src.estimators import DiDResult

    result = DiDResult(
        coefficient=0.5,
        std_error=0.1,
        t_stat=5.0,
        p_value=0.001,
        ci_lower=0.3,
        ci_upper=0.7,
        n_obs=1000,
        n_entities=50,
        r_squared=0.05,
        estimator='TWFE'
    )

    assert result.is_significant(alpha=0.05)
    assert not result.is_significant(alpha=0.0001)

    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict['coefficient'] == 0.5
