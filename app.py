# app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv"
    df = pd.read_csv(url, parse_dates=["Date"])
    df["Country"] = df["Country"].astype("category")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔎 Filter Options")
country = st.sidebar.selectbox("Select Country", df["Country"].unique())
start_date = st.sidebar.date_input("Start Date", df["Date"].min().date())
end_date = st.sidebar.date_input("End Date", df["Date"].max().date())
# Filter data
df_filtered = df[(df["Country"] == country) &
                 (df["Date"].dt.date >= start_date) &
                 (df["Date"].dt.date <= end_date)]

st.download_button(
    label="📥 Download filtered data as CSV",
    data=df_filtered.to_csv(index=False).encode('utf-8'),
    file_name='covid_filtered_data.csv',
    mime='text/csv'
)

# Derived features
df_filtered["Active"] = df_filtered["Confirmed"] - df_filtered["Recovered"] - df_filtered["Deaths"]
df_filtered["DailyConfirmed"] = df_filtered["Confirmed"].diff().fillna(0)
df_filtered["GrowthRate"] = df_filtered["Confirmed"].pct_change().fillna(0)
df_filtered["MA7_Confirmed"] = df_filtered["Confirmed"].rolling(7).mean()

# Dashboard title
st.title("🌍 COVID-19 EDA Dashboard")
st.write(f"### Data for {country}")
st.dataframe(df_filtered.head())
st.write(f"### Showing data from {start_date} to {end_date}")

# Time series chart
st.subheader("📈 Confirmed Cases Over Time")
fig1 = px.line(df_filtered, x="Date", y="Confirmed", title="Confirmed Cases")
# --- Section: Top 10 Countries by Confirmed Cases ---
st.markdown("## 🔢 Top 10 Countries by Confirmed Cases")

# Get the latest date in the dataset
latest_date = df["Date"].max()

# Filter data for the latest date
df_latest = df[df["Date"] == latest_date]

# Get top 10 countries by confirmed cases
df_top10 = df_latest.sort_values(by="Confirmed", ascending=False).head(10)

# Create the bar chart
fig_top10 = px.bar(
    df_top10,
    x="Country",
    y="Confirmed",
    title=f"Top 10 Countries by Confirmed Cases on {latest_date.date()}",
    color="Confirmed",
    color_continuous_scale="Reds"
)

# Display the chart
st.plotly_chart(fig1, use_container_width=True)

# Daily confirmed histogram
st.subheader("📊 Daily Confirmed Case Distribution")
fig2 = px.histogram(df_filtered, x="DailyConfirmed", nbins=50)
st.plotly_chart(fig2, use_container_width=True)

# Correlation heatmap
st.subheader("🔗 Correlation Matrix")
corr = df_filtered[["Confirmed", "Deaths", "Recovered", "Active"]].corr()
fig3 = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
st.plotly_chart(fig3, use_container_width=True)


#interactive dashboard with multiple visualizations
# --- Section: Time Series with Range Selector ---
st.markdown("## 📈 Time Series with Range Selector")
fig_ts = px.line(df_filtered, x="Date", y="Confirmed", title="Confirmed Cases Over Time")
fig_ts.update_xaxes(rangeslider_visible=True)
st.plotly_chart(fig_ts, use_container_width=True)

# --- Section: Global Map of Confirmed Cases ---
st.markdown("## 🗺️ Global Map of Confirmed Cases")
latest_date = df["Date"].max()
df_latest = df[df["Date"] == latest_date]
fig_map = px.choropleth(df_latest, locations="Country", locationmode="country names",
                        color="Confirmed", title=f"Confirmed Cases on {latest_date.date()}",
                        color_continuous_scale="Reds")
st.plotly_chart(fig_map, use_container_width=True)

# --- Section: Country Comparison Mode ---
st.markdown("## 📌 Confirmed Cases Comparison Across Countries")

# Sidebar multiselect for comparison
selected_countries = st.sidebar.multiselect(
    "Compare Countries",
    df["Country"].unique(),
    default=[country]
)

# Filter data for selected countries and date range
df_compare = df[
    (df["Country"].isin(selected_countries)) &
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
]

# Plot comparison chart
fig_compare = px.line(
    df_compare,
    x="Date",
    y="Confirmed",
    color="Country",
    title="Confirmed Cases Over Time"
)
st.plotly_chart(fig_compare, use_container_width=True)

# --- Section: Growth Rate & Moving Average Trends ---
st.markdown("## 📈 Growth Rate & Moving Average Trends")

# 7-Day Moving Average Chart
st.subheader("📊 7-Day Moving Average of Confirmed Cases")
fig_ma = px.line(
    df_filtered,
    x="Date",
    y="MA7_Confirmed",
    title="7-Day Moving Average of Confirmed Cases"
)
st.plotly_chart(fig_ma, use_container_width=True)

# Daily Growth Rate Chart
st.subheader("📊 Daily Growth Rate of Confirmed Cases")
fig_growth = px.line(
    df_filtered,
    x="Date",
    y="GrowthRate",
    title="Daily Growth Rate (%)"
)
st.plotly_chart(fig_growth, use_container_width=True)

# --- Section: Correlation Heatmap (already added in Step 1) ---
st.markdown("## 🔗 Correlation Matrix")
fig_corr = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
fig_corr.update_layout(margin=dict(l=40, r=40, t=40, b=40))
st.plotly_chart(fig_corr, use_container_width=True)

# --- Section: Scatter Plot with Hover Info ---
st.markdown("## 📌 Daily Cases vs Growth Rate")
fig_scatter = px.scatter(df_filtered, x="DailyConfirmed", y="GrowthRate",
                         hover_data=["Date"], title="Daily Cases vs Growth Rate")
st.plotly_chart(fig_scatter, use_container_width=True)




