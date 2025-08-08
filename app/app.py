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
    df['CPI'] = (df['impressions'] * 0.01) / df['installs'].replace(0, 1)
    df['LTV'] = df['revenue'] / df['installs'].replace(0, 1)
    df['ROI'] = df['LTV'] / df['CPI'].replace(0, 1)
    return df

df = load_data()

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.title("📊 Filters")
campaign_filter = st.sidebar.selectbox("Select Campaign", options=["All", "A", "B"])
date_default = [df['date'].min(), df['date'].max()]
date_range = st.sidebar.date_input(
    "Select Date Range",
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
st.markdown("Analyze acquisition funnel performance, product KPIs, A/B tests, and retention across two campaigns (A & B).")

# -------------------------
# DAU / MAU / Stickiness  (ACTIVE users only)
# Define an 'active user' as someone who did more than see an ad: clicked OR installed OR purchased
# -------------------------
active_df = filtered_df[
    (filtered_df['clicks'] > 0) | (filtered_df['installs'] > 0) | (filtered_df['purchases'] > 0)
].copy()

# DAU: unique active users per day
dau_daily = (
    active_df.groupby('date')['user_id']
    .nunique()
    .rename('DAU')
    .reset_index()
)

# MAU: unique active users per calendar month
if not active_df.empty:
    active_df['month'] = active_df['date'].values.astype('datetime64[M]')
    mau_monthly = (
        active_df.groupby('month')['user_id']
        .nunique()
        .rename('MAU')
        .reset_index()
    )
else:
    mau_monthly = pd.DataFrame(columns=['month', 'MAU'])

# Stickiness = avg daily DAU in month / MAU (same month)
if not dau_daily.empty:
    dau_daily_m = dau_daily.copy()
    dau_daily_m['month'] = dau_daily_m['date'].values.astype('datetime64[M]')
    avg_dau_by_month = (
        dau_daily_m.groupby('month')['DAU']
        .mean()
        .reset_index()
        .rename(columns={'DAU': 'avg_DAU'})
    )
else:
    avg_dau_by_month = pd.DataFrame(columns=['month', 'avg_DAU'])

stickiness = avg_dau_by_month.merge(mau_monthly, on='month', how='inner') if not mau_monthly.empty else pd.DataFrame(columns=['month','avg_DAU','MAU'])
if not stickiness.empty:
    stickiness['DAU_MAU_ratio'] = (stickiness['avg_DAU'] / stickiness['MAU']).fillna(0.0)

# KPI snapshots
latest_day = dau_daily['date'].max() if not dau_daily.empty else None
last7_dau = dau_daily[dau_daily['date'] >= (latest_day - pd.Timedelta(days=6))]['DAU'].mean() if latest_day else 0

latest_month = mau_monthly['month'].max() if not mau_monthly.empty else None
latest_mau = int(mau_monthly[mau_monthly['month'] == latest_month]['MAU'].iloc[0]) if latest_month is not None else 0
latest_stickiness = float(stickiness[stickiness['month'] == latest_month]['DAU_MAU_ratio'].iloc[0]) if (latest_month is not None and not stickiness.empty) else 0.0

# -------------------------
# KPI Cards
# -------------------------
st.subheader("Key Performance Indicators")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Avg CTR", f"{filtered_df['CTR'].mean():.2%}")
k2.metric("Avg CPI (€)", f"{filtered_df['CPI'].mean():.2f}")
k3.metric("Avg ROI", f"{filtered_df['ROI'].mean():.2f}")
k4.metric("Retention (D7)", f"{filtered_df['retained_day_7'].mean():.2%}")
k5.metric("DAU (7-day avg)", f"{last7_dau:.0f}")
k6.metric("MAU (latest month)", f"{latest_mau:,}")
st.info(f"**Stickiness (DAU/MAU, latest month):** {latest_stickiness:.1%}")

# -------------------------
# Funnel Chart
# -------------------------
st.subheader("📉 Funnel Breakdown")
funnel = filtered_df[['impressions', 'clicks', 'installs', 'purchases']].sum()
funnel_df = funnel.reset_index()
funnel_df.columns = ['Stage', 'Count']
funnel_fig = px.bar(
    funnel_df, x='Stage', y='Count', title='Funnel Stages',
    text='Count', color='Stage', color_discrete_sequence=px.colors.qualitative.Set2
)
funnel_fig.update_traces(textposition='outside')
st.plotly_chart(funnel_fig, use_container_width=True)

# -------------------------
# Revenue by Campaign (global)
# -------------------------
st.subheader("💶 Total Revenue by Campaign")
revenue_df = df.groupby('campaign')['revenue'].sum().reset_index()
revenue_fig = px.bar(
    revenue_df, x='campaign', y='revenue', text='revenue',
    color='campaign', color_discrete_sequence=["#EF553B", "#00CC96"], title="Total Revenue (All Dates)"
)
revenue_fig.update_traces(textposition='outside')
st.plotly_chart(revenue_fig, use_container_width=True)

# -------------------------
# Time Series: Installs over time (filtered)
# -------------------------
st.subheader("📈 Daily Installs Over Time")
daily_installs = filtered_df.groupby('date')['installs'].sum().reset_index()
if not daily_installs.empty:
    trend_fig = px.line(daily_installs, x='date', y='installs', markers=True, title='Installs Over Time')
    st.plotly_chart(trend_fig, use_container_width=True)
else:
    st.write("No data for selected filters.")

# -------------------------
# DAU & MAU Charts
# -------------------------
st.subheader("👥 Daily Active Users (DAU)")
if not dau_daily.empty:
    dau_fig = px.line(dau_daily, x='date', y='DAU', markers=True, title='DAU Over Time')
    st.plotly_chart(dau_fig, use_container_width=True)
else:
    st.write("No DAU data for selected filters.")

st.subheader("👥 Monthly Active Users (MAU) & Stickiness")
if not mau_monthly.empty:
    mau_fig = px.bar(mau_monthly, x='month', y='MAU', title='Monthly Active Users (MAU)')
    st.plotly_chart(mau_fig, use_container_width=True)

    if not stickiness.empty:
        stick_fig = px.bar(
            stickiness, x='month', y='DAU_MAU_ratio',
            title='DAU/MAU Stickiness', labels={'DAU_MAU_ratio': 'Stickiness'},
            text='DAU_MAU_ratio'
        )
        stick_fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
        st.plotly_chart(stick_fig, use_container_width=True)
else:
    st.write("No monthly activity for selected filters.")

# -------------------------
# Retention Rate by Campaign (global)
# -------------------------
st.subheader("🔁 Day-7 Retention by Campaign")
retention_df = df.groupby('campaign')['retained_day_7'].mean().reset_index()
retention_fig = px.bar(
    retention_df, x='campaign', y='retained_day_7', text='retained_day_7',
    color='campaign', color_discrete_sequence=px.colors.qualitative.Dark24,
    title="Day-7 Retention Rate"
)
retention_fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
st.plotly_chart(retention_fig, use_container_width=True)

# -------------------------
# A/B Test Summary (global A vs B)
# -------------------------
st.subheader("🧪 A/B Test Results (A vs B)")
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
- **DAU** shows healthy activity; **MAU & stickiness** indicate recurring usage.

**Recommendations**
- Shift **~25–30%** budget from A → B and re-evaluate in 2 weeks.
- Add **re-engagement** for installers who don’t purchase (push/email offers).
- Segment by **device/region** for more granular experiments.
- Track **weekly retention cohorts** to validate long-term lift.
""")

st.markdown("---")
st.markdown("📊 *Simulated case study to demonstrate product analytics for Carrots Lab internship*")
