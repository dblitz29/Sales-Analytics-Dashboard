import streamlit as st
from dotenv import load_dotenv

from data import load_data
from metrics import sales_by_region, sales_by_brand, weakest_outlets
from summary import build_summary

def _fmt_compact(value: float) -> str:
    """Rp value as a compact string, e.g. Rp 1.2B / Rp 850.0M / Rp 12K."""
    abs_v = abs(value)
    if abs_v >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.1f}B"
    if abs_v >= 1_000_000:
        return f"Rp {value / 1_000_000:.1f}M"
    if abs_v >= 1_000:
        return f"Rp {value / 1_000:.0f}K"
    return f"Rp {value:,.0f}"


load_dotenv()

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")
st.title("Sales Analytics Dashboard")
st.caption("Sales performance overview · September–October 2026")

df = load_data("data/sales.csv")
st.caption("Data notes: 6 standardized regions · 3 duplicate records retained")

region_df = sales_by_region(df)
brand_df = sales_by_brand(df)
weak_df = weakest_outlets(df, n=5)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Net Sales", _fmt_compact(df["net_sales_idr"].sum()))
kpi2.metric("Total Invoices", f"{df['invoice_no'].nunique():,}")
kpi3.metric("Total Outlets", f"{df['outlet_id'].nunique():,}")
kpi4.metric("Total Cartons Sold", f"{df['qty_carton'].sum():,.0f}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Region")
    st.bar_chart(region_df.set_index("region")["net_sales_idr"], horizontal=True)
    st.dataframe(region_df, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Sales by Brand")
    st.bar_chart(brand_df.set_index("brand")["net_sales_idr"], horizontal=True)
    st.dataframe(brand_df, use_container_width=True, hide_index=True)

st.subheader("5 Weakest Outlets (lowest total net sales, Sep-Oct 2026)")
st.dataframe(weak_df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("Sales Manager Brief")

text, mode = build_summary(region_df, brand_df, weak_df)
badge = "🤖 AI-generated summary" if mode == "ai" else "📐 Template-based summary"
st.caption(badge)
st.text_area("Summary", text, height=120, label_visibility="collapsed")
