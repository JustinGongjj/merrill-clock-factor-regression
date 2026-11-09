import numpy as np
import pandas as pd

from factorlab.regression import factor_regression
from examples_factor_regression import synthetic_demo


def test_factor_regression_runs_with_risk_free_adjustment():
    rng = np.random.default_rng(12)
    idx = pd.date_range("2010-01-31", periods=80, freq="ME")
    factors = pd.DataFrame({"Mkt-RF": rng.normal(0, .04, 80), "SMB": rng.normal(0, .02, 80)}, index=idx)
    rf = pd.Series(.001, index=idx)
    strategy = .001 + .7 * factors["Mkt-RF"] + .1 * factors["SMB"] + rf + rng.normal(0, .01, 80)
    result = factor_regression(strategy, factors, maxlags=3, risk_free_returns=rf)
    assert int(result.nobs) == 80
    assert "const" in result.params.index
    assert np.isfinite(result.tvalues).all()


def test_offline_demo_is_reproducible_and_regressible():
    strategy, factors, rf = synthetic_demo(seed=44, periods=90)
    result = factor_regression(strategy, factors, maxlags=3, risk_free_returns=rf)
    assert int(result.nobs) == 90
    assert np.isfinite(result.params).all()


def test_regression_rejects_too_few_complete_rows():
    idx = pd.date_range("2020-01-31", periods=4, freq="ME")
    y = pd.Series([.01, .02, .01, .00], index=idx)
    x = pd.DataFrame({"factor": [.01, .00, .02, -.01]}, index=idx)
    try:
        factor_regression(y, x)
    except ValueError as exc:
        assert "Too few" in str(exc)
    else:
        raise AssertionError("expected a too-few-observations error")
