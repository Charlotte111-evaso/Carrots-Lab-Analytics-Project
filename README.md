# 📱 Mobile App Analytics Dashboard – Carrots Lab Internship Project

A simulated end-to-end **mobile app product analytics** project demonstrating skills in **ETL, KPI tracking, dashboarding, and A/B testing** — aligned with the Product Analyst Intern role at Carrots Lab.

---

## 🚀 Overview
This project showcases the process of:
- Generating **mobile app campaign data** (synthetic, CSV)
- Cleaning, transforming, and enriching it in Python
- Calculating **core metrics**:
  - CTR, CPI, Conversion Rate
  - LTV, ROI
  - Day-7 Retention
- Conducting **A/B testing** between campaigns
- Visualising insights in an **interactive Streamlit dashboard**
- Providing **strategic recommendations** based on data

---

## 🛠 Tech Stack
- **Python** (pandas, numpy, scipy)
- **Plotly** (interactive visualizations)
- **Streamlit** (dashboard app)
- **Jupyter Notebooks** (data generation & analysis)
- **Render** (hosting)

---

## 📊 Dashboard Features
- **KPI Cards** — CTR, CPI, ROI, Retention (D7)
- **Funnel Chart** — Impressions → Clicks → Installs → Purchases
- **Installs Trend** — Daily installs over time (filtered)
- **Revenue by Campaign** — A vs B (global)
- **A/B Test Table** — CTR, Conversion, ROI, Retention with significance
- **Insights Panel** — Actionable recommendations for growth

---

## 📂 Project Structure

```plaintext
carrots-lab-analytics-project/
│
├── data/
│   └── mobile_funnel_data.csv       # Synthetic dataset
│
├── notebooks/
│   ├── 1_generate_data.ipynb        # Simulate raw mobile app data
│   └── 2_analysis_kpis_abtest.ipynb # Compute KPIs & A/B tests
│
├── app/
│   └── app.py                       # Streamlit dashboard application
│
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation