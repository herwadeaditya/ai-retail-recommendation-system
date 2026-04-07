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
# HEADER
# -------------------------
st.markdown("<h1 style='text-align: center;'>🛍️ AI Retail Recommendation System</h1>", unsafe_allow_html=True)

st.markdown("""
This system analyzes customer purchase patterns using **Apriori Algorithm**  
to suggest smart product combinations, demand insights, and pricing strategies.
""")

st.divider()

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("sales_data.csv")
combo_rules = pickle.load(open("model/combo_rules.pkl", "rb"))

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
            st.success("🔥 High Demand")
        elif qty >= max_sales * 0.4:
            st.warning("⚡ Medium Demand")
        else:
            st.info("💡 Low Demand")

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
# PRODUCT PERFORMANCE (FIXED)
# -------------------------
st.subheader("📊 Product Performance")

products_list = sales_data.index.tolist()

top_products = products_list[:3]
low_products = [p for p in products_list[-3:] if p not in top_products]

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
# COMBO SECTION (UPGRADED)
# -------------------------
st.subheader("🔥 Smart Combos")

st.markdown("### 💡 Why these combos?")
st.info("These products are frequently bought together based on historical transaction data using Apriori Algorithm.")

# Slider
top_n = st.slider("Select number of recommendations", 5, 20, 10)

valid_products = set(filtered['Product'].unique())

filtered_rules = combo_rules[
    combo_rules['antecedents'].apply(lambda x: set(x).issubset(valid_products)) &
    combo_rules['consequents'].apply(lambda x: set(x).issubset(valid_products))
]

if filtered_rules.empty:
    st.warning("No combos for this occasion")
else:
    rules = filtered_rules.sort_values(by="lift", ascending=False).head(top_n)

    for _, row in rules.iterrows():
        confidence = round(row['confidence'] * 100, 2)

        st.markdown(f"""
        🔹 **Buy {list(row['antecedents'])} → Get {list(row['consequents'])}**  
        📊 Lift: **{round(row['lift'], 2)}**  
        🎯 Confidence: **{confidence}%**  
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

st.markdown("""
**Aditya Herwade**  
📧 adityaherwade17@gmail.com  
🔗 GitHub: https://github.com/herwadeaditya  
🔗 LinkedIn: https://linkedin.com/in/adityaherwade  
""")