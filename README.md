# 🌍 Geospatial Business Intelligence Dashboard

## 📌 Project Overview

The **Geospatial Business Intelligence Dashboard** is an interactive Business Intelligence application developed using **Python and Streamlit**.

The project combines retail sales, inventory, stock transfer, geospatial, MSME and demographic datasets into a unified dashboard. It enables users to explore business performance through interactive filters, KPIs, charts, tables and location-based visualizations.

The dashboard is designed to provide a consolidated view of business data and support data-driven analysis through interactive visual analytics.

---

## 🎯 Problem Statement

Business data is often available in multiple datasets such as sales, inventory, stock movement, demographic information and MSME statistics.

Analyzing these datasets separately makes it difficult to obtain a consolidated understanding of:

- Sales performance
- City-wise business activity
- Product and category performance
- Inventory position
- Stock movement
- Geographical distribution
- MSME activity
- Demographic and location-based information

This project addresses the problem by integrating these datasets into a single interactive Business Intelligence dashboard.

---

## 🎯 Objectives

The main objectives of this project are:

1. To develop an interactive Business Intelligence dashboard.
2. To analyze retail sales performance.
3. To visualize city-wise business activity.
4. To provide geographical visualization of business data.
5. To analyze stock transfer and movement data.
6. To provide inventory-related insights.
7. To analyze MSME-related data.
8. To integrate demographic and location-based datasets.
9. To provide interactive filtering using city, category and date.
10. To present business information through clear and interactive visualizations.

---

# 🚀 Key Features

## 🛒 1. Retail Intelligence

The Retail Intelligence module provides analysis of retail sales data.

It includes:

- Daily sales analysis
- City-wise sales analysis
- Category-wise sales analysis
- Revenue analysis
- Product/SKU-level analysis
- Top-performing products
- Interactive sales visualizations

---

## 🌍 2. Geospatial Intelligence

The Geospatial Intelligence module provides location-based visualization of business information.

It allows analysis of:

- City-wise business activity
- Geographic distribution
- Location-based sales information
- Interactive map-based visualization

The geographical visualization helps understand the spatial distribution of business activity.

---

## 🚚 3. Logistics & Stock Transfer Intelligence

The Logistics & Stock Transfer module analyzes the available stock-transfer dataset.

The cleaned stock-transfer dataset contains:

- 3 cities
- 50 SKUs
- 30 dates
- 4,500 transfer records

The dashboard provides:

- Total Transfer Quantity
- Cities Covered
- SKUs Covered
- City-wise stock movement
- SKU-wise stock movement
- Stock transfer intensity visualization
- Transfer data table

### Current Dashboard Output

The current dashboard output includes:

- **Total Transfer Quantity:** 163,780
- **Cities Covered:** 3
- **SKUs Covered:** 50

### Important Data Limitation

The original stock-transfer dataset is provided in a city-wise matrix format.

The available data contains city, SKU, date and quantity information but does not explicitly provide source and destination fields.

Therefore, the dashboard does **not** create or assume artificial source-to-destination routes.

Instead, the project performs:

**City-wise Stock Movement Analysis**

based on the available source data.

---

## 📦 4. Inventory Intelligence

The Inventory Intelligence module uses the Opening Stock dataset to provide inventory-related analysis.

It provides information related to:

- Opening stock records
- City-wise stock
- SKU-level stock
- Date-wise stock information
- Product-level inventory
- Inventory-related KPIs

The dashboard displays the available inventory information from the source dataset.

---

## 🏭 5. MSME Intelligence

The MSME Intelligence module uses the available Maharashtra MSME dataset to provide business-related statistical analysis.

It supports:

- MSME-related data exploration
- Location-based analysis
- District-level information
- Interactive visualizations

---

## 🗺️ 6. Census & Location Intelligence

The project integrates demographic and geographical datasets.

These datasets are used for:

- District-level analysis
- Population-related information
- Location analysis
- Geographical visualization
- Business-location context

---

# 🎛️ 7. Interactive Filters

The dashboard provides interactive filters for data exploration.

Available filters include:

- City
- Category
- Date Range

Changing the filters dynamically updates the relevant dashboard visualizations.

---

# 📊 8. Dashboard Visualizations

The dashboard uses interactive visualizations for business analysis, including:

- KPI cards
- Bar charts
- Line charts
- Geographic visualizations
- Stock movement charts
- Category-wise analysis
- City-wise analysis
- SKU-level analysis
- Interactive data tables

The visualizations are designed to make business information easier to understand and explore.

---

# 📈 9. Business Intelligence Analysis

The dashboard provides analysis across multiple business dimensions.

### Retail Analysis

- Total Units Sold
- Total Revenue
- Daily Sales
- City-wise Sales
- Category-wise Sales
- Product/SKU-level Sales

### Inventory Analysis

- Opening Stock
- SKU-level Stock
- Product-level Inventory
- Inventory-related KPIs

### Logistics Analysis

- Total Transfer Quantity
- Cities Covered
- SKUs Covered
- City-wise Stock Movement
- SKU-wise Stock Movement
- Transfer Intensity

### Geospatial Analysis

- City-level business activity
- Geographical distribution
- Location-based analysis
- Interactive geographical visualization

### MSME & Demographic Analysis

- District-level MSME information
- Census information
- Location-based demographic context

---

# 🗂️ 10. Datasets

The project uses multiple datasets stored in the `data/raw/` directory.

### Main Datasets

```text
Sales.csv
SKU MASTER.csv
Opening Stock.csv
stock_transfer_cleaned.csv
census2011.csv
maharashtra-districts.csv
district_level_total_Registered_msme.csv
```

### Dataset Description

#### Sales.csv

Contains retail sales information used for:

- Daily sales analysis
- Revenue analysis
- City-wise sales analysis
- Category-wise sales analysis
- Product/SKU-level analysis
- Sales trend visualization

#### SKU MASTER.csv

Contains product and SKU master information used for:

- Product identification
- SKU-level analysis
- Product-level mapping
- Category analysis

#### Opening Stock.csv

Contains opening inventory information used for:

- Opening stock analysis
- City-wise stock analysis
- SKU-level inventory analysis
- Inventory-related KPIs

#### stock_transfer_cleaned.csv

Contains cleaned stock-transfer information structured by:

- City
- SKU
- Date
- Quantity

The dataset is used for city-wise and SKU-wise stock movement analysis.

#### census2011.csv

Contains census-related information used for demographic and geographical analysis.

#### maharashtra-districts.csv

Contains Maharashtra district geographical information used for location-based visualization.

#### district_level_total_Registered_msme.csv

Contains district-level registered MSME information used for MSME analysis.

---

# 🧹 11. Data Cleaning & Preparation

The project uses data preprocessing before performing dashboard analysis.

The general data preparation workflow includes:

1. Loading the source datasets.
2. Inspecting dataset structure.
3. Handling missing or invalid values where required.
4. Standardizing column names.
5. Converting date columns into appropriate date formats.
6. Converting numerical fields into appropriate data types.
7. Preparing datasets for visualization.
8. Cleaning and structuring stock-transfer data.
9. Preparing geographical information for mapping.
10. Using the cleaned datasets for dashboard analysis.

The stock-transfer data was transformed into a structured format containing:

```text
City
SKU
Date
Quantity
```

This structured format allows efficient analysis of stock movement by city, SKU and date.

---

# 🔄 12. Stock Transfer Data Transformation

The original stock-transfer data was provided in a city-wise matrix format.

For dashboard analysis, it was converted into a cleaned structured dataset containing:

```text
City
SKU
Date
Quantity
```

This transformation allows the dashboard to perform:

- City-wise stock movement analysis
- SKU-wise stock movement analysis
- Date-wise stock analysis
- Quantity-based transfer analysis
- Transfer intensity visualization

The transformation preserves the information available in the original dataset without inventing source or destination routes.

---

# 🗺️ 13. Geospatial Analysis

The dashboard includes geospatial analysis using available geographical information.

The geospatial component supports:

- City-level analysis
- District-level information
- Geographic distribution
- Location-based business analysis
- Interactive map visualization

Geographical datasets are used to provide additional context to business and demographic information.

---

# 📊 14. KPI Analysis

The dashboard presents important business indicators through KPI cards.

Examples include:

### Retail KPIs

- Total Units Sold
- Total Revenue
- Sales Performance

### Inventory KPIs

- Opening Stock
- Available Inventory Information
- SKU Coverage

### Logistics KPIs

- Total Transfer Quantity
- Cities Covered
- SKUs Covered

The KPI values are generated from the available datasets and dashboard filters.

---

# 🔍 15. Interactive Data Exploration

The dashboard allows users to interact with the available business data.

Users can select:

- Cities
- Categories
- Date ranges

The selected filters are applied to the relevant analysis and visualizations.

This allows users to explore specific portions of the dataset without modifying the original source files.

---

# 🛠️ 16. Technology Stack

### Programming Language

- Python

### Dashboard Framework

- Streamlit

### Data Processing

- Pandas
- NumPy

### Data Visualization

- Plotly

### Geospatial Analysis

- Geographical datasets
- Interactive map visualizations

### Development Tools

- Visual Studio Code
- Git
- GitHub
- Python Virtual Environment

---

# 📁 17. Project Structure

The project follows the following structure:

```text
Geospatial-BI-Dashboard/
│
├── data/
│   ├── external/
│   ├── processed/
│   └── raw/
│       ├── census2011.csv
│       ├── district_level_total_Registered_msme.csv
│       ├── maharashtra-districts.csv
│       ├── Opening Stock.csv
│       ├── Sales.csv
│       ├── SKU MASTER.csv
│       └── stock_transfer_cleaned.csv
│
├── notebooks/
│
├── src/
│
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

---

# ⚙️ 18. Installation & Setup

## 18.1 Clone the Repository

```bash
git clone https://github.com/ajxy1910/Geospatial-BI-Dashboard.git
```

## 18.2 Navigate to the Project Directory

```bash
cd Geospatial-BI-Dashboard
```

## 18.3 Create a Virtual Environment

```bash
python -m venv .venv
```

## 18.4 Activate the Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 18.5 Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ 19. Run the Application

After activating the virtual environment and installing the dependencies, run:

```bash
streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

The Streamlit dashboard will open in the browser.

---

# 🔧 20. Git & GitHub

The project is maintained using Git and GitHub.

The repository contains:

- Source code
- Dashboard application
- Dataset files
- Requirements file
- Project documentation

The project can be updated using the standard Git workflow:

```bash
git status
git add .
git commit -m "Update dashboard"
git push origin main
```

---

# ☁️ 21. Deployment

The Streamlit application can be deployed using a Streamlit-compatible cloud environment.

The deployment requires:

- GitHub repository
- `app.py`
- `requirements.txt`
- Required datasets
- Compatible Python environment

The application is designed to run as a Streamlit web application.

---

# 💡 22. Key Project Highlights

The project combines multiple analytical areas into a single Business Intelligence dashboard:

- Retail Sales
- Inventory
- Stock Transfer
- Logistics
- Geospatial Analysis
- MSME Data
- Census and Demographic Information

The project demonstrates the practical implementation of:

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Data Cleaning
- Data Transformation
- Business Intelligence
- Geospatial Visualization
- Interactive Dashboard Development

---

# 📌 23. Data Integrity & Limitations

The dashboard is designed to remain consistent with the available source datasets.

Important considerations:

- The dashboard does not invent unavailable business information.
- Stock-transfer routes are not artificially created.
- Source and destination fields are not assumed when they are absent from the dataset.
- Geographical analysis is based on the available geographical information.
- Dashboard results depend on the quality and structure of the source datasets.
- Filtered results change according to the selected dashboard filters.

The stock-transfer component follows the actual structure of the available dataset.

Since explicit source and destination fields are not available, the dashboard focuses on **city-wise stock movement analysis** rather than assumed route-level transfer analysis.

---

# 🎓 24. Academic Project

This project was developed as an academic and educational Business Intelligence project.

It demonstrates an end-to-end workflow starting from raw datasets and progressing through:

```text
Raw Data
   ↓
Data Cleaning
   ↓
Data Transformation
   ↓
Data Analysis
   ↓
Business Intelligence
   ↓
Interactive Visualization
   ↓
Streamlit Dashboard
```

The project provides practical experience in handling multiple datasets and integrating them into a unified analytical dashboard.

---

# 👨‍💻 25. Authors

**Ajaykumar Nishad**  
**Anand Sahani**  
**Nikhil Prajapati**

**B.Tech Computer Science & Engineering (Data Science)**

**Lokmanya Tilak College of Engineering, Navi Mumbai**

---

# 📜 License

This project is developed for academic and educational purposes.

---

# ✅ Conclusion

The **Geospatial Business Intelligence Dashboard** provides a unified platform for analyzing retail sales, inventory, stock movement, logistics, geographical information, MSME data and demographic information.

The project demonstrates how multiple datasets can be cleaned, transformed and integrated into an interactive Business Intelligence application using Python, Pandas, Plotly and Streamlit.

The dashboard provides interactive filters, KPI indicators, charts, tables and geographical visualizations to support business data exploration.

The stock-transfer analysis follows the structure of the available source data and focuses on city-wise stock movement without creating unsupported source-to-destination routes.

Overall, the project demonstrates an end-to-end Business Intelligence workflow from **raw data to interactive dashboard visualization**.