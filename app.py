import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Retail & Geospatial BI Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "raw"

# =========================================================
# HELPERS
# =========================================================

def find_file(filename):
    path = DATA_DIR / filename
    if path.exists():
        return path

    # flexible search
    files = list(DATA_DIR.glob("*"))
    target = filename.lower().replace(" ", "").replace("_", "")
    
    for f in files:
        name = f.name.lower().replace(" ", "").replace("_", "")
        if target in name or name in target:
            return f

    return None


def load_csv(filename):
    path = find_file(filename)

    if path is None:
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        try:
            return pd.read_excel(path)
        except Exception:
            return pd.DataFrame()


def clean_columns(df):
    if df.empty:
        return df

    df = df.copy()
    df.columns = [
        str(c).strip().replace("\n", " ").replace("\r", " ")
        for c in df.columns
    ]
    return df


def find_col(df, possibilities):
    if df.empty:
        return None

    normalized = {
        str(c).lower().replace(" ", "").replace("_", "").replace("-", ""): c
        for c in df.columns
    }

    for p in possibilities:
        key = p.lower().replace(" ", "").replace("_", "").replace("-", "")
        if key in normalized:
            return normalized[key]

    # partial matching
    for p in possibilities:
        key = p.lower().replace(" ", "").replace("_", "").replace("-", "")
        for norm, original in normalized.items():
            if key in norm or norm in key:
                return original

    return None


# =========================================================
# LOAD DATA
# =========================================================

sales = clean_columns(load_csv("Sales.csv"))
sku = clean_columns(load_csv("SKU MASTER.csv"))
opening = clean_columns(load_csv("Opening Stock.csv"))
transfer = clean_columns(load_csv("STOCK TRANSFER.csv"))
census = clean_columns(load_csv("census2011.csv"))
districts = clean_columns(load_csv("maharashtra-districts.csv"))
msme = clean_columns(
    load_csv("district_level_total_Registered_msme.csv")
)

# =========================================================
# SALES PROCESSING
# =========================================================

if not sales.empty:

    date_col = find_col(
        sales,
        ["Date", "date", "transaction_date", "sales_date"]
    )

    sku_col = find_col(
        sales,
        ["SKU", "sku", "product_code"]
    )

    product_col = find_col(
        sales,
        ["Product Name", "Product", "Description", "product_name"]
    )

    city_col = find_col(
        sales,
        ["City", "city", "Location"]
    )

    sales_col = find_col(
        sales,
        ["Sales", "Quantity", "Units Sold", "Units"]
    )

    if date_col:
        sales[date_col] = pd.to_datetime(
            sales[date_col],
            errors="coerce"
        )

    if sales_col:
        sales[sales_col] = pd.to_numeric(
            sales[sales_col],
            errors="coerce"
        ).fillna(0)

    # Merge SKU information
    if not sku.empty and sku_col:

        sku_sku_col = find_col(
            sku,
            ["SKU", "sku", "product_code"]
        )

        category_col_sku = find_col(
            sku,
            ["Category", "category"]
        )

        price_col = find_col(
            sku,
            ["Price", "price", "Unit Price"]
        )

        description_col = find_col(
            sku,
            ["Description", "Product Name", "Product"]
        )

        merge_cols = [sku_sku_col]

        if category_col_sku:
            merge_cols.append(category_col_sku)

        if price_col:
            merge_cols.append(price_col)

        if description_col:
            merge_cols.append(description_col)

        sku_temp = sku[merge_cols].drop_duplicates()

        rename_map = {}

        if category_col_sku:
            rename_map[category_col_sku] = "Category"

        if price_col:
            rename_map[price_col] = "Price"

        if description_col:
            rename_map[description_col] = "SKU Description"

        sku_temp = sku_temp.rename(columns=rename_map)

        sales = sales.merge(
            sku_temp,
            left_on=sku_col,
            right_on=sku_sku_col,
            how="left"
        )

    if "Category" not in sales.columns:
        sales["Category"] = "Unknown"

    if "Price" not in sales.columns:
        sales["Price"] = 0

    sales["Price"] = pd.to_numeric(
        sales["Price"],
        errors="coerce"
    ).fillna(0)

    if sales_col:
        sales["Revenue"] = sales[sales_col] * sales["Price"]
    else:
        sales["Revenue"] = 0

else:

    st.error("Sales.csv not found.")
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎛️ Dashboard Filters")

# Cities
available_cities = sorted(
    sales[city_col].dropna().astype(str).unique()
) if city_col else []

selected_cities = st.sidebar.multiselect(
    "Select City",
    available_cities,
    default=available_cities
)

# Categories
available_categories = sorted(
    sales["Category"].dropna().astype(str).unique()
)

selected_categories = st.sidebar.multiselect(
    "Select Category",
    available_categories,
    default=available_categories
)

# Date
if date_col and sales[date_col].notna().any():

    min_date = sales[date_col].min().date()
    max_date = sales[date_col].max().date()

    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:
    selected_dates = None


# =========================================================
# FILTER SALES
# =========================================================

filtered = sales.copy()

if city_col and selected_cities:
    filtered = filtered[
        filtered[city_col].astype(str).isin(selected_cities)
    ]

if selected_categories:
    filtered = filtered[
        filtered["Category"].astype(str).isin(selected_categories)
    ]

if date_col and selected_dates:

    if len(selected_dates) == 2:

        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)

        filtered = filtered[
            (filtered[date_col] >= start_date) &
            (filtered[date_col] < end_date)
        ]


# =========================================================
# HEADER
# =========================================================

st.title("🗺️ Retail & Geospatial Business Intelligence Dashboard")

st.markdown(
    """
    **Retail Sales • Inventory • Logistics • MSME • Census •
    Maharashtra Geospatial Analysis**
    """
)

st.divider()


# =========================================================
# OVERVIEW
# =========================================================

st.header("🏠 Executive Overview")

total_units = (
    filtered[sales_col].sum()
    if sales_col else 0
)

total_revenue = filtered["Revenue"].sum()

products = (
    filtered[sku_col].nunique()
    if sku_col else 0
)

cities_count = (
    filtered[city_col].nunique()
    if city_col else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("🛒 Total Units Sold", f"{total_units:,.0f}")
c2.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
c3.metric("📦 Products", f"{products:,}")
c4.metric("🏙️ Cities", f"{cities_count:,}")


# =========================================================
# RETAIL INTELLIGENCE
# =========================================================

st.header("🛍️ Retail Intelligence")

col1, col2 = st.columns(2)

with col1:

    if date_col and sales_col:

        daily_sales = (
            filtered
            .groupby(date_col)[sales_col]
            .sum()
            .reset_index()
        )

        fig = px.line(
            daily_sales,
            x=date_col,
            y=sales_col,
            markers=True,
            title="Daily Sales Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    if city_col and sales_col:

        city_sales = (
            filtered
            .groupby(city_col)[sales_col]
            .sum()
            .reset_index()
            .sort_values(sales_col, ascending=False)
        )

        fig = px.bar(
            city_sales,
            x=city_col,
            y=sales_col,
            text=sales_col,
            title="City-wise Sales"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


col3, col4 = st.columns(2)

with col3:

    category_sales = (
        filtered
        .groupby("Category")[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
    )

    fig = px.bar(
        category_sales,
        x=sales_col,
        y="Category",
        orientation="h",
        text=sales_col,
        title="Category-wise Sales"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col4:

    category_revenue = (
        filtered
        .groupby("Category")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    fig = px.pie(
        category_revenue,
        names="Category",
        values="Revenue",
        hole=0.45,
        title="Revenue Distribution by Category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TOP PRODUCTS
# =========================================================

st.subheader("🏆 Top 10 Products")

if product_col and sales_col:

    top_products = (
        filtered
        .groupby(product_col)[sales_col]
        .sum()
        .reset_index()
        .sort_values(sales_col, ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_products.sort_values(sales_col),
        x=sales_col,
        y=product_col,
        orientation="h",
        text=sales_col,
        title="Top 10 Products by Units Sold"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# GEOSPATIAL INTELLIGENCE
# =========================================================

st.header("🗺️ Geospatial Intelligence")

st.markdown(
    """
    This section connects **retail sales with geographical location**
    to identify spatial business patterns.
    """
)

# Known Maharashtra city coordinates
city_coordinates = {
    "Mumbai": (19.0760, 72.8777),
    "Thane": (19.2183, 72.9781),
    "Navi Mumbai": (19.0330, 73.0297),
    "Pune": (18.5204, 73.8567),
    "Nashik": (19.9975, 73.7898),
    "Aurangabad": (19.8762, 75.3433),
    "Chhatrapati Sambhajinagar": (19.8762, 75.3433),
    "Nagpur": (21.1458, 79.0882),
    "Kolhapur": (16.7050, 74.2433),
    "Solapur": (17.6599, 75.9064),
    "Amravati": (20.9374, 77.7796),
    "Satara": (17.6805, 74.0183),
    "Sangli": (16.8524, 74.5815),
    "Ahmednagar": (19.0948, 74.7480),
    "Nanded": (19.1383, 77.3210),
    "Jalgaon": (21.0077, 75.5626)
}

if city_col:

    geo_sales = (
        filtered
        .groupby(city_col)
        .agg(
            Sales=(sales_col, "sum"),
            Revenue=("Revenue", "sum"),
            Products=(sku_col, "nunique")
        )
        .reset_index()
    )

    geo_sales["Latitude"] = geo_sales[city_col].map(
        lambda x: city_coordinates.get(str(x), (np.nan, np.nan))[0]
    )

    geo_sales["Longitude"] = geo_sales[city_col].map(
        lambda x: city_coordinates.get(str(x), (np.nan, np.nan))[1]
    )

    geo_sales = geo_sales.dropna(
        subset=["Latitude", "Longitude"]
    )

    if not geo_sales.empty:

        fig = px.scatter_mapbox(
            geo_sales,
            lat="Latitude",
            lon="Longitude",
            size="Sales",
            color="Revenue",
            hover_name=city_col,
            hover_data=[
                "Sales",
                "Revenue",
                "Products"
            ],
            zoom=5.5,
            height=600,
            title="📍 Retail Sales Geospatial Map"
        )

        fig.update_layout(
            mapbox_style="open-street-map"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning(
            "City names do not match the available map coordinates."
        )


# =========================================================
# MSME INTELLIGENCE
# =========================================================

st.header("🏢 MSME / Business Density Intelligence")

if not msme.empty:

    st.write("MSME dataset detected.")

    st.dataframe(
        msme.head(20),
        use_container_width=True
    )

    # Try to identify district and MSME count
    msme_district = find_col(
        msme,
        ["District", "district", "District Name"]
    )

    msme_value = find_col(
        msme,
        [
            "Total",
            "Total Registered MSME",
            "Registered MSME",
            "MSME",
            "Count"
        ]
    )

    if msme_district and msme_value:

        msme[msme_value] = pd.to_numeric(
            msme[msme_value],
            errors="coerce"
        ).fillna(0)

        msm_plot = (
            msme
            .groupby(msme_district)[msme_value]
            .sum()
            .reset_index()
            .sort_values(msme_value, ascending=False)
            .head(20)
        )

        fig = px.bar(
            msm_plot,
            x=msme_value,
            y=msme_district,
            orientation="h",
            title="Top Districts by Registered MSMEs"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

else:

    st.info("MSME dataset not available.")


# =========================================================
# LOGISTICS
# =========================================================

st.header("🚚 Logistics Intelligence")

if not transfer.empty:

    st.success(
        "Stock Transfer dataset connected."
    )

    st.dataframe(
        transfer.head(20),
        use_container_width=True
    )

    source_col = find_col(
        transfer,
        [
            "Source",
            "From",
            "Source City",
            "Origin",
            "From City"
        ]
    )

    destination_col = find_col(
        transfer,
        [
            "Destination",
            "To",
            "Destination City",
            "To City"
        ]
    )

    quantity_col = find_col(
        transfer,
        [
            "Quantity",
            "Transfer Quantity",
            "Units",
            "Stock Transfer"
        ]
    )

    if source_col and destination_col and quantity_col:

        transfer[quantity_col] = pd.to_numeric(
            transfer[quantity_col],
            errors="coerce"
        ).fillna(0)

        route_data = (
            transfer
            .groupby(
                [source_col, destination_col]
            )[quantity_col]
            .sum()
            .reset_index()
        )

        route_data = route_data.sort_values(
            quantity_col,
            ascending=False
        )

        st.subheader("📦 Major Stock Transfer Routes")

        st.dataframe(
            route_data.head(20),
            use_container_width=True
        )

        st.metric(
            "Total Stock Transferred",
            f"{transfer[quantity_col].sum():,.0f}"
        )

    else:

        st.info(
            "Transfer columns could not be automatically mapped. "
            "The raw logistics data is displayed above."
        )

else:

    st.warning(
        "STOCK TRANSFER dataset not found."
    )


# =========================================================
# INVENTORY
# =========================================================

st.subheader("📦 Inventory Intelligence")

if not opening.empty:

    st.write(
        f"Opening Stock Records: {len(opening):,}"
    )

    st.dataframe(
        opening.head(20),
        use_container_width=True
    )


# =========================================================
# URBAN PLANNING
# =========================================================

st.header("🏙️ Urban Planning Intelligence")

if not census.empty:

    st.success(
        "Census 2011 dataset connected."
    )

    st.dataframe(
        census.head(15),
        use_container_width=True
    )

    numeric_cols = census.select_dtypes(
        include=np.number
    ).columns.tolist()

    if numeric_cols:

        selected_numeric = st.selectbox(
            "Select Census Indicator",
            numeric_cols
        )

        urban_summary = (
            census[selected_numeric]
            .describe()
            .to_frame()
            .T
        )

        st.dataframe(
            urban_summary,
            use_container_width=True
        )

else:

    st.warning(
        "Census dataset not found."
    )


# =========================================================
# LOCATION INTELLIGENCE
# =========================================================

st.header("📍 Location Intelligence")

st.markdown(
    """
    ### Business Opportunity Analysis

    Location intelligence combines:

    **Retail Demand + Business Presence + Population + Geography**

    to identify areas requiring further business analysis.
    """
)

if city_col:

    location_analysis = (
        filtered
        .groupby(city_col)
        .agg(
            Units_Sold=(sales_col, "sum"),
            Revenue=("Revenue", "sum"),
            Products=(sku_col, "nunique")
        )
        .reset_index()
    )

    location_analysis["Revenue_per_Unit"] = (
        location_analysis["Revenue"] /
        location_analysis["Units_Sold"].replace(0, np.nan)
    )

    location_analysis = location_analysis.sort_values(
        "Revenue",
        ascending=False
    )

    st.dataframe(
        location_analysis,
        use_container_width=True
    )


# =========================================================
# DETAILED DATA
# =========================================================

st.header("📋 Filtered Sales Data")

st.dataframe(
    filtered,
    use_container_width=True,
    height=500
)


# =========================================================
# DATASET SUMMARY
# =========================================================

with st.expander("📂 Dataset Information"):

    dataset_info = pd.DataFrame({
        "Dataset": [
            "Sales",
            "SKU Master",
            "Opening Stock",
            "Stock Transfer",
            "Census 2011",
            "Maharashtra Districts",
            "Registered MSME"
        ],
        "Rows": [
            len(sales),
            len(sku),
            len(opening),
            len(transfer),
            len(census),
            len(districts),
            len(msme)
        ],
        "Status": [
            "Loaded" if not sales.empty else "Missing",
            "Loaded" if not sku.empty else "Missing",
            "Loaded" if not opening.empty else "Missing",
            "Loaded" if not transfer.empty else "Missing",
            "Loaded" if not census.empty else "Missing",
            "Loaded" if not districts.empty else "Missing",
            "Loaded" if not msme.empty else "Missing"
        ]
    })

    st.dataframe(
        dataset_info,
        use_container_width=True
    )


st.divider()

st.caption(
    "Retail & Geospatial Business Intelligence Dashboard | "
    "Streamlit | Python | Pandas | Plotly"
)