# 📱 Mobile App Analytics Dashboard – Carrots Lab Internship Project

A simulated end-to-end **mobile app product analytics** project demonstrating skills in **ETL, KPI tracking, dashboarding, and A/B testing** — aligned with the Product Analyst Intern role at Carrots Lab.

---

## 🚀 Overview
This project showcases the process of:
- Generating **mobile app campaign data** (synthetic, CSV).
- Cleaning, transforming, and enriching it in Python.
- Calculating **core mobile app metrics**:
  - **DAU (Daily Active Users)**
  - **MAU (Monthly Active Users)**
  - **DAU/MAU Stickiness Ratio**
  - CTR, CPI, ROI, LTV, Conversion Rate
  - Day-7 Retention
- Conducting **A/B testing** between campaigns.
- Visualising insights in an **interactive Streamlit dashboard**.
- Providing **strategic recommendations** based on data.

---

## 🛠 Tech Stack
- **Python** (pandas, numpy, matplotlib, plotly, scipy)
- **Streamlit** – interactive web app
- **Jupyter Notebooks** – data generation & KPI analysis
- **Render** – dashboard hosting
- **Git** – version control

---

## 📊 Features
### 1. **KPI Tracking**
- DAU & MAU with monthly stickiness ratio
- CTR, CPI, ROI, LTV, Conversion
- Retention metrics

### 2. **Funnels & Trends**
- Acquisition funnel (Impressions → Clicks → Installs → Purchases)
- Daily installs trend
- Revenue by campaign

### 3. **Engagement & Retention**
- DAU/MAU Stickiness charts
- Day-7 Retention rates by campaign

### 4. **A/B Testing**
- Statistical tests (t-test) for CTR, Conversion, ROI, Retention between campaigns
- Significance flagging

### 5. **Insights Panel**
- Actionable recommendations for budget allocation, re-engagement, and segmentation.

---

## 📂 Project Structure
CarrotsLab_Project/
│
├── data/
│   └── mobile_funnel_data.csv     # synthetic dataset
│
├── notebooks/
│   ├── 1_generate_data.ipynb      # simulate raw data
│   ├── 2_analysis_kpis_abtest.ipynb # compute KPIs & tests
│
├── app/
│   └── app.py                     # Streamlit dashboard
│
├── requirements.txt
└── README.md
