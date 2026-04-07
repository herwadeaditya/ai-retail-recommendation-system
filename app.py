# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 17:15:41 2026

@author: ADITYA
"""

import streamlit as st
import pandas as pd
import pickle
import warnings

warnings.filterwarnings("ignore")

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Retail System", layout="wide")

# -------------------------
# STYLE
# -------------------------
st.markdown("""
<style>
    .stMetric {text-align: center;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("sales_data.csv")
combo_rules = pickle.load(open("model/combo_rules.pkl", "rb"))

# -------------------------
# HEADER
# -------------------------
st.markdown("<h1 style='text-align: center;'>🛍️ AI Retail Recommendation System</h1>", unsafe_allow_html=True)

# -------------------------
# KPI CARDS
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("🛒 Products", len(df['Product'].unique()))
col2.metric("📦 Orders", df['InvoiceNo'].nunique())
col3.metric("💰 Total Sales", int(df['Quantity'].sum()))

st.divider()

# -------------------------
# OCCASION SELECT
# -------------------------
occasion = st.selectbox("🎯 Select Occasion", ["All"] + list(df['Occasion'].unique()))

filtered = df if occasion == "All" else df[df['Occasion'] == occasion]

if filtered.empty:
    st.warning("No data available")
    st.stop()

# -------------------------
# SALES OVERVIEW
# -------------------------
st.subheader("📊 Sales Overview")

sales_data = filtered.groupby('Product')['Quantity'].sum().sort_values(ascending=False)
st.bar_chart(sales_data)

st.divider()

# -------------------------
# DEMAND INSIGHTS
# -------------------------
st.subheader("🔮 Demand Insights")

max_sales = sales_data.max()

for product, qty in sales_data.items():
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### 🛍️ {product}")
        st.write(f"Sales: **{qty}**")

    with col2:
        if qty >= max_sales * 0.7:
            st.success("🔥 High")
        elif qty >= max_sales * 0.4:
            st.warning("⚡ Medium")
        else:
            st.info("💡 Low")

st.divider()

# -------------------------
# REVENUE INSIGHT
# -------------------------
st.subheader("💰 Revenue Insight")

filtered['Revenue'] = filtered['Quantity'] * filtered['Price']
revenue_data = filtered.groupby('Product')['Revenue'].sum().sort_values(ascending=False)

st.bar_chart(revenue_data)

top_revenue = revenue_data.idxmax()
st.success(f"💸 Highest revenue product: {top_revenue}")

st.divider()

# -------------------------
# ORDER INSIGHT
# -------------------------
st.subheader("📦 Order Insights")

avg_order = filtered.groupby('InvoiceNo')['Quantity'].sum().mean()
st.metric("Avg Items per Order", int(avg_order))

st.divider()

# -------------------------
# ✅ FIXED PRODUCT PERFORMANCE
# -------------------------
st.subheader("📊 Product Performance")

products_list = sales_data.index.tolist()

# Top products
top_products = products_list[:3]

# Low products (remove overlap)
low_products = products_list[-3:]
low_products = [p for p in low_products if p not in top_products]

top_df = sales_data.loc[top_products]
low_df = sales_data.loc[low_products]

col1, col2 = st.columns(2)

with col1:
    st.write("🔥 Top Products")
    st.dataframe(top_df)

with col2:
    st.write("⚠ Low Products")
    if len(low_df) == 0:
        st.info("No low-performing products")
    else:
        st.dataframe(low_df)

st.divider()

# -------------------------
# ACTION RECOMMENDATIONS
# -------------------------
st.subheader("🎯 Action Recommendations")

st.success(f"🔥 Focus on: {', '.join(top_products)}")
st.write("📦 Bundle these products to increase sales")

st.divider()

# -------------------------
# COMBO RECOMMENDATIONS
# -------------------------
st.subheader("🔥 Smart Combos")

valid_products = set(filtered['Product'].unique())

filtered_rules = combo_rules[
    combo_rules['antecedents'].apply(lambda x: set(x).issubset(valid_products)) &
    combo_rules['consequents'].apply(lambda x: set(x).issubset(valid_products))
]

if filtered_rules.empty:
    st.warning("No combos for this occasion")
else:
    rules = filtered_rules.sort_values(by="lift", ascending=False).head(5)

    for _, row in rules.iterrows():
        st.markdown(f"""
        🔹 **Buy {list(row['antecedents'])} → Get {list(row['consequents'])}**  
        📊 Lift: {round(row['lift'], 2)}  
        💡 Customers frequently buy these together  
        """)

st.divider()

# -------------------------
# PRICING STRATEGY
# -------------------------
st.subheader("💸 Pricing Strategy")

if max_sales > 20:
    st.success("🔥 High demand → Low discount (5–10%)")
else:
    st.warning("⚡ Moderate demand → Use combo offers")

st.info("💡 Bundle items to increase cart value")

st.divider()

# -------------------------
# BUSINESS DECISIONS
# -------------------------
st.subheader("🧠 Business Decisions")

st.write("➡ Increase stock for high-demand products")
st.write("➡ Promote combo offers")
st.write("➡ Optimize pricing strategy")

st.divider()

# -------------------------
# FINAL INSIGHT
# -------------------------
st.subheader("📊 Business Insight")

st.info(f"""
For **{occasion}**, focus on high-demand products,  
bundle them strategically, and optimize pricing  
to maximize revenue.
""")    