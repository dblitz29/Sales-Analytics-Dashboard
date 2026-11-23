"""Load and clean sales.csv.

Data quality decisions (see requirements.md):
- Region labels are trimmed, case-normalized (title case) and an explicit
  alias map merges "Jabar" into "Jawa Barat". This must yield exactly the
  6 validated canonical regions.
- outlet_id is the stable grouping key for outlets (outlet_name has
  whitespace-only duplicates: 45 raw vs 42 trimmed variants).
- Missing salesman values and the 3 exact duplicate invoice/sku rows are
  left untouched: no feature in scope depends on salesman, and nothing in
  the brief defines a rule for collapsing duplicate line items.
"""
import pandas as pd

CANONICAL_REGIONS = {
    "Jabodetabek", "Jawa Barat", "Jawa Timur", "Jawa Tengah", "Sumatera", "Kalimantan",
}

REGION_ALIASES = {
    "Jabar": "Jawa Barat",
}

NUMERIC_COLS = [
    "qty_carton", "price_per_carton_idr", "gross_sales_idr", "discount_idr", "net_sales_idr",
]


def _normalize_region(raw: str) -> str:
    cleaned = raw.strip().title()
    # title() turns "Jabar" into "Jabar" (already single word) - alias map is keyed the same way
    return REGION_ALIASES.get(cleaned, cleaned)


def load_data(path: str = "data/sales.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["region"] = df["region"].map(_normalize_region)
    df["outlet_name"] = df["outlet_name"].str.strip()
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="raise")

    unexpected = set(df["region"].unique()) - CANONICAL_REGIONS
    assert not unexpected, f"Region normalization produced unexpected values: {unexpected}"
    assert set(df["region"].unique()) == CANONICAL_REGIONS, (
        "Region normalization did not yield all 6 canonical regions; "
        f"got {sorted(df['region'].unique())}"
    )
    return df


if __name__ == "__main__":
    out = load_data()
    print(f"Loaded {len(out)} rows, {out['region'].nunique()} canonical regions:")
    print(sorted(out["region"].unique()))
