"""Aggregations used by the app. Pure functions, no Streamlit/UI dependency.

"Weakest outlet" = lowest total net_sales_idr over the full period,
grouped by outlet_id (the stable identifier; outlet_name is not unique
and has whitespace duplicates). This definition is stated explicitly
wherever it is displayed, per requirements.md open question #1.
"""
import pandas as pd


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("region", as_index=False)
        .agg(net_sales_idr=("net_sales_idr", "sum"), qty_carton=("qty_carton", "sum"),
             invoices=("invoice_no", "nunique"))
        .sort_values("net_sales_idr", ascending=False)
        .reset_index(drop=True)
    )
    return out


def sales_by_brand(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby("brand", as_index=False)
        .agg(net_sales_idr=("net_sales_idr", "sum"), qty_carton=("qty_carton", "sum"))
        .sort_values("net_sales_idr", ascending=False)
        .reset_index(drop=True)
    )
    return out


def weakest_outlets(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    n = min(n, df["outlet_id"].nunique())
    out = (
        df.groupby(["outlet_id", "outlet_name", "region", "branch", "outlet_type"], as_index=False)
        .agg(net_sales_idr=("net_sales_idr", "sum"))
        .sort_values("net_sales_idr", ascending=True)
        .head(n)
        .reset_index(drop=True)
    )
    return out


if __name__ == "__main__":
    # minimal self-check against a tiny fixture
    fixture = pd.DataFrame([
        {"region": "A", "brand": "X", "invoice_no": "I1", "outlet_id": "O1", "outlet_name": "o1",
         "branch": "b", "outlet_type": "t", "qty_carton": 1, "net_sales_idr": 100},
        {"region": "A", "brand": "Y", "invoice_no": "I1", "outlet_id": "O1", "outlet_name": "o1",
         "branch": "b", "outlet_type": "t", "qty_carton": 2, "net_sales_idr": 200},
        {"region": "B", "brand": "X", "invoice_no": "I2", "outlet_id": "O2", "outlet_name": "o2",
         "branch": "b", "outlet_type": "t", "qty_carton": 1, "net_sales_idr": 50},
    ])
    r = sales_by_region(fixture)
    assert r.loc[r.region == "A", "net_sales_idr"].iloc[0] == 300
    b = sales_by_brand(fixture)
    assert b.loc[b.brand == "X", "net_sales_idr"].iloc[0] == 150
    w = weakest_outlets(fixture, n=5)
    assert list(w["outlet_id"]) == ["O2", "O1"]
    print("metrics self-check passed")
