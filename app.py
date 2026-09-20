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

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

# =========================================================
# HELPERS
# =========================================================
def normalize_name(value):
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def find_file(*filenames):
    roots = [DATA_DIR, BASE_DIR / "data", BASE_DIR]
    wanted = [normalize_name(x) for x in filenames]
    for root in roots:
        if not root.exists():
            continue
        for wanted_name, original in zip(wanted, filenames):
            exact = root / original
            if exact.exists() and exact.is_file():
                return exact
        files = [x for x in root.rglob("*") if x.is_file()]
        for wanted_name in wanted:
            for f in files:
                n = normalize_name(f.name)
                if n == wanted_name or wanted_name in n or n in wanted_name:
                    return f
    return None


def load_table(*filenames):
    path = find_file(*filenames)
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
    out = df.copy()
    out.columns = [str(c).strip().replace("\n", " ").replace("\r", " ") for c in out.columns]
    return out


def find_col(df, possibilities):
    if df.empty:
        return None
    normalized = {normalize_name(c): c for c in df.columns}
    for p in possibilities:
        k = normalize_name(p)
        if k in normalized:
            return normalized[k]
    for p in possibilities:
        k = normalize_name(p)
        for n, original in normalized.items():
            if k in n or n in k:
                return original
    return None


def safe_number(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def show_chart(fig, key, height=None):
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, width="stretch", key=key)


def empty_matrix_frame():
    return pd.DataFrame(columns=["City", "SKU", "Date", "Quantity"])


def parse_city_matrix(filename, quantity_name="Quantity"):
    """Parse the project's city-block matrix format.

    Expected layout:
      row 0: city names at the start of each block
      row 1: dates across each block
      col 0: SKU names
      row 2+: quantities
    """
    path = find_file(filename)
    if path is None:
        return empty_matrix_frame()

    try:
        raw = pd.read_csv(path, header=None)
    except Exception:
        try:
            raw = pd.read_excel(path, header=None)
        except Exception:
            return empty_matrix_frame()

    if raw.shape[0] < 3 or raw.shape[1] < 2:
        return empty_matrix_frame()

    city_starts = []
    for col in range(raw.shape[1]):
        v = raw.iat[0, col]
        if pd.isna(v):
            continue
        city = str(v).strip()
        if city and city.lower() not in {"city", "sku", "date", "nan"}:
            city_starts.append((col, city))

    if not city_starts:
        return empty_matrix_frame()

    aliases = {
        "nasik": "Nashik",
        "nashik": "Nashik",
        "aurangabad": "Aurangabad",
        "chhatrapati sambhajinagar": "Aurangabad",
        "pune": "Pune",
    }
    records = []

    for i, (start, raw_city) in enumerate(city_starts):
        end = city_starts[i + 1][0] if i + 1 < len(city_starts) else raw.shape[1]
        city = aliases.get(raw_city.lower(), raw_city)
        for row in range(2, raw.shape[0]):
            sku_value = raw.iat[row, 0]
            if pd.isna(sku_value) or not str(sku_value).strip():
                continue
            sku_value = str(sku_value).strip()
            for col in range(start, end):
                dt = pd.to_datetime(raw.iat[1, col], errors="coerce")
                qty = pd.to_numeric(raw.iat[row, col], errors="coerce")
                if pd.isna(dt) or pd.isna(qty):
                    continue
                records.append((city, sku_value, dt, float(qty)))

    out = pd.DataFrame(records, columns=["City", "SKU", "Date", quantity_name])
    return out


def load_transfer():
    # Prefer the normalized file if it exists.
    path = find_file("stock_transfer_cleaned.csv")
    if path is not None:
        try:
            df = pd.read_csv(path)
            df.columns = [str(c).strip() for c in df.columns]
            if {"City", "SKU", "Date", "Transfer Quantity"}.issubset(df.columns):
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df["Transfer Quantity"] = safe_number(df["Transfer Quantity"])
                return df.dropna(subset=["Date"])
        except Exception:
            pass
    return parse_city_matrix("STOCK TRANSFER.csv", "Transfer Quantity")


CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Thane": (19.2183, 72.9781),
    "Navi Mumbai": (19.0330, 73.0297),
    "Pune": (18.5204, 73.8567),
    "Nashik": (19.9975, 73.7898),
    "Aurangabad": (19.8762, 75.3433),
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


def add_coordinates(df, city_col_name="City"):
    out = df.copy()
    out["Latitude"] = out[city_col_name].map(lambda x: CITY_COORDINATES.get(str(x), (np.nan, np.nan))[0])
    out["Longitude"] = out[city_col_name].map(lambda x: CITY_COORDINATES.get(str(x), (np.nan, np.nan))[1])
    return out.dropna(subset=["Latitude", "Longitude"])


def geo_bubble_map(df, city_col_name, value_col, title, key, height=500):
    geo = add_coordinates(df, city_col_name)
    if geo.empty:
        st.info("No mapped city coordinates are available for this selection.")
        return

    fig = px.scatter_geo(
        geo,
        lat="Latitude",
        lon="Longitude",
        size=value_col,
        color=value_col,
        hover_name=city_col_name,
        hover_data={value_col: ":,.0f", "Latitude": False, "Longitude": False},
        projection="mercator",
        title=title,
    )
    fig.update_traces(marker=dict(opacity=0.82, line=dict(width=1)))
    fig.update_geos(
        showland=True,
        landcolor="lightgray",
        showocean=True,
        oceancolor="aliceblue",
        showcountries=True,
        showcoastlines=True,
        fitbounds="locations",
        lonaxis_range=[70, 81],
        lataxis_range=[15, 23],
    )
    fig.update_layout(margin=dict(l=0, r=0, t=55, b=0), legend_title_text="Intensity")
    show_chart(fig, key, height)


# =========================================================
# LOAD DATA
# =========================================================
sales = clean_columns(load_table("Sales.csv"))
sku = clean_columns(load_table("SKU MASTER.csv"))
opening = parse_city_matrix("Opening Stock.csv", "Opening Stock")
transfer = load_transfer()
census = clean_columns(load_table("census2011.csv"))
districts = clean_columns(load_table("maharashtra-districts.csv"))
msme = clean_columns(load_table("district_level_total_Registered_msme.csv"))

if sales.empty:
    st.error("Sales.csv could not be loaded. Put it inside data/raw/ and restart the app.")
    st.stop()

# =========================================================
# SALES PREPARATION
# =========================================================
date_col = find_col(sales, ["Date", "transaction_date", "sales_date"])
sku_col = find_col(sales, ["SKU", "product_code", "item_code"])
product_col = find_col(sales, ["Product Name", "Product", "Description", "product_name"])
city_col = find_col(sales, ["City", "Location"])
sales_col = find_col(sales, ["Sales", "Quantity", "Units Sold", "Units", "Qty"])

if date_col:
    sales[date_col] = pd.to_datetime(sales[date_col], errors="coerce")
if sales_col:
    sales[sales_col] = safe_number(sales[sales_col])
else:
    sales["Sales"] = 0
    sales_col = "Sales"

if sku_col and not sku.empty:
    sku_key = find_col(sku, ["SKU", "product_code", "item_code"])
    category_col = find_col(sku, ["Category"])
    price_col = find_col(sku, ["Price", "Unit Price"])
    desc_col = find_col(sku, ["Description", "Product Name", "Product"])
    if sku_key:
        cols = [sku_key] + [c for c in [category_col, price_col, desc_col] if c and c != sku_key]
        sm = sku[cols].drop_duplicates(subset=[sku_key]).copy()
        rename = {}
        if category_col:
            rename[category_col] = "Category"
        if price_col:
            rename[price_col] = "Price"
        if desc_col:
            rename[desc_col] = "SKU Description"
        sm = sm.rename(columns=rename)
        for c in ["Category", "Price", "SKU Description"]:
            if c in sales.columns:
                sales = sales.drop(columns=c)
        sales = sales.merge(sm, left_on=sku_col, right_on=sku_key, how="left")

if "Category" not in sales.columns:
    sales["Category"] = "Unknown"
if "Price" not in sales.columns:
    sales["Price"] = 0
sales["Category"] = sales["Category"].fillna("Unknown").astype(str)
sales["Price"] = safe_number(sales["Price"])
sales["Revenue"] = sales[sales_col] * sales["Price"]

# =========================================================
# SIDEBAR FILTERS — SINGLE INSTANCE
# =========================================================
st.sidebar.title("🎛️ Dashboard Filters")
st.sidebar.caption("Filters apply to the retail sales analysis.")

available_cities = sorted(sales[city_col].dropna().astype(str).unique()) if city_col else []
selected_cities = st.sidebar.multiselect(
    "Select City",
    available_cities,
    default=available_cities,
    key="city_filter_main",
)

available_categories = sorted(sales["Category"].dropna().astype(str).unique())
selected_categories = st.sidebar.multiselect(
    "Select Category",
    available_categories,
    default=available_categories,
    key="category_filter_main",
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
        key="date_filter_main",
    )

filtered = sales.copy()
if city_col and selected_cities:
    filtered = filtered[filtered[city_col].astype(str).isin(selected_cities)]
if selected_categories:
    filtered = filtered[filtered["Category"].astype(str).isin(selected_categories)]
if date_col and selected_dates:
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start = pd.Timestamp(selected_dates[0])
        end = pd.Timestamp(selected_dates[1]) + pd.Timedelta(days=1)
        filtered = filtered[(filtered[date_col] >= start) & (filtered[date_col] < end)]
    else:
        d = pd.Timestamp(selected_dates)
        filtered = filtered[filtered[date_col].dt.date == d.date()]

# =========================================================
# HEADER
# =========================================================
st.title("🗺️ Retail & Geospatial Business Intelligence Dashboard")
st.markdown("**Retail Sales • Inventory • Logistics • MSME • Census • Maharashtra Geospatial Analysis**")
st.divider()

# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================
st.header("🏠 Executive Overview")
units = filtered[sales_col].sum()
revenue = filtered["Revenue"].sum()
product_count = filtered[sku_col].nunique() if sku_col and sku_col in filtered.columns else filtered[product_col].nunique() if product_col and product_col in filtered.columns else 0
city_count = filtered[city_col].nunique() if city_col and city_col in filtered.columns else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("🛒 Total Units Sold", f"{units:,.0f}")
c2.metric("💰 Total Revenue", f"₹{revenue:,.0f}")
c3.metric("📦 Products", f"{product_count:,}")
c4.metric("🏙️ Cities", f"{city_count:,}")

# =========================================================
# RETAIL INTELLIGENCE
# =========================================================
st.header("🛍️ Retail Intelligence")
r1, r2 = st.columns(2)
with r1:
    if date_col and not filtered.empty:
        daily = filtered.groupby(date_col, as_index=False)[sales_col].sum()
        fig = px.line(daily, x=date_col, y=sales_col, markers=True, title="Daily Sales Trend")
        show_chart(fig, "chart_daily_sales")
with r2:
    if city_col and not filtered.empty:
        city_sales = filtered.groupby(city_col, as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False)
        fig = px.bar(city_sales, x=city_col, y=sales_col, text=sales_col, title="City-wise Sales")
        show_chart(fig, "chart_city_sales")

r3, r4 = st.columns(2)
with r3:
    cat_sales = filtered.groupby("Category", as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False)
    fig = px.bar(cat_sales, x=sales_col, y="Category", orientation="h", text=sales_col, title="Category-wise Sales")
    show_chart(fig, "chart_category_sales")
with r4:
    if sku_col and not filtered.empty:
        top_sku = filtered.groupby(sku_col, as_index=False)[sales_col].sum().sort_values(sales_col, ascending=False).head(10)
        fig = px.bar(top_sku.sort_values(sales_col), x=sales_col, y=sku_col, orientation="h", text=sales_col, title="Top 10 Products / SKUs")
        show_chart(fig, "chart_top_skus")

# =========================================================
# GEOSPATIAL INTELLIGENCE
# =========================================================
st.header("🗺️ Geospatial Intelligence")
st.write("Retail performance is connected with city location to identify geographic concentration of demand and revenue.")

if city_col and not filtered.empty:
    geo = filtered.groupby(city_col).agg(Sales=(sales_col, "sum"), Revenue=("Revenue", "sum"), Products=(sku_col, "nunique") if sku_col else (sales_col, "count")).reset_index()
    geo = add_coordinates(geo, city_col)
    if not geo.empty:
        geo_bubble_map(geo, city_col, "Sales", "Retail Sales by City", "map_retail_sales", 540)
        st.subheader("📍 City-wise Geospatial Summary")
        st.dataframe(geo.sort_values("Sales", ascending=False), width="stretch")
    else:
        st.info("No city coordinates matched the selected retail cities.")

# =========================================================
# LOGISTICS
# =========================================================
st.header("🚚 Logistics & Stock Transfer Intelligence")

if not transfer.empty:
    st.info("Stock-transfer data is provided as city-wise SKU quantities by date for Pune, Aurangabad and Nashik. The source file has no explicit source/destination route fields, so routes are not invented.")

    transfer_city = transfer.groupby("City", as_index=False)["Transfer Quantity"].sum().sort_values("Transfer Quantity", ascending=False)
    transfer_sku = transfer.groupby("SKU", as_index=False)["Transfer Quantity"].sum().sort_values("Transfer Quantity", ascending=False)

    l1, l2, l3 = st.columns(3)
    l1.metric("Total Transfer Quantity", f"{transfer['Transfer Quantity'].sum():,.0f}")
    l2.metric("Cities Covered", f"{transfer['City'].nunique():,}")
    l3.metric("SKUs Covered", f"{transfer['SKU'].nunique():,}")

    a, b = st.columns(2)
    with a:
        fig = px.bar(transfer_city, x="City", y="Transfer Quantity", text="Transfer Quantity", title="City-wise Stock Transfer")
        show_chart(fig, "chart_transfer_city")
    with b:
        fig = px.bar(transfer_sku.head(10).sort_values("Transfer Quantity"), x="Transfer Quantity", y="SKU", orientation="h", text="Transfer Quantity", title="Top 10 SKUs by Transfer Quantity")
        show_chart(fig, "chart_transfer_sku")

    st.subheader("🗺️ Stock Transfer Intensity Map")
    geo_bubble_map(transfer_city, "City", "Transfer Quantity", "City-wise Stock Transfer Intensity", "map_transfer_intensity", 520)
    st.caption("Bubble size and intensity represent total transfer quantity. This is a city-level intensity map, not a route/network map.")

    with st.expander("📋 View Transfer Records"):
        st.dataframe(transfer.sort_values(["Date", "City", "SKU"]).head(200), width="stretch", height=420)
else:
    st.warning("STOCK TRANSFER dataset could not be loaded. Keep STOCK TRANSFER.csv or stock_transfer_cleaned.csv inside data/raw/.")

# =========================================================
# INVENTORY
# =========================================================
st.header("📦 Inventory Intelligence")
if not opening.empty:
    inv_city = opening.groupby("City", as_index=False)["Opening Stock"].sum().sort_values("Opening Stock", ascending=False)
    inv_sku = opening.groupby("SKU", as_index=False)["Opening Stock"].sum().sort_values("Opening Stock", ascending=False)
    i1, i2, i3 = st.columns(3)
    i1.metric("Opening Stock", f"{opening['Opening Stock'].sum():,.0f}")
    i2.metric("Cities Covered", f"{opening['City'].nunique():,}")
    i3.metric("SKUs Covered", f"{opening['SKU'].nunique():,}")
    q1, q2 = st.columns(2)
    with q1:
        fig = px.bar(inv_city, x="City", y="Opening Stock", text="Opening Stock", title="Opening Stock by City")
        show_chart(fig, "chart_opening_city")
    with q2:
        fig = px.bar(inv_sku.head(10).sort_values("Opening Stock"), x="Opening Stock", y="SKU", orientation="h", text="Opening Stock", title="Top 10 SKUs by Opening Stock")
        show_chart(fig, "chart_opening_sku")
    with st.expander("📋 View Opening Stock Records"):
        st.dataframe(opening.sort_values(["Date", "City", "SKU"]).head(200), width="stretch", height=420)
else:
    st.info("Opening Stock dataset could not be parsed.")

# =========================================================
# MSME / BUSINESS DENSITY
# =========================================================
st.header("🏢 MSME / Business Density Intelligence")
if not msme.empty:
    md = find_col(msme, ["district_name", "District", "District Name"])
    mv = find_col(msme, ["total", "Total", "Registered MSME", "MSME"])
    if md and mv:
        msme_plot = msme.copy()
        msme_plot[mv] = safe_number(msme_plot[mv])
        if "state_name" in msme_plot.columns:
            state = msme_plot["state_name"].astype(str).str.lower()
            if state.str.contains("maharashtra").any():
                msme_plot = msme_plot[state.str.contains("maharashtra")]
        msme_plot = msme_plot.groupby(md, as_index=False)[mv].sum().sort_values(mv, ascending=False).head(15)
        fig = px.bar(msme_plot.sort_values(mv), x=mv, y=md, orientation="h", text=mv, title="Top Districts by Registered MSMEs")
        show_chart(fig, "chart_msme_districts")
    else:
        st.info("MSME dataset loaded, but district/count fields could not be identified.")
else:
    st.info("MSME dataset not available.")

# =========================================================
# CENSUS / URBAN INTELLIGENCE
# =========================================================
st.header("🏙️ Census & Urban Intelligence")
if not census.empty:
    cdf = census.copy()
    if "State" in cdf.columns:
        state = cdf["State"].astype(str).str.lower()
        if state.str.contains("maharashtra").any():
            cdf = cdf[state.str.contains("maharashtra")]
    numeric = cdf.select_dtypes(include=np.number).columns.tolist()
    if numeric:
        indicator = st.selectbox("Select Census Indicator", numeric, key="census_indicator_main")
        summary = cdf[[indicator]].describe().T
        st.dataframe(summary, width="stretch")
        if "District" in cdf.columns:
            top_census = cdf[["District", indicator]].dropna().sort_values(indicator, ascending=False).head(15)
            fig = px.bar(top_census.sort_values(indicator), x=indicator, y="District", orientation="h", text=indicator, title=f"Top Districts by {indicator}")
            show_chart(fig, "chart_census_indicator")
    else:
        st.info("No numeric Census indicators were detected.")
else:
    st.info("Census dataset not available.")

# =========================================================
# LOCATION INTELLIGENCE
# =========================================================
st.header("📍 Location Intelligence")
st.write("Combines retail demand, revenue and product coverage at city level for business-location analysis.")
if city_col and not filtered.empty:
    agg = {"Units Sold": (sales_col, "sum"), "Revenue": ("Revenue", "sum")}
    if sku_col:
        agg["Products"] = (sku_col, "nunique")
    loc = filtered.groupby(city_col).agg(**agg).reset_index()
    loc["Revenue per Unit"] = loc["Revenue"] / loc["Units Sold"].replace(0, np.nan)
    st.dataframe(loc.sort_values("Revenue", ascending=False), width="stretch")

# =========================================================
# DATASET INFORMATION / METHODOLOGY
# =========================================================
with st.expander("📂 Dataset Information"):
    dataset_info = pd.DataFrame({
        "Dataset": ["Sales", "SKU Master", "Opening Stock", "Stock Transfer", "Census 2011", "Maharashtra Districts", "Registered MSME"],
        "Rows": [len(sales), len(sku), len(opening), len(transfer), len(census), len(districts), len(msme)],
        "Status": ["Loaded" if not x.empty else "Missing" for x in [sales, sku, opening, transfer, census, districts, msme]],
    })
    st.dataframe(dataset_info, width="stretch")

with st.expander("ℹ️ Project Methodology"):
    st.markdown(
        "**Data Preparation:** CSV datasets are cleaned, dates are standardized and numeric fields are converted safely.\n\n"
        "**Retail Analysis:** Sales are aggregated by date, city, category and SKU. Revenue is calculated using SKU price and units sold.\n\n"
        "**Geospatial Analysis:** City-level retail metrics are linked with city coordinates to visualize geographic concentration.\n\n"
        "**Logistics Analysis:** The stock-transfer matrix is reshaped into City–SKU–Date–Quantity records. Because source/destination fields are absent, no artificial route is created.\n\n"
        "**Inventory Analysis:** The opening-stock matrix is reshaped in the same way and summarized by city and SKU.\n\n"
        "**Business Context:** MSME and Census datasets provide district-level economic and demographic context for location intelligence."
    )

# =========================================================
# FILTERED DATA + FOOTER
# =========================================================
with st.expander("📋 View Filtered Sales Data"):
    st.dataframe(filtered, width="stretch", height=450)

st.divider()
st.caption("Retail & Geospatial Business Intelligence Dashboard | Streamlit • Python • Pandas • Plotly")
