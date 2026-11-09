import pandas as pd

from factorlab.data import read_factor_csv


def test_factor_csv_parses_dates_and_numeric_columns(tmp_path):
    p = tmp_path / "factors.csv"
    p.write_text("date,Mkt-RF,RF\n2024-01-31,0.01,0.001\n2024-02-29,-0.02,0.001\n", encoding="utf-8")
    data = read_factor_csv(str(p))
    assert isinstance(data.index, pd.DatetimeIndex)
    assert list(data.columns) == ["Mkt-RF", "RF"]
    assert data.loc[pd.Timestamp("2024-01-31"), "Mkt-RF"] == .01
