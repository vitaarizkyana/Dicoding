import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# Impor dataset
hour_df = pd.read_csv("https://raw.githubusercontent.com/vitaarizkyana/Dicoding/main/dashboard/hour_cleaned.csv")
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

st.set_page_config(page_title="Bike Sharing Dashboard",
                   layout="wide")


# Membuat fungsi untuk pengelompokkan berdasarkan musim, bulan, dan hari
def create_seasonly_usage_df(hour_df):
    seasonly_usage_df = hour_df.groupby("season").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })

    seasonly_usage_df = seasonly_usage_df.reset_index()
    seasonly_usage_df.rename(columns={
        "cnt": "total_rental_bikes",
        "casual": "casual_users",
        "registered": "registered_users"
    }, inplace=True)
    
    seasonly_usage_df = pd.melt(seasonly_usage_df,
                                      id_vars=['season'],
                                      value_vars=['casual_users', 'registered_users'],
                                      var_name='users',
                                      value_name='count_rides')
    
    seasonly_usage_df['season'] = pd.Categorical(seasonly_usage_df['season'],
                                             categories=['Spring', 'Summer', 'Fall', 'Winter'])
    
    seasonly_usage_df = seasonly_usage_df.sort_values('season')
    return seasonly_usage_df


def create_monthly_usage_df(hour_df):
    monthly_usage_df = hour_df.resample(rule='M', on='dteday').agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })

    monthly_usage_df.index = monthly_usage_df.index.strftime('%b-%y')
    monthly_usage_df = monthly_usage_df.reset_index()
    monthly_usage_df.rename(columns={
        "dteday": "yearmonth",
        "cnt": "total_rental_bikes",
        "casual": "casual_users",
        "registered": "registered_users"
    }, inplace=True)
    
    return monthly_usage_df


def create_weekday_usage_df(hour_df):
    weekday_usage_df = hour_df.groupby("weekday").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    })
    weekday_usage_df = weekday_usage_df.reset_index()
    weekday_usage_df.rename(columns={
        "cnt": "total_rental_bikes",
        "casual": "casual_users",
        "registered": "registered_users"
    }, inplace=True)
    
    weekday_usage_df = pd.melt(weekday_usage_df,
                                      id_vars=['weekday'],
                                      value_vars=['casual_users', 'registered_users'],
                                      var_name='users',
                                      value_name='count_rides')
    
    weekday_usage_df['weekday'] = pd.Categorical(weekday_usage_df['weekday'],
                                             categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    weekday_usage_df = weekday_usage_df.sort_values('weekday')
    return weekday_usage_df


# Membuat filter tanggal paling awal dan akhir dari kolom "dteday"
start_date = hour_df["dteday"].min()
end_date = hour_df["dteday"].max()


# ----- SIDEBAR -----
with st.sidebar:
    
    # Memunculkan fitur filter pada sidebar
    st.sidebar.header("Filter:")

    # Mengambil tanggal paling awal dan akhir dari kolom "dteday"
    min_date, max_date = st.date_input(
        label="Time Period", min_value=start_date,
        max_value=end_date,
        value=[start_date, end_date]
    )


# Menghubungkan filter dengan data dteday
date_day = hour_df[
    (hour_df["dteday"] >= str(min_date)) &
    (hour_df["dteday"] <= str(max_date))
]

# Assign date_day ke fungsi yang telah dibuat di awal
seasonly_usage_df = create_seasonly_usage_df(date_day)
monthly_usage_df = create_monthly_usage_df(date_day)
weekday_usage_df = create_weekday_usage_df(date_day)



# ----- MAINPAGE -----
st.title("Bike-Sharing Dashboard")
st.markdown("##")

col1, col2, col3 = st.columns(3)
with col1:
    total_rental_bikes = date_day['cnt'].sum()
    st.metric("Total Rental Bikes", value=total_rental_bikes)
with col2:
    total_casual_users = date_day['casual'].sum()
    st.metric("Total Casual Users", value=total_casual_users)
with col3:
    total_registered_users = date_day['registered'].sum()
    st.metric("Total Registered Users", value=total_registered_users)
st.markdown("---")


# ----- CHART -----
fig1 = px.bar(seasonly_usage_df,
              x='season',
              y=['count_rides'],
              color='users',
              color_discrete_sequence=["lavender", "mediumpurple", "olive"],
              title='Jumlah Sewa Sepeda per Musim').update_layout(xaxis_title='', yaxis_title='Total Rental Bikes')
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(monthly_usage_df,
              x='yearmonth',
              y=['casual_users', 'registered_users', 'total_rental_bikes'],
              color_discrete_sequence=["mediumorchid", "olive", "turquoise"],
              markers=True,
              title="Jumlah Sewa Sepeda per Bulan").update_layout(xaxis_title='', yaxis_title='Total Rental Bikes')
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(weekday_usage_df,
              x='weekday',
              y=['count_rides'],
              color='users',
              barmode='group',
              color_discrete_sequence=["sandybrown", "burlywood", "turquoise"],
              title='Jumlah Sewa Sepeda per Hari').update_layout(xaxis_title='', yaxis_title='Total Rental Bikes')
st.plotly_chart(fig3, use_container_width=True)


# ----- HIDE STREAMLIT STYLE -----
hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)