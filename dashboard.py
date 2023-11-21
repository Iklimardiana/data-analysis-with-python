import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# menyiapkan dataframe dengan membuat beberapa helper function
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_customer_bycity_df(df):
    customer_bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    customer_bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return customer_bycity_df

def create_seller_bycity_df(df):
    seller_bycity_df = df.groupby(by="seller_city").seller_id.nunique().reset_index()
    seller_bycity_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    
    return seller_bycity_df

def create_sum_order_items_df(df):
    sum_order_item_df = df.groupby(by="product_category_name_english")["product_id"].count().reset_index()
    sum_order_item_df.rename(columns={
        "product_id": "total_orders"
    }, inplace=True)
    
    sum_order_item_df = sum_order_item_df.sort_values(by='total_orders', ascending=False)
    
    return sum_order_item_df

def create_rating_items_df(df):
    rating_item_df = df.groupby('product_category_name_english')['review_score'].mean().round(1).reset_index()
    
    rating_item_df = rating_item_df.sort_values(by='review_score', ascending=True)
    
    return rating_item_df

def create_payment_type_df(df):
    payment_type_df = df.groupby('payment_type').order_id.nunique().reset_index()
    payment_type_df = payment_type_df.sort_values(by='order_id', ascending=True)
    
    return payment_type_df


# load berkas all_data.csv
all_df = pd.read_csv("data/all_data.csv")

# Mengubah kolom menjadi tipe data datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image('asset/logo.png')
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
# start_date dan end_date akan digunakan untuk memfilter all_df yang selanjutnya akan disimpan pada main_df
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(main_df)
customer_bycity_df = create_customer_bycity_df(main_df)
seller_bycity_df = create_seller_bycity_df(main_df)
sum_order_item_df = create_sum_order_items_df (main_df)
rating_item_df = create_rating_items_df(main_df)
payment_type_trend = create_payment_type_df(main_df)


st.header('E-Commerce Dashboard :sparkles:')


# PEMESANAN HARIAN
st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
plt.title("Daily Orders", loc="center", fontsize=25)
 
st.pyplot(fig)


# CUSTOMER TERBANYAK BERDASARKAN KOTA

st.subheader("\nNumber of Customers by City")
 
fig, ax = plt.subplots(figsize=(10, 5))

colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="customer_city",
    data=customer_bycity_df.sort_values(by="customer_count", ascending=False).head(5),
    palette=colors_
)

plt.title("Number of Customers by City", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)

st.pyplot(fig)


# SELLER TERBANYAK BERDASARKAN KOTA

st.subheader("\nNumber of Sellers by City")
 
fig, ax = plt.subplots(figsize=(10, 5))

colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="seller_count", 
    y="seller_city",
    data=seller_bycity_df.sort_values(by="seller_count", ascending=False).head(5),
    palette=colors_
)

plt.title("Number of Sellers by City", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)

st.pyplot(fig)


# PRODUK PALING BANYAK DAN SEDIKIT TERJUAL

st.subheader("\nBest & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="total_orders", y="product_category_name_english", data=sum_order_item_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Products", loc="center", fontsize=40)
ax[0].tick_params(axis ='y', labelsize=30)
ax[0].tick_params(axis ='x', labelsize=25)

sns.barplot(x="total_orders", y="product_category_name_english", data=sum_order_item_df.sort_values(by="total_orders", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Products", loc="center", fontsize=40)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis ='x', labelsize=25)
 
st.pyplot(fig)

# PRODUK DENGAN RATING TERENDAH
st.subheader("\nWorst Rating Product")

fig, ax = plt.subplots(figsize=(10, 5))

colors2 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]

sns.barplot(
    y="product_category_name_english",
    x="review_score",
    data=rating_item_df.sort_values(by="review_score", ascending=False).tail(5),
    palette=colors2
)
plt.title("Worst Rating Product", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)

st.pyplot(fig)

# TIPE PEMBAYARAN
st.subheader("\nPayment Type Trend")

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    y="order_id",
    x="payment_type",
    data=payment_type_trend.sort_values(by="order_id", ascending=False),
    palette=colors
)
plt.title("Payment Type Trend", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)

st.pyplot(fig)


