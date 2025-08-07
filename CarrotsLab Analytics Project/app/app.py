import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import ttest_ind

# --- Load & preprocess data ---
@st.cache_data
def load_data():
    df = pd.read_csv("../data/mobile_funnel_data.csv", parse_dates=["date"])
    df['CTR'] = df['clicks'] / df['impressions']
    df['Conversion'] = df['purchases'] / df['installs'].replace(0, 1)
    df['CPI'] = (df['impressions'] * 0.01) / df['installs'].replace(0, 1)
    df['LTV'] = df['revenue'] / df['installs'].replace(0, 1)
    df['ROI'] = df['LTV'] / df['CPI'].replace(0, 1)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.title("📊 Filters")
campaign_filter = st.sidebar.selectbox("Select Campaign", options=["All", "A", "B"])
date_range = st.sidebar.date_input("Select Date Range", 
                                   [df['date'].min(), df['date'].max()])

# Apply filters
filtered_df = df.copy()
if campaign_filter != "All":
    filtered_df = filtered_df[filtered_df["campaign"] == campaign_filter]

filtered_df = filtered_df[(filtered_df["date"] >= pd.to_datetime(date_range[0])) &
                          (filtered_df["date"] <= pd.to_datetime(date_range[1]))]

# --- Header ---
st.title("📱 Mobile App Campaign Dashboard – Carrots Lab")
st.markdown("This dashboard simulates marketing analytics for a mobile app funnel across two acquisition campaigns (A and B).")

# --- KPI Cards ---
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg CTR", f"{filtered_df['CTR'].mean():.2%}")
col2.metric("Avg CPI (€)", f"{filtered_df['CPI'].mean():.2f}")
col3.metric("Avg ROI", f"{filtered_df['ROI'].mean():.2f}")
col4.metric("Retention (D7)", f"{filtered_df['retained_day_7'].mean():.2%}")

# --- Funnel Chart ---
funnel = filtered_df[['impressions', 'clicks', 'installs', 'purchases']].sum()
funnel_df = funnel.reset_index()
funnel_df.columns = ['Stage', 'Count']

funnel_fig = px.bar(funnel_df, x='Stage', y='Count',
                    title='📉 Funnel Breakdown',
                    text='Count',
                    color='Stage',
                    color_discrete_sequence=px.colors.qualitative.Set2)
funnel_fig.update_traces(textposition='outside')
st.plotly_chart(funnel_fig, use_container_width=True)

# --- Revenue by Campaign ---
st.subheader("💶 Total Revenue by Campaign")
revenue_df = df.groupby('campaign')['revenue'].sum().reset_index()
revenue_fig = px.bar(revenue_df, x='campaign', y='revenue',
                     text='revenue',
                     color='campaign',
                     color_discrete_sequence=["#EF553B", "#00CC96"],
                     title="Total Revenue")
revenue_fig.update_traces(textposition='outside')
st.plotly_chart(revenue_fig, use_container_width=True)

# --- Time-Series: Installs over time ---
st.subheader("📈 Daily Installs Over Time")
daily_installs = filtered_df.groupby('date')['installs'].sum().reset_index()
trend_fig = px.line(daily_installs, x='date', y='installs',
                    markers=True, title="Installs Over Time")
st.plotly_chart(trend_fig, use_container_width=True)

# --- Retention Rate by Campaign ---
st.subheader("🔁 Retention Rate by Campaign")
retention_df = df.groupby('campaign')['retained_day_7'].mean().reset_index()
retention_fig = px.bar(retention_df, x='campaign', y='retained_day_7',
                       text='retained_day_7',
                       color='campaign',
                       color_discrete_sequence=px.colors.qualitative.Dark24,
                       title="Day 7 Retention Rate")
retention_fig.update_traces(textposition='outside')
st.plotly_chart(retention_fig, use_container_width=True)

# --- A/B Test Summary ---
st.subheader("🧪 A/B Test Results")

a = df[df['campaign'] == 'A']
b = df[df['campaign'] == 'B']

def ab_test(metric):
    t, p = ttest_ind(a[metric].dropna(), b[metric].dropna())
    return round(t, 3), round(p, 4), "Significant" if p < 0.05 else "Not Significant"

metrics_to_test = ['CTR', 'Conversion', 'ROI', 'retained_day_7']
results = {metric: ab_test(metric) for metric in metrics_to_test}

ab_test_df = pd.DataFrame([
    {'Metric': metric, 't-stat': t, 'p-value': p, 'Result': result}
    for metric, (t, p, result) in results.items()
])

st.dataframe(ab_test_df.style.format({'p-value': '{:.4f}'}))

# --- Strategic Insights ---
with st.expander("📈 Strategic Insights & Recommendations", expanded=True):
    st.markdown("""
    ### 🧠 Key Insights:
    - **Campaign B** significantly outperforms Campaign A in both **conversion rate** and **Day 7 retention** (p < 0.05).
    - While **CPI** is slightly higher for Campaign B, it yields a **higher ROI**, indicating better long-term efficiency.
    - **Funnel analysis** shows most drop-off occurs at the install → purchase stage for both campaigns.
    - **Daily installs** for Campaign B show a steady upward trend from mid-month, signaling strong acquisition momentum.
    - **Retention uplift** (+10% over Campaign A) suggests higher user quality and potential LTV from Campaign B.

    ### 💡 Recommendations:
    - **Reallocate 25–30%** of Campaign A's budget to Campaign B to optimize return.
    - Consider **targeted re-engagement** flows (push/email) for users who install but don’t convert.
    - Run **follow-up tests** by segmenting campaigns by user type (device, region, channel).
    - Track **cohort-based retention** over the next 4 weeks to validate long-term performance.
    """)

# --- Footer ---
st.markdown("---")
st.markdown("📊 *Simulated case study built to demonstrate product analytics skills for Carrots Lab internship*")