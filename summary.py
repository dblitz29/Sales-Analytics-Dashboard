"""Build the one-paragraph, Telegram-readable summary for a sales manager.

Two modes:
- "ai": calls an LLM with the already-computed numbers (the model summarizes
  facts, it does not do arithmetic, so numbers can't be hallucinated).
- "template": deterministic f-string built from the same numbers, used
  whenever no OPENAI_API_KEY is set or the API call fails for any reason.
  The app must always produce a usable summary with zero network/API setup.
"""
import os
import pandas as pd


def _facts(region_df: pd.DataFrame, brand_df: pd.DataFrame, weak_df: pd.DataFrame) -> dict:
    total = region_df["net_sales_idr"].sum()
    top_region = region_df.iloc[0]
    bottom_region = region_df.iloc[-1]
    top_brand = brand_df.iloc[0]
    weak_names = weak_df["outlet_name"].tolist()
    return {
        "total": total,
        "top_region": top_region["region"], "top_region_sales": top_region["net_sales_idr"],
        "bottom_region": bottom_region["region"], "bottom_region_sales": bottom_region["net_sales_idr"],
        "top_brand": top_brand["brand"], "top_brand_sales": top_brand["net_sales_idr"],
        "weak_names": weak_names,
    }


def _template_summary(facts: dict) -> str:
    weak_list = ", ".join(facts["weak_names"])
    return (
        f"Periode September-Oktober 2026: total penjualan bersih mencapai "
        f"Rp{facts['total']:,.0f}. Region {facts['top_region']} memimpin dengan "
        f"Rp{facts['top_region_sales']:,.0f}, sedangkan {facts['bottom_region']} "
        f"paling rendah (Rp{facts['bottom_region_sales']:,.0f}). Brand terkuat adalah "
        f"{facts['top_brand']} (Rp{facts['top_brand_sales']:,.0f}). 5 outlet dengan "
        f"penjualan terlemah yang perlu perhatian: {weak_list}."
    ).replace(",", ".")


def _ai_summary(facts: dict) -> str:
    from openai import OpenAI
    client = OpenAI()
    weak_list = ", ".join(facts["weak_names"])
    prompt = (
        "Tulis satu paragraf ringkas (maksimal 80 kata, teks biasa tanpa markdown) "
        "untuk sales manager, cocok dikirim lewat Telegram, berdasarkan data berikut:\n"
        f"- Total penjualan bersih Sep-Okt 2026: Rp{facts['total']:,.0f}\n"
        f"- Region tertinggi: {facts['top_region']} (Rp{facts['top_region_sales']:,.0f})\n"
        f"- Region terendah: {facts['bottom_region']} (Rp{facts['bottom_region_sales']:,.0f})\n"
        f"- Brand terkuat: {facts['top_brand']} (Rp{facts['top_brand_sales']:,.0f})\n"
        f"- 5 outlet terlemah: {weak_list}\n"
        "Gunakan hanya angka dan fakta di atas. Jangan menambahkan angka, tren, "
        "sebab-akibat, atau rekomendasi generik yang tidak didukung data ini."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.4,
    )
    return resp.choices[0].message.content.strip()


def build_summary(region_df: pd.DataFrame, brand_df: pd.DataFrame, weak_df: pd.DataFrame):
    """Returns (text, mode) where mode is 'ai' or 'template'."""
    facts = _facts(region_df, brand_df, weak_df)
    if os.getenv("OPENAI_API_KEY"):
        try:
            return _ai_summary(facts), "ai"
        except Exception:
            pass
    return _template_summary(facts), "template"
