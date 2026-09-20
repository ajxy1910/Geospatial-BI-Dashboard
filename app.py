import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Retail & Geospatial BI Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    sales = pd.read_csv(DATA_DIR / "Sales.csv")

    sku = pd.read_csv(DATA_DIR / "SKU MASTER.csv")

    opening_stock = pd.read_csv(
        DATA_DIR / "Opening Stock.csv",
        header=None
    )

    stock_transfer = pd.read_csv(
        DATA_DIR / "STOCK TRANSFER.csv",
        header=None
    )

    census = pd.read_csv(DATA_DIR / "census2011.csv")

    districts = pd.read_csv(
        DATA_DIR / "maharashtra-districts.csv"
    )

    msme = pd.read_csv(
        DATA_DIR / "district_level_total_Registered_msme.csv"
    )

    return (
        sales,
        sku,
        opening_stock,
        stock_transfer,
        census,
        districts,
        msme
    )


# ============================================================
# LOAD
# ============================================================

try:

    (
        sales,
        sku,
        opening_stock,
        stock_transfer,
        census,
        districts,
        msme
    ) = load_data()

except Exception as e:

    st.error("❌ Data loading error")

    st.code(str(e))

    st.info(
        "Check that all CSV files are inside the 'data' folder."
    )

    st.stop()


# ============================================================
# CLEAN SALES DATA
# ============================================================

sales["Date"] = pd.to_datetime(
    sales["Date"],
    errors="coerce"
)

sales["Sales"] = pd.to_numeric(
    sales["Sales"],
    errors="coerce"
).fillna(0)


# ============================================================
# CLEAN SKU MASTER
# ============================================================

sku.columns = [
    str(col).strip()
    for col in sku.columns
]

sku["Category"] = (
    sku["Category"]
    .astype(str)
    .str.strip()
)

sku["Description"] = (
    sku["Description"]
    .astype(str)
    .str.strip()
)

sku["Price"] = pd.to_numeric(
    sku["Price"],
    errors="coerce"
).fillna(0)


# ============================================================
# MERGE SALES + SKU
# ============================================================

sales = sales.merge(
    sku[["SKU", "Category", "Price"]],
    on="SKU",
    how="left"
)


# ============================================================
# CALCULATE REVENUE
# ============================================================

sales["Revenue"] = (
    sales["Sales"] *
    sales["Price"]
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎛️ Dashboard Filters")

st.sidebar.markdown("---")


# City filter

cities = sorted(
    sales["City"]
    .dropna()
    .unique()
    .tolist()
)

selected_cities = st.sidebar.multiselect(
    "Select City",
    cities,
    default=cities
)


# Category filter

categories = sorted(
    sales["Category"]
    .dropna()
    .unique()
    .tolist()
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    categories,
    default=categories
)


# Date filter

min_date = sales["Date"].min().date()
max_date = sales["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_sales = sales[
    sales["City"].isin(selected_cities)
    &
    sales["Category"].isin(selected_categories)
].copy()


if len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered_sales = filtered_sales[
        (filtered_sales["Date"] >= start_date)
        &
        (filtered_sales["Date"] <= end_date)
    ]


# ============================================================
# HEADER
# ============================================================

st.title("📊 Retail & Geospatial Business Intelligence Dashboard")

st.markdown(
    """
    **Retail Sales • Inventory • Business • Maharashtra Geospatial Analysis**
    """
)

st.markdown("---")


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_units = filtered_sales["Sales"].sum()

total_revenue = filtered_sales["Revenue"].sum()

total_products = filtered_sales["SKU"].nunique()

total_cities = filtered_sales["City"].nunique()


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🛒 Total Units Sold",
        f"{total_units:,.0f}"
    )


with col2:

    st.metric(
        "💰 Total Revenue",
        f"₹{total_revenue:,.0f}"
    )


with col3:

    st.metric(
        "📦 Products",
        total_products
    )


with col4:

    st.metric(
        "🏙️ Cities",
        total_cities
    )


st.markdown("---")


# ============================================================
# SALES TREND
# ============================================================

st.subheader("📈 Sales Trend")

daily_sales = (
    filtered_sales
    .groupby("Date", as_index=False)["Sales"]
    .sum()
)

fig_sales = px.line(
    daily_sales,
    x="Date",
    y="Sales",
    markers=True,
    title="Daily Sales Trend"
)

fig_sales.update_layout(
    xaxis_title="Date",
    yaxis_title="Units Sold"
)

st.plotly_chart(
    fig_sales,
    use_container_width=True
)


# ============================================================
# CITY + CATEGORY
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# CITY SALES
# ------------------------------------------------------------

with col1:

    st.subheader("🏙️ City-wise Sales")

    city_sales = (
        filtered_sales
        .groupby("City", as_index=False)["Sales"]
        .sum()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_city = px.bar(
        city_sales,
        x="City",
        y="Sales",
        text="Sales",
        title="Sales by City"
    )

    st.plotly_chart(
        fig_city,
        use_container_width=True
    )


# ------------------------------------------------------------
# CATEGORY SALES
# ------------------------------------------------------------

with col2:

    st.subheader("📦 Category-wise Sales")

    category_sales = (
        filtered_sales
        .groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_category = px.bar(
        category_sales,
        x="Category",
        y="Sales",
        text="Sales",
        title="Sales by Category"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# TOP PRODUCTS
# ============================================================

st.subheader("🏆 Top 10 Products")

top_products = (
    filtered_sales
    .groupby(
        ["SKU", "Product Name"],
        as_index=False
    )["Sales"]
    .sum()
    .sort_values(
        "Sales",
        ascending=False
    )
    .head(10)
)

fig_products = px.bar(
    top_products.sort_values("Sales"),
    x="Sales",
    y="Product Name",
    orientation="h",
    text="Sales",
    title="Top 10 Products by Units Sold"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)


# ============================================================
# REVENUE BY CATEGORY
# ============================================================

st.subheader("💰 Revenue by Category")

category_revenue = (
    filtered_sales
    .groupby("Category", as_index=False)["Revenue"]
    .sum()
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig_revenue = px.pie(
    category_revenue,
    names="Category",
    values="Revenue",
    hole=0.45,
    title="Revenue Distribution by Category"
)

st.plotly_chart(
    fig_revenue,
    use_container_width=True
)


# ============================================================
# DATA TABLE
# ============================================================

st.subheader("📋 Filtered Sales Data")

st.dataframe(
    filtered_sales,
    use_container_width=True,
    height=400
)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Retail & Geospatial BI Dashboard | Built with Python, "
    "Streamlit, Pandas and Plotly"
)