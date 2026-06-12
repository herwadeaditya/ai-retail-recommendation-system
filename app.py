# -*- coding: utf-8 -*-
"""
AI Retail Intelligence Platform - Enhanced Version
Developed by Aditya Herwade
"""

import streamlit as st
import pandas as pd
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import anthropic
import io

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="AI Retail Intelligence Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------
st.markdown("""
<style>

/* Base */
.main { background-color: #0f172a; }
[data-testid="stSidebar"] { background-color: #1e293b; }

/* Hero */
.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    padding: 30px 40px;
    border-radius: 16px;
    text-align: center;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(79,70,229,0.3);
}
.hero h1 { font-size: 2.2rem; margin: 0 0 8px 0; }
.hero p { font-size: 1rem; opacity: 0.85; margin: 0; }

/* KPI Cards */
.kpi-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-value { font-size: 2rem; font-weight: 700; color: #a78bfa; }
.kpi-label { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }

/* Recommendation Cards */
.rec-card {
    background: linear-gradient(135deg, #1e293b, #162032);
    border: 1px solid #334155;
    border-left: 4px solid #7c3aed;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.rec-title { color: #c4b5fd; font-weight: 600; font-size: 1rem; margin-bottom: 8px; }
.rec-meta { display: flex; gap: 16px; flex-wrap: wrap; }
.rec-badge {
    background: #1e1b4b;
    color: #a78bfa;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 500;
}
.rec-badge.lift { background: #052e16; color: #4ade80; }
.rec-badge.conf { background: #1e1b4b; color: #818cf8; }

/* Insight Cards */
.insight-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
}

/* Section Headers */
.section-header {
    color: #e2e8f0;
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid #334155;
}

/* Tab styling */
[data-testid="stTab"] { font-size: 0.9rem; }

/* Metric styling */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------
# DATA LOADING
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    df["Revenue"] = df["Quantity"] * df["Price"]
    # Parse date if column exists
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

@st.cache_resource
def load_rules():
    with open("combo_rules.pkl", "rb") as f:
        return pickle.load(f)

df = load_data()
combo_rules = load_rules()

has_dates = "Date" in df.columns and df["Date"].notna().any()


# -----------------------------------
# HERO
# -----------------------------------
st.markdown("""
<div class="hero">
    <h1>🛍️ AI Retail Intelligence Platform</h1>
    <p>Demand Analytics &nbsp;•&nbsp; Revenue Intelligence &nbsp;•&nbsp; Smart Recommendations &nbsp;•&nbsp; AI Insights</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------
st.sidebar.title("⚙️ Filters")
st.sidebar.markdown("---")

# Occasion filter
occasion = st.sidebar.selectbox(
    "🎉 Occasion",
    ["All"] + sorted(df["Occasion"].unique().tolist())
)

# Category filter
category_filter = st.sidebar.multiselect(
    "📦 Category",
    options=sorted(df["Category"].unique().tolist()),
    default=[]
)

# Product search
product_search = st.sidebar.text_input("🔍 Search Product", "")

# Date range
if has_dates:
    st.sidebar.markdown("---")
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Price range
st.sidebar.markdown("---")
min_price = float(df["Price"].min())
max_price = float(df["Price"].max())
price_range = st.sidebar.slider(
    "💲 Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

st.sidebar.markdown("---")
st.sidebar.markdown("**👨‍💻 Developed by Aditya Herwade**")
st.sidebar.markdown("[GitHub](https://github.com/herwadeaditya) • [LinkedIn](https://www.linkedin.com/in/aditya-herwade)")


# -----------------------------------
# APPLY FILTERS
# -----------------------------------
filtered = df.copy()

if occasion != "All":
    filtered = filtered[filtered["Occasion"] == occasion]

if category_filter:
    filtered = filtered[filtered["Category"].isin(category_filter)]

if product_search:
    filtered = filtered[filtered["Product"].str.contains(product_search, case=False, na=False)]

filtered = filtered[
    (filtered["Price"] >= price_range[0]) &
    (filtered["Price"] <= price_range[1])
]

if has_dates and len(date_range) == 2:
    filtered = filtered[
        (filtered["Date"].dt.date >= date_range[0]) &
        (filtered["Date"].dt.date <= date_range[1])
    ]

if filtered.empty:
    st.warning("⚠️ No data matches your current filters. Try adjusting the sidebar filters.")
    st.stop()


# -----------------------------------
# KPI SECTION
# -----------------------------------
total_products = filtered["Product"].nunique()
total_orders   = filtered["InvoiceNo"].nunique()
total_units    = int(filtered["Quantity"].sum())
total_revenue  = filtered["Revenue"].sum()
avg_order_val  = total_revenue / total_orders if total_orders else 0
top_category   = filtered.groupby("Category")["Revenue"].sum().idxmax()

col1, col2, col3, col4, col5, col6 = st.columns(6)

metrics = [
    ("🛒 Products",    f"{total_products:,}",       col1),
    ("📦 Orders",      f"{total_orders:,}",         col2),
    ("📈 Units Sold",  f"{total_units:,}",          col3),
    ("💰 Revenue",     f"₹{total_revenue:,.0f}",    col4),
    ("🧾 Avg Order",   f"₹{avg_order_val:,.0f}",   col5),
    ("🏅 Top Category", top_category,               col6),
]

for label, value, col in metrics:
    with col:
        st.metric(label, value)

st.divider()


# -----------------------------------
# MAIN TABS
# -----------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Demand",
    "💰 Revenue",
    "📦 Categories",
    "🧠 Recommendations",
    "🎯 Occasions",
    "🤖 AI Insights"
])


# =========================================================
# TAB 1: DEMAND
# =========================================================
with tab1:
    st.markdown('<div class="section-header">🔥 Product Demand Analysis</div>', unsafe_allow_html=True)

    sales = (
        filtered.groupby("Product")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    col_a, col_b = st.columns([2, 1])

    with col_a:
        top_n = st.slider("Show Top N Products", 5, min(50, len(sales)), 15, key="demand_topn")
        fig = px.bar(
            sales.head(top_n),
            x="Quantity", y="Product",
            orientation="h",
            title=f"Top {top_n} Products by Units Sold",
            template="plotly_dark",
            color="Quantity",
            color_continuous_scale="Purples"
        )
        fig.update_layout(
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            yaxis={"categoryorder": "total ascending"},
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("**📋 Top 10 Products**")
        st.dataframe(
            sales.head(10).rename(columns={"Quantity": "Units Sold"}),
            use_container_width=True,
            hide_index=True
        )

    # Time-series demand if dates available
    if has_dates and "Month" in filtered.columns:
        st.markdown("---")
        st.markdown("**📅 Monthly Demand Trend**")
        monthly = (
            filtered.groupby("Month")["Quantity"]
            .sum()
            .reset_index()
            .sort_values("Month")
        )
        fig2 = px.line(
            monthly, x="Month", y="Quantity",
            title="Units Sold by Month",
            template="plotly_dark",
            markers=True,
            line_shape="spline"
        )
        fig2.update_traces(line_color="#a78bfa", marker_color="#7c3aed")
        fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
        st.plotly_chart(fig2, use_container_width=True)

    # Price vs Quantity scatter
    st.markdown("---")
    st.markdown("**🔵 Price vs Demand (Bubble = Revenue)**")
    scatter_data = (
        filtered.groupby("Product")
        .agg(Quantity=("Quantity","sum"), Price=("Price","mean"), Revenue=("Revenue","sum"))
        .reset_index()
    )
    fig3 = px.scatter(
        scatter_data,
        x="Price", y="Quantity",
        size="Revenue", hover_name="Product",
        title="Price vs Quantity (bubble size = revenue)",
        template="plotly_dark",
        color="Revenue",
        color_continuous_scale="Purples"
    )
    fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
    st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# TAB 2: REVENUE
# =========================================================
with tab2:
    st.markdown('<div class="section-header">💰 Revenue Analysis</div>', unsafe_allow_html=True)

    revenue = (
        filtered.groupby("Product")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    col_a, col_b = st.columns([2, 1])

    with col_a:
        top_n_rev = st.slider("Show Top N Products", 5, min(50, len(revenue)), 15, key="rev_topn")
        fig = px.bar(
            revenue.head(top_n_rev),
            x="Revenue", y="Product",
            orientation="h",
            title=f"Top {top_n_rev} Products by Revenue",
            template="plotly_dark",
            color="Revenue",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        best_product = revenue.iloc[0]["Product"]
        best_rev     = revenue.iloc[0]["Revenue"]
        st.success(f"🏆 **Best Product:** {best_product}")
        st.info(f"💰 Revenue: ₹{best_rev:,.0f}")

        st.markdown("**📋 Revenue Table**")
        disp = revenue.head(10).copy()
        disp["Revenue"] = disp["Revenue"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

    # Monthly revenue trend
    if has_dates and "Month" in filtered.columns:
        st.markdown("---")
        st.markdown("**📅 Monthly Revenue Trend**")
        monthly_rev = (
            filtered.groupby("Month")["Revenue"]
            .sum()
            .reset_index()
            .sort_values("Month")
        )
        fig2 = px.area(
            monthly_rev, x="Month", y="Revenue",
            title="Revenue by Month",
            template="plotly_dark"
        )
        fig2.update_traces(fillcolor="rgba(124,58,237,0.2)", line_color="#7c3aed")
        fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
        st.plotly_chart(fig2, use_container_width=True)

    # Revenue heatmap by occasion x category
    st.markdown("---")
    st.markdown("**🗺️ Revenue Heatmap: Occasion × Category**")
    pivot = (
        filtered.groupby(["Occasion", "Category"])["Revenue"]
        .sum()
        .unstack(fill_value=0)
    )
    fig3 = px.imshow(
        pivot,
        title="Revenue Heatmap",
        template="plotly_dark",
        color_continuous_scale="Purples",
        aspect="auto"
    )
    fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
    st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# TAB 3: CATEGORIES
# =========================================================
with tab3:
    st.markdown('<div class="section-header">📦 Category Analytics</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        cat_rev = (
            filtered.groupby("Category")["Revenue"]
            .sum()
            .reset_index()
        )
        fig = px.pie(
            cat_rev, values="Revenue", names="Category",
            title="Category Revenue Share",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", font_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        cat_qty = (
            filtered.groupby("Category")["Quantity"]
            .sum()
            .reset_index()
        )
        fig2 = px.pie(
            cat_qty, values="Quantity", names="Category",
            title="Category Units Share",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", font_color="#e2e8f0")
        st.plotly_chart(fig2, use_container_width=True)

    # Category comparison bar
    st.markdown("---")
    cat_summary = (
        filtered.groupby("Category")
        .agg(Revenue=("Revenue","sum"), Units=("Quantity","sum"), Products=("Product","nunique"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name="Revenue (₹)", x=cat_summary["Category"],
        y=cat_summary["Revenue"], marker_color="#7c3aed"
    ))
    fig3.add_trace(go.Bar(
        name="Units Sold", x=cat_summary["Category"],
        y=cat_summary["Units"], marker_color="#06b6d4",
        yaxis="y2"
    ))
    fig3.update_layout(
        title="Category: Revenue vs Units",
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        yaxis=dict(title="Revenue (₹)"),
        yaxis2=dict(title="Units Sold", overlaying="y", side="right")
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("**📋 Category Summary Table**")
    cat_summary["Revenue"] = cat_summary["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(cat_summary, use_container_width=True, hide_index=True)


# =========================================================
# TAB 4: RECOMMENDATIONS
# =========================================================
with tab4:
    st.markdown('<div class="section-header">🧠 Smart Product Recommendations</div>', unsafe_allow_html=True)

    valid_products = set(filtered["Product"].unique())

    col_mode, _ = st.columns([2, 3])
    with col_mode:
        rec_mode = st.radio(
            "Recommendation Mode",
            ["🔮 Top Rules (auto)", "🎯 Product-specific"],
            horizontal=True
        )

    if rec_mode == "🎯 Product-specific":
        selected_product = st.selectbox(
            "Select a product to get recommendations:",
            sorted(valid_products)
        )
        filtered_rules = combo_rules[
            combo_rules["antecedents"].apply(
                lambda x: selected_product in x
            )
        ]
    else:
        filtered_rules = combo_rules[
            combo_rules["antecedents"].apply(
                lambda x: set(x).issubset(valid_products)
            )
        ]

    col_min_conf, col_min_lift, col_top_n = st.columns(3)
    with col_min_conf:
        min_conf = st.slider("Min Confidence %", 0, 100, 50, key="conf_slider") / 100
    with col_min_lift:
        min_lift = st.slider("Min Lift", 1.0, 10.0, 1.0, step=0.1, key="lift_slider")
    with col_top_n:
        top_n_rules = st.slider("Max Rules to Show", 3, 20, 10, key="rules_n")

    filtered_rules = filtered_rules[
        (filtered_rules["confidence"] >= min_conf) &
        (filtered_rules["lift"] >= min_lift)
    ]

    if filtered_rules.empty:
        st.warning("No rules match your filters. Try lowering confidence or lift thresholds.")
    else:
        rules = (
            filtered_rules
            .sort_values("lift", ascending=False)
            .head(top_n_rules)
        )

        st.markdown(f"**Showing {len(rules)} recommendation(s):**")

        for _, row in rules.iterrows():
            ants = ", ".join(list(row["antecedents"]))
            cons = ", ".join(list(row["consequents"]))
            conf_pct = round(row["confidence"] * 100, 1)
            lift_val = round(row["lift"], 2)
            supp_val = round(row["support"] * 100, 2) if "support" in row else None

            supp_badge = f'<span class="rec-badge">📊 Support: {supp_val}%</span>' if supp_val else ""

            st.markdown(f"""
<div class="rec-card">
    <div class="rec-title">🛒 Customers who buy <b>{ants}</b> also buy <b>{cons}</b></div>
    <div class="rec-meta">
        <span class="rec-badge conf">🎯 Confidence: {conf_pct}%</span>
        <span class="rec-badge lift">📈 Lift: {lift_val}</span>
        {supp_badge}
    </div>
</div>
""", unsafe_allow_html=True)

        # Rules scatter chart
        with st.expander("📊 View Rules Chart (Confidence vs Lift)"):
            chart_df = rules.copy()
            chart_df["antecedents_str"] = chart_df["antecedents"].apply(lambda x: ", ".join(list(x)))
            chart_df["consequents_str"] = chart_df["consequents"].apply(lambda x: ", ".join(list(x)))
            chart_df["label"] = chart_df["antecedents_str"] + " → " + chart_df["consequents_str"]
            fig = px.scatter(
                chart_df,
                x="confidence", y="lift",
                hover_name="label",
                size=[20]*len(chart_df),
                title="Rules: Confidence vs Lift",
                template="plotly_dark",
                color="lift",
                color_continuous_scale="Purples"
            )
            fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 View Full Rules Table"):
            disp_rules = rules[["antecedents","consequents","confidence","lift"]].copy()
            disp_rules["antecedents"] = disp_rules["antecedents"].apply(lambda x: ", ".join(list(x)))
            disp_rules["consequents"] = disp_rules["consequents"].apply(lambda x: ", ".join(list(x)))
            disp_rules["confidence"] = disp_rules["confidence"].apply(lambda x: f"{x*100:.1f}%")
            disp_rules["lift"] = disp_rules["lift"].apply(lambda x: f"{x:.2f}")
            st.dataframe(disp_rules, use_container_width=True, hide_index=True)


# =========================================================
# TAB 5: OCCASIONS
# =========================================================
with tab5:
    st.markdown('<div class="section-header">🎯 Occasion Insights</div>', unsafe_allow_html=True)

    occ_df = df.copy()  # always use full df for occasion overview

    occasion_summary = (
        occ_df.groupby("Occasion")
        .agg(Revenue=("Revenue","sum"), Units=("Quantity","sum"), Orders=("InvoiceNo","nunique"))
        .sort_values("Revenue", ascending=False)
        .reset_index()
    )

    col_a, col_b = st.columns(2)

    with col_a:
        fig = px.bar(
            occasion_summary,
            x="Occasion", y="Revenue",
            title="Revenue by Occasion",
            template="plotly_dark",
            color="Revenue",
            color_continuous_scale="Purples"
        )
        fig.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = px.bar(
            occasion_summary,
            x="Occasion", y="Units",
            title="Units Sold by Occasion",
            template="plotly_dark",
            color="Units",
            color_continuous_scale="Blues"
        )
        fig2.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a")
        st.plotly_chart(fig2, use_container_width=True)

    best_occ = occasion_summary.iloc[0]["Occasion"]
    best_occ_rev = occasion_summary.iloc[0]["Revenue"]
    st.success(f"🎉 **Highest Revenue Occasion:** {best_occ} — ₹{best_occ_rev:,.0f}")

    # Top products per occasion
    st.markdown("---")
    st.markdown("**🏆 Top Products per Occasion**")
    sel_occ = st.selectbox("Select Occasion to Explore", sorted(occ_df["Occasion"].unique()))
    occ_products = (
        occ_df[occ_df["Occasion"] == sel_occ]
        .groupby("Product")[["Quantity","Revenue"]]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(10)
        .reset_index()
    )
    occ_products["Revenue"] = occ_products["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    st.dataframe(occ_products, use_container_width=True, hide_index=True)

    # Occasion × Category heatmap
    st.markdown("---")
    st.markdown("**🗺️ Occasion × Category Performance**")
    occ_cat = (
        occ_df.groupby(["Occasion","Category"])["Revenue"]
        .sum()
        .unstack(fill_value=0)
    )
    fig3 = px.imshow(
        occ_cat,
        title="Occasion × Category Revenue Heatmap",
        template="plotly_dark",
        color_continuous_scale="Purples",
        aspect="auto",
        text_auto=".2s"
    )
    fig3.update_layout(paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", font_color="#e2e8f0")
    st.plotly_chart(fig3, use_container_width=True)


# =========================================================
# TAB 6: AI INSIGHTS
# =========================================================
with tab6:
    st.markdown('<div class="section-header">🤖 AI-Powered Business Insights</div>', unsafe_allow_html=True)

    # Pre-computed static insights
    revenue_by_prod = filtered.groupby("Product")["Revenue"].sum()
    best_product    = revenue_by_prod.idxmax()
    occ_revenue     = df.groupby("Occasion")["Revenue"].sum()
    best_occasion   = occ_revenue.idxmax()
    cat_revenue     = filtered.groupby("Category")["Revenue"].sum()
    best_category   = cat_revenue.idxmax()
    low_performers  = revenue_by_prod.sort_values().head(3).index.tolist()

    static_insights = [
        f"🏆 **Top Product:** {best_product} is your highest revenue driver — consider increasing its inventory and featuring it prominently.",
        f"🎉 **Best Occasion:** {best_occasion} generates the most revenue — plan targeted promotions and stock-ups ahead of this period.",
        f"📦 **Leading Category:** {best_category} leads in revenue contribution — explore adding more variants or bundling products within this category.",
        f"⚠️ **Low Performers:** {', '.join(low_performers)} have low revenue — review pricing, placement, or consider combo deals to move stock.",
        "💡 **Combo Strategy:** Use the Recommendations tab to build combo offers for high-lift product pairs — this can increase average order value significantly.",
        "📈 **Pricing Tip:** Products with high demand but low price may have room for a price increase; products with high price but low demand may benefit from a discount or bundle.",
    ]

    for insight in static_insights:
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💬 Ask Claude for Custom Insights")
    st.markdown("Describe what you want to know about your data and Claude will analyze it.")

    # Build data summary for Claude
    data_summary = f"""
Retail Sales Data Summary:
- Total Revenue: ₹{total_revenue:,.0f}
- Total Orders: {total_orders:,}
- Total Products: {total_products}
- Top Product by Revenue: {best_product} (₹{revenue_by_prod.max():,.0f})
- Best Occasion: {best_occasion} (₹{occ_revenue.max():,.0f})
- Best Category: {best_category} (₹{cat_revenue.max():,.0f})
- Low Revenue Products: {', '.join(low_performers)}
- Avg Order Value: ₹{avg_order_val:,.0f}
- Category Revenue Breakdown: {cat_revenue.to_dict()}
- Occasion Revenue Breakdown: {occ_revenue.to_dict()}
"""

    user_question = st.text_area(
        "Your question",
        placeholder="e.g. What combo offers should I run for the upcoming festive season? Which categories should I invest more in?",
        height=100
    )

    if st.button("🤖 Get AI Insights", type="primary"):
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Analyzing your data with Claude..."):
                try:
                    client = anthropic.Anthropic()
                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1000,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""You are an expert retail business analyst. 
Here is a summary of the retailer's sales data:

{data_summary}

Answer this question with specific, actionable insights (use bullet points where helpful):
{user_question}"""
                            }
                        ]
                    )
                    ai_answer = response.content[0].text
                    st.markdown("**Claude's Analysis:**")
                    st.markdown(f'<div class="insight-card">{ai_answer}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Could not connect to Claude API: {e}")
                    st.info("Make sure your ANTHROPIC_API_KEY environment variable is set.")

st.divider()


# -----------------------------------
# DOWNLOAD SECTION
# -----------------------------------
st.subheader("📥 Download Reports")

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    revenue_csv = (
        filtered.groupby("Product")["Revenue"]
        .sum()
        .reset_index()
        .to_csv(index=False)
        .encode()
    )
    st.download_button(
        "📊 Revenue Report (CSV)",
        revenue_csv,
        "revenue_report.csv",
        "text/csv"
    )

with col_d2:
    demand_csv = (
        filtered.groupby("Product")["Quantity"]
        .sum()
        .reset_index()
        .to_csv(index=False)
        .encode()
    )
    st.download_button(
        "📈 Demand Report (CSV)",
        demand_csv,
        "demand_report.csv",
        "text/csv"
    )

with col_d3:
    full_csv = filtered.to_csv(index=False).encode()
    st.download_button(
        "📋 Full Filtered Data (CSV)",
        full_csv,
        "filtered_data.csv",
        "text/csv"
    )

st.divider()

# -----------------------------------
# FOOTER
# -----------------------------------
st.markdown("""
<div style="text-align:center; color:#64748b; padding: 10px 0 20px 0; font-size:0.85rem;">
    👨‍💻 Developed by <b>Aditya Herwade</b> &nbsp;|&nbsp;
    📧 adityaherwade17@gmail.com &nbsp;|&nbsp;
    <a href="https://github.com/herwadeaditya" style="color:#7c3aed;">GitHub</a> &nbsp;|&nbsp;
    <a href="https://www.linkedin.com/in/aditya-herwade" style="color:#7c3aed;">LinkedIn</a>
</div>
""", unsafe_allow_html=True)# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 17:15:41 2026

@author: ADITYA
"""

import streamlit as st
import pandas as pd
import pickle
import warnings

warnings.filterwarnings("ignore")


# PAGE CONFIG

st.set_page_config(page_title="AI Retail System", layout="wide")


# HEADER

st.markdown("<h1 style='text-align: center;'>🛍️ AI Retail Recommendation System</h1>", unsafe_allow_html=True)

st.markdown("""
This system analyzes customer purchase patterns using **Apriori Algorithm**  
to suggest smart product combinations, demand insights, and pricing strategies.
""")

st.divider()


# LOAD DATA

df = pd.read_csv("sales_data.csv")
combo_rules = pickle.load(open("model/combo_rules.pkl", "rb"))


# KPI CARDS

col1, col2, col3 = st.columns(3)

col1.metric("🛒 Products", len(df['Product'].unique()))
col2.metric("📦 Orders", df['InvoiceNo'].nunique())
col3.metric("💰 Total Sales", int(df['Quantity'].sum()))

st.divider()


# OCCASION SELECT

occasion = st.selectbox("🎯 Select Occasion", ["All"] + list(df['Occasion'].unique()))

filtered = df if occasion == "All" else df[df['Occasion'] == occasion]

if filtered.empty:
    st.warning("No data available")
    st.stop()


# SALES OVERVIEW

st.subheader("📊 Sales Overview")

sales_data = filtered.groupby('Product')['Quantity'].sum().sort_values(ascending=False)
st.bar_chart(sales_data)

st.divider()


# DEMAND INSIGHTS

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


# REVENUE INSIGHT

st.subheader("💰 Revenue Insight")

filtered['Revenue'] = filtered['Quantity'] * filtered['Price']
revenue_data = filtered.groupby('Product')['Revenue'].sum().sort_values(ascending=False)

st.bar_chart(revenue_data)

top_revenue = revenue_data.idxmax()
st.success(f"💸 Highest revenue product: {top_revenue}")

st.divider()


# ORDER INSIGHT

st.subheader("📦 Order Insights")

avg_order = filtered.groupby('InvoiceNo')['Quantity'].sum().mean()
st.metric("Avg Items per Order", int(avg_order))

st.divider()


# PRODUCT PERFORMANCE (FIXED)

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


# ACTION RECOMMENDATIONS

st.subheader("🎯 Action Recommendations")

st.success(f"🔥 Focus on: {', '.join(top_products)}")
st.write("📦 Bundle these products to increase sales")

st.divider()


# COMBO SECTION (UPGRADED)

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


# PRICING STRATEGY
 
st.subheader("💸 Pricing Strategy")

if max_sales > 20:
    st.success("🔥 High demand → Low discount (5–10%)")
else:
    st.warning("⚡ Moderate demand → Use combo offers")

st.info("💡 Bundle items to increase cart value")

st.divider()


# BUSINESS DECISIONS

st.subheader("🧠 Business Decisions")

st.write("➡ Increase stock for high-demand products")
st.write("➡ Promote combo offers")
st.write("➡ Optimize pricing strategy")

st.divider()


# FINAL INSIGHT

st.subheader("📊 Business Insight")

st.info(f"""
For **{occasion}**, focus on high-demand products,  
bundle them strategically, and optimize pricing  
to maximize revenue.
""")

st.markdown("### 👨‍💻 Developed by")

st.markdown("""
**Aditya Herwade**  

📧 [adityaherwade17@gmail.com](mailto:adityaherwade17@gmail.com)  

🔗 [GitHub](https://github.com/herwadeaditya)  

🔗 [LinkedIn](https://www.linkedin.com/in/aditya-herwade)  
""")
