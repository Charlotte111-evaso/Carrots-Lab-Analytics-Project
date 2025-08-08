import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import ttest_ind

st.set_page_config(page_title="Mobile App Campaign Dashboard", layout="wide")

# -------------------------
# Load & preprocess data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("../data/mobile_funnel_data.csv", parse_dates=["date"])
    # Derived KPIs
    df['CTR'] = df['clicks'] / df['impressions']
    df['Conversion'] = df['purchases'] / df['installs'].replace(0, 1)
    df['CPI'] = (df['impressions'] * 0.01) / df['installs'].replace(0, 1)  # assume €0.01 per impression
    df['LTV'] = df['revenue'] / df['installs'].replace(0, 1)
    df['ROI'] = df['LTV'] / df['CPI'].replace(0, 1)
    return df

df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.title("📊 Filters")
campaign_filter = st.sidebar.selectbox("Campaign", options=["All", "A", "B"])
date_default = [df['date'].min(), df['date'].max()]
date_range = st.sidebar.date_input(
    "Date Range",
    date_default,
    min_value=df['date'].min(),
    max_value=df['date'].max()
)

filtered_df = df.copy()
if campaign_filter != "All":
    filtered_df = filtered_df[filtered_df["campaign"] == campaign_filter]

filtered_df = filtered_df[
    (filtered_df["date"] >= pd.to_datetime(date_range[0])) &
    (filtered_df["date"] <= pd.to_datetime(date_range[1]))
]

# -------------------------
# Header
# -------------------------
st.title("📱 Mobile App Campaign Dashboard – Carrots Lab (Simulation)")
st.markdown("Analyze acquisition funnel performance, core KPIs, A/B tests, and retention for two campaigns (A & B).")

# -------------------------
# KPI Cards
# -------------------------
st.subheader("Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg CTR", f"{filtered_df['CTR'].mean():.2%}")
k2.metric("Avg CPI (€)", f"{filtered_df['CPI'].mean():.2f}")
k3.metric("Avg ROI", f"{filtered_df['ROI'].mean():.2f}")
k4.metric("Retention (D7)", f"{filtered_df['retained_day_7'].mean():.2%}")

# -------------------------
# Funnel Chart (filtered)
# -------------------------
st.subheader("📉 Funnel Breakdown")
funnel = filtered_df[['impressions', 'clicks', 'installs', 'purchases']].sum()
funnel_df = funnel.reset_index()
funnel_df.columns = ['Stage', 'Count']
funnel_fig = px.bar(
    funnel_df, x='Stage', y='Count', title='Funnel Stages (Filtered)',
    text='Count', color='Stage', color_discrete_sequence=px.colors.qualitative.Set2
)
funnel_fig.update_traces(textposition='outside')
st.plotly_chart(funnel_fig, use_container_width=True)

# -------------------------
# Revenue by Campaign (global)
# -------------------------
st.subheader("💶 Total Revenue by Campaign (All Dates)")
revenue_df = df.groupby('campaign')['revenue'].sum().reset_index()
revenue_fig = px.bar(
    revenue_df, x='campaign', y='revenue', text='revenue',
    color='campaign', color_discrete_sequence=["#EF553B", "#00CC96"]
)
revenue_fig.update_traces(textposition='outside')
st.plotly_chart(revenue_fig, use_container_width=True)

# -------------------------
# Time Series: Installs over time (filtered)
# -------------------------
st.subheader("📈 Daily Installs Over Time (Filtered)")
daily_installs = filtered_df.groupby('date')['installs'].sum().reset_index()
if not daily_installs.empty:
    trend_fig = px.line(daily_installs, x='date', y='installs', markers=True, title='Installs Over Time')
    st.plotly_chart(trend_fig, use_container_width=True)
else:
    st.write("No data for selected filters.")

# -------------------------
# Retention Rate by Campaign (global)
# -------------------------
st.subheader("🔁 Day-7 Retention by Campaign (All Dates)")
retention_df = df.groupby('campaign')['retained_day_7'].mean().reset_index()
retention_fig = px.bar(
    retention_df, x='campaign', y='retained_day_7', text='retained_day_7',
    color='campaign', color_discrete_sequence=px.colors.qualitative.Dark24,
    labels={'retained_day_7': 'Retention (D7)'}
)
retention_fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
st.plotly_chart(retention_fig, use_container_width=True)

# -------------------------
# A/B Test Summary (global)
# -------------------------
st.subheader("🧪 A/B Test Results (A vs B, All Data)")

a = df[df['campaign'] == 'A']
b = df[df['campaign'] == 'B']

def ab_test(metric):
    a_vals = a[metric].dropna()
    b_vals = b[metric].dropna()
    if len(a_vals) == 0 or len(b_vals) == 0:
        return np.nan, np.nan, "N/A"
    t, p = ttest_ind(a_vals, b_vals)
    return round(t, 3), round(p, 4), ("Significant" if p < 0.05 else "Not Significant")

metrics_to_test = ['CTR', 'Conversion', 'ROI', 'retained_day_7']
results = {m: ab_test(m) for m in metrics_to_test}

ab_test_df = pd.DataFrame([
    {'Metric': m, 't-stat': t, 'p-value': p, 'Result': r}
    for m, (t, p, r) in results.items()
])

st.dataframe(ab_test_df.style.format({'p-value': '{:.4f}'}), use_container_width=True)

# -------------------------
# Strategic Insights
# -------------------------
with st.expander("📈 Strategic Insights & Recommendations", expanded=True):
    st.markdown("""
**Key Insights**
- **Campaign B** outperforms Campaign A on **conversion** and **Day-7 retention** (p < 0.05).
- While **CPI** may be slightly higher for B, **ROI** is higher overall → better efficiency.
- Largest funnel drop-off is **Install → Purchase** for both campaigns.

**Recommendations**
- Shift **~25–30%** budget from A → B and re-evaluate in 2 weeks.
- Add **re-engagement** for installers who don’t purchase (push/email offers).
- Segment by **device/region** for more granular experiments.
- Track **weekly retention cohorts** to validate long-term lift.
""")

st.markdown("---")
st.markdown("📊 *Simulated case study to demonstrate product analytics for Carrots Lab internship*")