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
    initial_sidebar_state="expanded",
)

# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

# =========================================================
# HELPERS
# =========================================================
def normalize_name(value):
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def find_file(filename):
    # Look in data/raw first, then recursively under data/. This makes the
    # dashboard tolerant of minor filename/path differences on Streamlit Cloud.
    search_roots = [DATA_DIR, BASE_DIR / "data"]

    target = normalize_name(filename)
    for root in search_roots:
        if not root.exists():
            continue

        exact = root / filename
        if exact.exists() and exact.is_file():
            return exact

        candidates = [f for f in root.rglob("*") if f.is_file()]
        for f in candidates:
            if normalize_name(f.name) == target:
                return f
        for f in candidates:
            name = normalize_name(f.name)
            if target in name or name in target:
                return f

    return None


def load_table(filename):
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
    df.columns = [str(c).strip().replace("\n", " ").replace("\r", " ") for c in df.columns]
    return df


def find_col(df, possibilities):
    if df.empty:
        return None

    normalized = {
        normalize_name(c): c for c in df.columns
    }

    for possible in possibilities:
        key = normalize_name(possible)
        if key in normalized:
            return normalized[key]

    for possible in possibilities:
        key = normalize_name(possible)
        for norm, original in normalized.items():
            if key in norm or norm in key:
                return original
    return None


def safe_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


# A single chart wrapper with explicit unique keys prevents Streamlit duplicate
# element IDs even if the app is rerun many times.
def show_chart(fig, key, height=None):
    if height is not None:
        fig.update_layout(height=height)
    st.plotly_chart(fig, width="stretch", key=key)


# =========================================================
# STOCK TRANSFER MATRIX PARSER
# =========================================================
def load_stock_transfer_matrix(filename):
    """Load the supplied STOCK TRANSFER matrix safely.

    Source layout:
      Row 0 -> city block names (Pune, Aurangabad, Nasik)
      Row 1 -> dates for each city block
      Row 2+ -> SKU quantities

    Output:
      City | SKU | Date | Transfer Quantity

    A cleaned 4-column file is preferred when present because it is more
    reliable for deployment, but the original matrix is also supported.
    """
    # Preferred deployment-safe cleaned file.
    cleaned_candidates = [
        DATA_DIR / "stock_transfer_cleaned.csv",
        BASE_DIR / "stock_transfer_cleaned.csv",
    ]
    for cleaned_path in cleaned_candidates:
        if cleaned_path.exists():
            try:
                cleaned = pd.read_csv(cleaned_path)
                cleaned.columns = [str(c).strip() for c in cleaned.columns]
                required = {"City", "SKU", "Date", "Transfer Quantity"}
                if required.issubset(set(cleaned.columns)):
                    cleaned["Date"] = pd.to_datetime(cleaned["Date"], errors="coerce")
                    cleaned["Transfer Quantity"] = pd.to_numeric(
                        cleaned["Transfer Quantity"], errors="coerce"
                    )
                    cleaned = cleaned.dropna(subset=["City", "SKU", "Date", "Transfer Quantity"]).copy()
                    if not cleaned.empty:
                        cleaned["City"] = cleaned["City"].astype(str).str.strip()
                        cleaned["SKU"] = cleaned["SKU"].astype(str).str.strip()
                        return cleaned[["City", "SKU", "Date", "Transfer Quantity"]]
            except Exception:
                pass

    path = find_file(filename)
    if path is None:
        return pd.DataFrame(columns=["City", "SKU", "Date", "Transfer Quantity"])

    try:
        raw = pd.read_csv(path, header=None)
    except Exception:
        try:
            raw = pd.read_excel(path, header=None)
        except Exception:
            return pd.DataFrame(columns=["City", "SKU", "Date", "Transfer Quantity"])

    if raw.shape[0] < 3 or raw.shape[1] < 2:
        return pd.DataFrame(columns=["City", "SKU", "Date", "Transfer Quantity"])

    # Detect city starts from row 0. Ignore the first label cell ("City").
    city_starts = []
    for col in range(raw.shape[1]):
        value = raw.iat[0, col]
        if pd.isna(value):
            continue
        city = str(value).strip()
        if not city or city.lower() in {"city", "sku", "date", "nan"}:
            continue
        city_starts.append((col, city))

    if not city_starts:
        return pd.DataFrame(columns=["City", "SKU", "Date", "Transfer Quantity"])

    records = []
    aliases = {
        "nasik": "Nashik",
        "nashik": "Nashik",
        "aurangabad": "Aurangabad",
        "pune": "Pune",
    }

    for idx, (start_col, raw_city) in enumerate(city_starts):
        end_col = city_starts[idx + 1][0] if idx + 1 < len(city_starts) else raw.shape[1]
        city = aliases.get(raw_city.strip().lower(), raw_city.strip())

        for row in range(2, raw.shape[0]):
            sku_value = raw.iat[row, 0]
            if pd.isna(sku_value) or not str(sku_value).strip():
                continue
            sku_value = str(sku_value).strip()

            for col in range(start_col, end_col):
                dt = pd.to_datetime(raw.iat[1, col], errors="coerce")
                qty = pd.to_numeric(raw.iat[row, col], errors="coerce")
                if pd.isna(dt) or pd.isna(qty):
                    continue
                records.append((city, sku_value, dt, float(qty)))

    return pd.DataFrame(
        records,
        columns=["City", "SKU", "Date", "Transfer Quantity"],
    )


# =========================================================
# CITY COORDINATES
# =========================================================
CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Thane": (19.2183, 72.9781),
    "Navi Mumbai": (19.0330, 73.0297),
    "Pune": (18.5204, 73.8567),
    "Nashik": (19.9975, 73.7898),
    "Nasik": (19.9975, 73.7898),
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
    "Jalgaon": (21.0077, 75.5626),
}

# =========================================================
# LOAD DATASETS
# =========================================================
sales = clean_columns(load_table("Sales.csv"))
sku = clean_columns(load_table("SKU MASTER.csv"))
opening = clean_columns(load_table("Opening Stock.csv"))
transfer = load_stock_transfer_matrix("STOCK TRANSFER.csv")
census = clean_columns(load_table("census2011.csv"))
districts = clean_columns(load_table("maharashtra-districts.csv"))
msme = clean_columns(load_table("district_level_total_Registered_msme.csv"))

if sales.empty:
    st.error("Sales.csv could not be loaded. Check that it exists inside data/raw/.")
    st.stop()

# =========================================================
# SALES COLUMN DETECTION
# =========================================================
date_col = find_col(sales, ["Date", "transaction_date", "sales_date"])
sku_col = find_col(sales, ["SKU", "product_code", "item_code"])
product_col = find_col(sales, ["Product Name", "Product", "Description", "product_name"])
city_col = find_col(sales, ["City", "Location"])
sales_col = find_col(sales, ["Sales", "Quantity", "Units Sold", "Units", "Qty"])

# =========================================================
# SALES CLEANING + SKU MASTER MERGE
# =========================================================
if date_col:
    sales[date_col] = pd.to_datetime(sales[date_col], errors="coerce")

if sales_col:
    sales[sales_col] = safe_number(sales[sales_col])
else:
    sales["Sales"] = 0
    sales_col = "Sales"

if sku_col and not sku.empty:
    sku_sku_col = find_col(sku, ["SKU", "product_code", "item_code"])
    category_col = find_col(sku, ["Category"])
    price_col = find_col(sku, ["Price", "Unit Price"])
    desc_col = find_col(sku, ["Description", "Product Name", "Product"])

    if sku_sku_col:
        merge_cols = [sku_sku_col]
        for c in [category_col, price_col, desc_col]:
            if c and c not in merge_cols:
                merge_cols.append(c)

        sku_temp = sku[merge_cols].drop_duplicates(subset=[sku_sku_col]).copy()
        rename_map = {}
        if category_col:
            rename_map[category_col] = "Category"
        if price_col:
            rename_map[price_col] = "Price"
        if desc_col:
            rename_map[desc_col] = "SKU Description"
        sku_temp = sku_temp.rename(columns=rename_map)

        for c in ["Category", "Price", "SKU Description"]:
            if c in sales.columns:
                sales = sales.drop(columns=c)

        sales = sales.merge(
            sku_temp,
            left_on=sku_col,
            right_on=sku_sku_col,
            how="left",
        )

if "Category" not in sales.columns:
    sales["Category"] = "Unknown"
if "Price" not in sales.columns:
    sales["Price"] = 0

sales["Category"] = sales["Category"].fillna("Unknown").astype(str)
sales["Price"] = safe_number(sales["Price"])
sales["Revenue"] = sales[sales_col] * sales["Price"]

# =========================================================
# SIDEBAR - ONLY ONE INSTANCE
# =========================================================
st.sidebar.title("🎛️ Dashboard Filters")

available_cities = sorted(sales[city_col].dropna().astype(str).unique()) if city_col else []
selected_cities = st.sidebar.multiselect(
    "Select City",
    options=available_cities,
    default=available_cities,
    key="dashboard_city_filter",
)

available_categories = sorted(sales["Category"].dropna().astype(str).unique())
selected_categories = st.sidebar.multiselect(
    "Select Category",
    options=available_categories,
    default=available_categories,
    key="dashboard_category_filter",
)

selected_dates = None
if date_col and sales[date_col].notna().any():
    min_date = sales[date_col].min().date()
    max_date = sales[date_col].max().date()
    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="dashboard_date_filter",
    )

# =========================================================
# APPLY FILTERS
# =========================================================
filtered = sales.copy()

if city_col and selected_cities:
    filtered = filtered[filtered[city_col].astype(str).isin(selected_cities)]

if selected_categories:
    filtered = filtered[filtered["Category"].astype(str).isin(selected_categories)]

if date_col and selected_dates:
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date = pd.Timestamp(selected_dates[0])
        end_date = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)
        filtered = filtered[(filtered[date_col] >= start_date) & (filtered[date_col] < end_date)]
    else:
        one_date = pd.Timestamp(selected_dates)
        filtered = filtered[filtered[date_col].dt.date == one_date.date()]

# =========================================================
# HEADER
# =========================================================
st.title("🗺️ Retail & Geospatial Business Intelligence Dashboard")
st.markdown(
    "**Retail Sales • Inventory • Logistics • MSME • Census • Maharashtra Geospatial Analysis**"
)
st.divider()

# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================
st.header("🏠 Executive Overview")

total_units = filtered[sales_col].sum()
total_revenue = filtered["Revenue"].sum()
products = filtered[sku_col].nunique() if sku_col and sku_col in filtered.columns else (
    filtered[product_col].nunique() if product_col and product_col in filtered.columns else 0
)
cities_count = filtered[city_col].nunique() if city_col and city_col in filtered.columns else 0

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
    if date_col and sales_col and not filtered.empty:
        daily_sales = filtered.groupby(date_col, as_index=False)[sales_col].sum()
        fig = px.line(daily_sales, x=date_col, y=sales_col, markers=True, title="Daily Sales Trend")
        show_chart(fig, "retail_daily_sales")
    else:
        st.info("Daily sales trend is not available for the current selection.")

with col2:
    if city_col and sales_col and not filtered.empty:
        city_sales = (
            filtered.groupby(city_col, as_index=False)[sales_col]
            .sum()
            .sort_values(sales_col, ascending=False)
        )
        fig = px.bar(city_sales, x=city_col, y=sales_col, text=sales_col, title="City-wise Sales")
        show_chart(fig, "retail_city_sales")

col3, col4 = st.columns(2)
with col3:
    category_sales = (
        filtered.groupby("Category", as_index=False)[sales_col]
        .sum()
        .sort_values(sales_col, ascending=False)
    )
    fig = px.bar(
        category_sales,
        x=sales_col,
        y="Category",
        orientation="h",
        text=sales_col,
        title="Category-wise Sales",
    )
    show_chart(fig, "retail_category_sales")

with col4:
    category_revenue = (
        filtered.groupby("Category", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    fig = px.pie(
        category_revenue,
        names="Category",
        values="Revenue",
        hole=0.45,
        title="Revenue Distribution by Category",
    )
    show_chart(fig, "retail_category_revenue")

# =========================================================
# TOP PRODUCTS
# =========================================================
st.subheader("🏆 Top 10 Products")
if product_col and product_col in filtered.columns and not filtered.empty:
    top_products = (
        filtered.groupby(product_col, as_index=False)[sales_col]
        .sum()
        .sort_values(sales_col, ascending=False)
        .head(10)
    )
    fig = px.bar(
        top_products.sort_values(sales_col),
        x=sales_col,
        y=product_col,
        orientation="h",
        text=sales_col,
        title="Top 10 Products by Units Sold",
    )
    show_chart(fig, "retail_top_products")
else:
    st.info("Product-level information is not available.")

# =========================================================
# GEOSPATIAL INTELLIGENCE
# =========================================================
st.header("🗺️ Geospatial Intelligence")
st.markdown(
    "This section connects **retail sales with geographical location** using city coordinates. "
    "Marker size represents sales and marker colour represents revenue."
)

if city_col and not filtered.empty:
    geo_agg = {"Sales": (sales_col, "sum"), "Revenue": ("Revenue", "sum")}
    if sku_col and sku_col in filtered.columns:
        geo_agg["Products"] = (sku_col, "nunique")

    geo_sales = filtered.groupby(city_col).agg(**geo_agg).reset_index()
    geo_sales["Latitude"] = geo_sales[city_col].map(
        lambda x: CITY_COORDINATES.get(str(x), (np.nan, np.nan))[0]
    )
    geo_sales["Longitude"] = geo_sales[city_col].map(
        lambda x: CITY_COORDINATES.get(str(x), (np.nan, np.nan))[1]
    )
    geo_sales = geo_sales.dropna(subset=["Latitude", "Longitude"])

    if not geo_sales.empty:
        max_sales = max(float(geo_sales["Sales"].max()), 1.0)
        marker_sizes = 18 + (geo_sales["Sales"] / max_sales * 42)

        custom_columns = [geo_sales["Sales"], geo_sales["Revenue"]]
        if "Products" in geo_sales.columns:
            custom_columns.append(geo_sales["Products"])
        else:
            custom_columns.append(pd.Series(0, index=geo_sales.index))

        fig = go.Figure(
            go.Scattergeo(
                lat=geo_sales["Latitude"],
                lon=geo_sales["Longitude"],
                mode="markers+text",
                text=geo_sales[city_col].astype(str),
                textposition="top center",
                marker=dict(
                    size=marker_sizes,
                    color=geo_sales["Revenue"],
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(title="Revenue"),
                    line=dict(width=1),
                    opacity=0.85,
                ),
                customdata=np.column_stack(custom_columns),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Sales: %{customdata[0]:,.0f}<br>"
                    "Revenue: ₹%{customdata[1]:,.0f}<br>"
                    "Products: %{customdata[2]:,.0f}<extra></extra>"
                ),
                name="Retail Locations",
            )
        )
        fig.update_geos(
            scope="asia",
            projection_type="mercator",
            showland=True,
            showcountries=True,
            showcoastlines=True,
            showocean=True,
            landcolor="lightgray",
            oceancolor="lightblue",
            coastlinecolor="gray",
            countrycolor="gray",
            center=dict(lat=19.2, lon=75.0),
            lataxis_range=[15.0, 23.0],
            lonaxis_range=[70.0, 81.0],
        )
        fig.update_layout(title="📍 Retail Sales & Revenue by Location", margin=dict(l=0, r=0, t=60, b=0))
        show_chart(fig, "geospatial_retail_map", height=620)

        st.subheader("📍 Geospatial Sales Summary")
        geo_display = geo_sales[
            [city_col, "Sales", "Revenue"] + (["Products"] if "Products" in geo_sales.columns else [])
        ].sort_values("Sales", ascending=False)
        st.dataframe(geo_display, width="stretch")
    else:
        st.warning("No matching city coordinates were found for the selected cities.")
else:
    st.info("City information is not available for geospatial analysis.")

# =========================================================
# MSME / BUSINESS DENSITY
# =========================================================
st.header("🏢 MSME / Business Density Intelligence")
if not msme.empty:
    msme_district = find_col(msme, ["District", "District Name", "district_name"])
    msme_value = find_col(msme, ["Total", "Total Registered MSME", "Registered MSME", "MSME", "Count"])

    if msme_district and msme_value:
        msme[msme_value] = safe_number(msme[msme_value])
        msm_plot = (
            msme.groupby(msme_district, as_index=False)[msme_value]
            .sum()
            .sort_values(msme_value, ascending=False)
            .head(20)
        )
        fig = px.bar(
            msm_plot,
            x=msme_value,
            y=msme_district,
            orientation="h",
            text=msme_value,
            title="Top Districts by Registered MSMEs",
        )
        show_chart(fig, "msme_districts")
    else:
        st.info("MSME dataset loaded, but district/count columns could not be mapped automatically.")
else:
    st.info("MSME dataset not available.")

# =========================================================
# LOGISTICS INTELLIGENCE
# =========================================================
st.header("🚚 Logistics & Stock Transfer Intelligence")

if not transfer.empty:
    st.info(
        "The STOCK TRANSFER file is a city-wise matrix. It contains SKU quantities by date "
        "for Pune, Aurangabad and Nasik/Nashik. It does not contain explicit source and "
        "destination fields, so the dashboard does not invent transfer routes."
    )

    transfer_city = (
        transfer.groupby("City", as_index=False)["Transfer Quantity"]
        .sum()
        .sort_values("Transfer Quantity", ascending=False)
    )
    transfer_sku = (
        transfer.groupby("SKU", as_index=False)["Transfer Quantity"]
        .sum()
        .sort_values("Transfer Quantity", ascending=False)
    )

    l1, l2, l3 = st.columns(3)
    l1.metric("Total Transfer Quantity", f"{transfer['Transfer Quantity'].sum():,.0f}")
    l2.metric("Cities Covered", f"{transfer['City'].nunique():,}")
    l3.metric("SKUs Covered", f"{transfer['SKU'].nunique():,}")

    st.subheader("🏙️ City-wise Stock Transfer")
    fig = px.bar(
        transfer_city,
        x="City",
        y="Transfer Quantity",
        text="Transfer Quantity",
        title="Stock Transfer / Allocation by City",
    )
    show_chart(fig, "logistics_city_transfer")

    st.subheader("🗺️ Stock Transfer Intensity Map")
    transfer_map = transfer_city.copy()
    transfer_map["Latitude"] = transfer_map["City"].map(
        lambda x: CITY_COORDINATES.get(str(x), (np.nan, np.nan))[0]
    )
    transfer_map["Longitude"] = transfer_map["City"].map(
        lambda x: CITY_COORDINATES.get(str(x), (np.nan, np.nan))[1]
    )
    transfer_map = transfer_map.dropna(subset=["Latitude", "Longitude"])

    if not transfer_map.empty:
        fig = go.Figure(
            go.Scattergeo(
                lat=transfer_map["Latitude"],
                lon=transfer_map["Longitude"],
                mode="markers+text",
                text=transfer_map["City"],
                textposition="top center",
                marker=dict(
                    size=np.maximum(18, np.sqrt(transfer_map["Transfer Quantity"]) * 1.5),
                    opacity=0.85,
                ),
                customdata=np.column_stack([transfer_map["Transfer Quantity"]]),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Transfer Quantity: %{customdata[0]:,.0f}<extra></extra>"
                ),
                showlegend=False,
            )
        )
        fig.update_geos(
            scope="asia",
            projection_type="mercator",
            showland=True,
            showcountries=True,
            showcoastlines=True,
            showocean=True,
            center=dict(lat=19.2, lon=75.0),
            lataxis_range=[15.0, 23.0],
            lonaxis_range=[70.0, 81.0],
        )
        fig.update_layout(title="City-wise Stock Transfer Intensity", margin=dict(l=0, r=0, t=50, b=0))
        show_chart(fig, "logistics_transfer_map", height=600)

    st.subheader("📦 Top SKUs by Transfer Quantity")
    fig = px.bar(
        transfer_sku.head(10).sort_values("Transfer Quantity"),
        x="Transfer Quantity",
        y="SKU",
        orientation="h",
        text="Transfer Quantity",
        title="Top 10 SKUs by Stock Transfer Quantity",
    )
    show_chart(fig, "logistics_top_skus")

    st.subheader("📋 Transfer Data")
    st.dataframe(
        transfer.sort_values(["Date", "City", "SKU"]).head(100),
        width="stretch",
    )
else:
    st.warning("STOCK TRANSFER dataset not found or could not be parsed.")

# =========================================================
# INVENTORY INTELLIGENCE
# =========================================================
st.header("📦 Inventory Intelligence")
if not opening.empty:
    st.write(f"Opening Stock Records: {len(opening):,}")
    st.dataframe(opening.head(20), width="stretch")
else:
    st.info("Opening Stock dataset not available.")

# =========================================================
# URBAN / CENSUS INTELLIGENCE
# =========================================================
st.header("🏙️ Urban Planning Intelligence")
if not census.empty:
    numeric_cols = census.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        selected_numeric = st.selectbox(
            "Select Census Indicator",
            numeric_cols,
            key="census_indicator",
        )
        urban_summary = census[selected_numeric].describe().to_frame().T
        st.dataframe(urban_summary, width="stretch")
        st.caption("Census indicators provide demographic context for location and market analysis.")
    else:
        st.info("No numeric Census indicators were detected.")
else:
    st.warning("Census dataset not found.")

# =========================================================
# LOCATION INTELLIGENCE
# =========================================================
st.header("📍 Location Intelligence")
st.markdown(
    "### Business Opportunity Analysis\n\n"
    "Location intelligence combines **Retail Demand + Business Presence + Population + Geography** "
    "to support further business analysis."
)

if city_col and not filtered.empty:
    location_agg = {"Units_Sold": (sales_col, "sum"), "Revenue": ("Revenue", "sum")}
    if sku_col and sku_col in filtered.columns:
        location_agg["Products"] = (sku_col, "nunique")

    location_analysis = filtered.groupby(city_col).agg(**location_agg).reset_index()
    location_analysis["Revenue_per_Unit"] = (
        location_analysis["Revenue"] / location_analysis["Units_Sold"].replace(0, np.nan)
    )
    location_analysis = location_analysis.sort_values("Revenue", ascending=False)
    st.dataframe(location_analysis, width="stretch")

# =========================================================
# FILTERED SALES DATA
# =========================================================
st.header("📋 Filtered Sales Data")
st.dataframe(filtered, width="stretch", height=500)

# =========================================================
# DATASET SUMMARY
# =========================================================
with st.expander("📂 Dataset Information"):
    dataset_info = pd.DataFrame(
        {
            "Dataset": [
                "Sales",
                "SKU Master",
                "Opening Stock",
                "Stock Transfer",
                "Census 2011",
                "Maharashtra Districts",
                "Registered MSME",
            ],
            "Rows": [
                len(sales),
                len(sku),
                len(opening),
                len(transfer),
                len(census),
                len(districts),
                len(msme),
            ],
            "Status": [
                "Loaded" if not sales.empty else "Missing",
                "Loaded" if not sku.empty else "Missing",
                "Loaded" if not opening.empty else "Missing",
                "Loaded" if not transfer.empty else "Missing",
                "Loaded" if not census.empty else "Missing",
                "Loaded" if not districts.empty else "Missing",
                "Loaded" if not msme.empty else "Missing",
            ],
        }
    )
    st.dataframe(dataset_info, width="stretch")

# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption("Retail & Geospatial Business Intelligence Dashboard | Streamlit | Python | Pandas | Plotly")
