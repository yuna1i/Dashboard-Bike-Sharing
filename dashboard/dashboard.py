import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Define mappings for categorical conversion
season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
holiday_map = {0: 'Non-holiday', 1: 'Holiday'}
weekday_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 
               4: 'Thursday', 5: 'Friday', 6: 'Saturday'}

# Load data
all_df = pd.read_csv("https://raw.githubusercontent.com/yuna1i/Dashboard-Bike-Sharing/refs/heads/main/dashboard/all_data.csv")

# Convert datetime column
datetime_columns = ["dteday_x"]
all_df.sort_values(by="dteday_x", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Apply the mappings to convert numeric columns to categorical labels
all_df['season_x'] = all_df['season_x'].map(season_map)
all_df['holiday_x'] = all_df['holiday_x'].map(holiday_map)
all_df['weekday_x'] = all_df['weekday_x'].map(weekday_map)

min_date = all_df["dteday_x"].min()
max_date = all_df["dteday_x"].max()

# Streamlit sidebar for date selection
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

main_df = all_df[(all_df["dteday_x"] >= str(start_date)) & (all_df["dteday_x"] <= str(end_date))]

# Define functions to create aggregated DataFrames
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday_x').agg({
        "instant": "nunique",
        "cnt_y": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "instant": "order_count",
        "cnt_y": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season_x").instant.nunique().reset_index()
    byseason_df.rename(columns={"instant": "customer_count"}, inplace=True)
    return byseason_df

def create_byholiday_df(df):
    byholiday_df = df.groupby(by="holiday_x").instant.nunique().reset_index()
    byholiday_df.rename(columns={"instant": "customer_count"}, inplace=True)
    return byholiday_df

def create_byweekday_df(df):
    byweekday_df = df.groupby(by="weekday_x").instant.nunique().reset_index()
    byweekday_df.rename(columns={"instant": "customer_count"}, inplace=True)
    return byweekday_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "instant": "nunique",
        "cnt_y": "sum"
    })
    rfm_df.columns = ["instant", "monetary"]
    rfm_df["frequency"] = df.groupby("instant").size().values
    rfm_df.drop("instant", axis=1, inplace=True)
    return rfm_df

# Create data frames for analysis
daily_orders_df = create_daily_orders_df(main_df)
byseason_df = create_byseason_df(main_df)
byholiday_df = create_byholiday_df(main_df)
byweekday_df = create_byweekday_df(main_df)
rfm_df = create_rfm_df(main_df)

# Streamlit layout for visualizations
st.header('Dicoding Bikes Dashboard :sparkles:')

# Customer Demographics section
st.subheader("Customer Demographics")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y="customer_count",
        x="season_x",
        data=byseason_df.sort_values(by="customer_count", ascending=False),
        palette="Blues_d",
        ax=ax
    )
    ax.set_title("Number of Customers by Season", fontsize=50)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y="customer_count",
        x="holiday_x",
        data=byholiday_df.sort_values(by="customer_count", ascending=False),
        palette="Blues_d",
        ax=ax
    )
    ax.set_title("Number of Customers by Holiday", fontsize=50)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="weekday_x",
    y="customer_count",
    data=byweekday_df.sort_values(by="customer_count", ascending=False),
    palette="Blues_d",
    ax=ax
)
ax.set_title("Number of Customers by Weekday", fontsize=30)
st.pyplot(fig)

# RFM analysis section
col1, col2, col3 = st.columns(3)

with col1:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col2:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='en_AU')
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9"]

sns.barplot(y="frequency", x="frequency", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Frequency", fontsize=30)
ax[0].set_title("By Frequency", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="monetary", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Monetary", fontsize=30)
ax[1].set_title("By Monetary", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

