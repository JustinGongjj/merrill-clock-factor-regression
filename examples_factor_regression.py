"""Standalone HAC factor-regression example.

No arguments runs an offline deterministic synthetic demo. To analyze your own
strategy return CSV, pass --returns-csv; supply --factors-csv to avoid the
optional live Fama-French download.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from factorlab.data import fetch_fama_french_5_factors, read_factor_csv
from factorlab.regression import factor_regression


def synthetic_demo(seed: int = 2026, periods: int = 120):
    """Return simulated monthly factor and strategy data for an offline demo."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2015-01-31", periods=periods, freq="ME")
    factors = pd.DataFrame({
        "Mkt-RF": rng.normal(0.006, 0.04, periods),
        "SMB": rng.normal(0.001, 0.025, periods),
        "HML": rng.normal(0.001, 0.025, periods),
        "RMW": rng.normal(0.001, 0.02, periods),
        "CMA": rng.normal(0.001, 0.02, periods),
    }, index=idx)
    rf = pd.Series(0.001, index=idx, name="RF")
    beta = np.array([0.7, 0.15, -0.1, 0.05, 0.1])
    strategy = pd.Series(0.001 + factors.to_numpy() @ beta + rf.to_numpy()
                          + rng.normal(0.0, 0.02, periods), index=idx, name="strategy_return")
    return strategy, factors, rf


def main() -> int:
    parser = argparse.ArgumentParser(description="HAC factor regression demo")
    parser.add_argument("--returns-csv", type=Path, help="CSV with date and strategy return column (decimal returns)")
    parser.add_argument("--return-column", default="net_return")
    parser.add_argument("--date-column", default="date")
    parser.add_argument("--factors-csv", type=Path, help="optional CSV with date and decimal factor returns; may include RF")
    parser.add_argument("--maxlags", type=int, default=3, help="Newey-West/HAC maximum lag")
    args = parser.parse_args()

    if args.returns_csv is None:
        if args.factors_csv is not None:
            parser.error("--factors-csv requires --returns-csv")
        strategy, factors, rf = synthetic_demo()
        print("Demo data: deterministic synthetic monthly returns (not real market data).")
    else:
        raw = pd.read_csv(args.returns_csv)
        if args.date_column not in raw or args.return_column not in raw:
            parser.error(f"Returns CSV needs {args.date_column!r} and {args.return_column!r} columns")
        raw[args.date_column] = pd.to_datetime(raw[args.date_column], errors="coerce")
        raw[args.return_column] = pd.to_numeric(raw[args.return_column], errors="coerce")
        strategy = raw.dropna(subset=[args.date_column, args.return_column]).set_index(args.date_column)[args.return_column].sort_index()
        if args.factors_csv is not None:
            factor_frame = read_factor_csv(str(args.factors_csv), date_column=args.date_column)
        else:
            print("Fetching the public Fama-French five-factor file; check its current terms before use.")
            factor_frame = fetch_fama_french_5_factors()
        rf = factor_frame["RF"] if "RF" in factor_frame.columns else None
        factors = factor_frame.drop(columns=["RF"], errors="ignore")

    result = factor_regression(strategy, factors, maxlags=args.maxlags, risk_free_returns=rf)
    print(f"Observations: {int(result.nobs)}")
    print("Coefficients:\n", result.params.to_string())
    print("HAC t-statistics:\n", result.tvalues.to_string())
    print("HAC p-values:\n", result.pvalues.to_string())
    print(f"R-squared: {float(result.rsquared):.6f}")
    print("Interpretation: the intercept and factor loadings describe this historical sample; they are not forecasts or causal effects.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
