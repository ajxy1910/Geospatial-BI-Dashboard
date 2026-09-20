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

The Logistics module analyzes stock transfer data.

The cleaned stock-transfer dataset contains:

- 3 cities
- 50 SKUs
- 30 dates
- 4,500 transfer records

The dashboard currently provides:

- Total Transfer Quantity
- Cities Covered
- SKUs Covered
- City-wise stock movement
- SKU-wise stock movement
- Stock transfer intensity visualization
- Transfer data table

### Current Dashboard Output

- **Total Transfer Quantity:** 163,780
- **Cities Covered:** 3
- **SKUs Covered:** 50

### Important Data Limitation

The source stock-transfer dataset does not explicitly provide source and destination fields.

Therefore, the dashboard does **not** create or assume artificial source-to-destination routes.

Instead, the project performs:

> **City-wise Stock Movement Analysis**

based on the available city, SKU, date and quantity information.

---

## 📦 4. Inventory Intelligence

The Inventory Intelligence module uses inventory-related datasets to provide stock analysis.

It includes:

- Opening stock analysis
- SKU-level stock information
- Stock-related KPIs
- Inventory visualization
- Product-level analysis

---

## 🏭 5. MSME Intelligence

The MSME module uses the available Maharashtra MSME dataset to provide business-related statistical analysis.

It supports:

- MSME-related data exploration
- Location-based analysis
- District-level information
- Interactive visualizations

---

## 🗺️ 6. Census & Location Intelligence

The project also integrates demographic and geographical datasets.

These datasets are used for:

- District-level analysis
- Population-related information
- Location analysis
- Geographical visualization
- Business-location context

---

# 🎛️ Interactive Filters

The dashboard provides interactive filters for data exploration.

Available filters include:

- City
- Category
- Date Range

Changing the filters dynamically updates the relevant dashboard visualizations.

---

# 📊 Dashboard Visualizations

The dashboard uses interactive visualizations for business analysis, including:

- Bar charts
- Line charts
- KPI cards
- Data tables
- Geographic visualizations
- Stock movement charts
- Category-wise analysis
- City-wise analysis
- SKU-level analysis

---

# 🗂️ Datasets

The project uses multiple datasets stored in the `data/raw/` directory.

## Main Datasets

```text
Sales.csv
SKU MASTER.csv
Opening Stock.csv
stock_transfer_cleaned.csv
census2011.csv
maharashtra-districts.csv
district_level_total_Registered_msme.csv

📁 Dataset Description
Sales.csv

Contains retail sales information used for:

Daily sales analysis
Revenue analysis
City-wise sales analysis
Category-wise analysis
Product/SKU-level analysis
Sales trend visualization
SKU MASTER.csv

Contains SKU/product master information used for:

Product identification
SKU-level analysis
Product-related business analysis
Opening Stock.csv

Contains opening inventory information used for:

Opening stock analysis
SKU-level inventory analysis
Inventory-related KPIs
Stock visualization
stock_transfer_cleaned.csv

This is the cleaned and structured stock-transfer dataset used by the dashboard.

The dataset contains:

3 Cities
50 SKUs
30 Dates
4,500 Transfer Records

The structured data contains:

City
SKU
Date
Quantity

This format allows the dashboard to perform city-wise, SKU-wise and date-wise stock movement analysis.

census2011.csv

Contains Census 2011-related demographic information used for supporting:

District-level analysis
Population-related analysis
Location-based analysis
maharashtra-districts.csv

Contains Maharashtra district geographical information used for:

Geospatial analysis
District-level mapping
Location visualization
Geographical business context
district_level_total_Registered_msme.csv

Contains district-level registered MSME information used for:

MSME analysis
District-level business context
Location-based analysis
Interactive visualization
🧹 Data Cleaning & Preprocessing

The project performs data preparation before using the datasets for dashboard analysis.

The preprocessing workflow includes:

Loading CSV datasets using Pandas
Cleaning dataset columns
Handling missing or unnecessary values
Converting dates into appropriate formats
Converting numerical fields into numeric data types
Standardizing city information
Preparing datasets for visualization
Transforming the original stock-transfer matrix into a structured dataset
🔄 Stock Transfer Data Transformation

The original STOCK TRANSFER.csv dataset was provided in a city-wise matrix format.

The original structure was not directly suitable for dashboard analysis because city, SKU, date and quantity information were arranged in a matrix-style format.

The data was therefore transformed into a structured format:

City | SKU | Date | Quantity

This cleaned dataset is stored as:

stock_transfer_cleaned.csv

The transformed dataset is used by the dashboard for:

Total transfer quantity
City-wise stock movement
SKU-wise stock movement
Date-wise stock movement
Transfer intensity analysis
🔐 Data Integrity

The project follows a data-integrity approach in which information is not artificially generated when it is unavailable in the source dataset.

The original stock-transfer data does not contain explicit:

Source City
Destination City

fields.

Therefore, the dashboard does not create artificial source-to-destination routes.

Instead, it performs:

City-wise Stock Movement Analysis

using the available:

City
SKU
Date
Quantity

This ensures that the dashboard analysis remains consistent with the available source data.

📊 Business Intelligence Analysis

The dashboard provides analysis across multiple business dimensions.

Retail Analysis
Total Units Sold
Total Revenue
Daily Sales
City-wise Sales
Category-wise Sales
Product/SKU-level Sales
Inventory Analysis
Opening Stock
SKU-level Stock
Product-level Inventory
Inventory-related KPIs
Logistics Analysis
Total Transfer Quantity
Cities Covered
SKUs Covered
City-wise Stock Movement
SKU-wise Stock Movement
Transfer Intensity
Geospatial Analysis
City-level business activity
Geographical distribution
Location-based analysis
Interactive geographical visualization
MSME & Demographic Analysis
District-level MSME information
Census information
Population-related information
Geographical business context
🗺️ Geospatial Analysis Workflow

The geospatial component follows the workflow:

Business Data
      ↓
City / District Information
      ↓
Geographical Data
      ↓
Latitude & Longitude
      ↓
Spatial Visualization
      ↓
Business Insights

The geospatial component helps connect business information with geographical locations.

It supports:

Location-based business analysis
City-wise analysis
District-level analysis
Interactive map visualization
Geographical comparison
🚚 Logistics Analysis Workflow

The logistics analysis follows:

STOCK TRANSFER.csv
        ↓
Data Cleaning
        ↓
Data Transformation
        ↓
City / SKU / Date / Quantity
        ↓
Aggregation
        ↓
Stock Movement Analysis
        ↓
Interactive Visualization

The dashboard uses the cleaned stock-transfer dataset for logistics-related analysis.

🎛️ Dashboard Filter Workflow

The dashboard provides interactive filtering through the Streamlit sidebar.

City Filter

Allows users to select one or multiple cities.

Category Filter

Allows users to select one or multiple product categories.

Date Range Filter

Allows users to select a date range for time-based analysis.

The selected filters dynamically affect the relevant dashboard analysis.

📈 Dashboard KPIs

The dashboard provides KPI cards to summarize important business information.

Retail KPIs
Total Units Sold
Total Revenue
Number of Products
Number of Cities
Logistics KPIs
Total Transfer Quantity
Cities Covered
SKUs Covered

The displayed values depend on the selected dataset and dashboard filters.

🛠️ Technology Stack
Programming Language
Python
Dashboard Framework
Streamlit
Data Processing
Pandas
NumPy
Data Visualization
Plotly
Geospatial Visualization
Plotly
Geographical coordinate data
Maharashtra district data
Development Tools
Visual Studio Code
Python Virtual Environment
Git
GitHub
📂 Project Structure
Geospatial-BI-Dashboard/
│
├── data/
│   ├── external/
│   ├── processed/
│   └── raw/
│       ├── Sales.csv
│       ├── SKU MASTER.csv
│       ├── Opening Stock.csv
│       ├── stock_transfer_cleaned.csv
│       ├── census2011.csv
│       ├── maharashtra-districts.csv
│       └── district_level_total_Registered_msme.csv
│
├── notebooks/
│
├── src/
│
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
⚙️ Installation & Setup
1. Clone the Repository
git clone https://github.com/ajxy1910/Geospatial-BI-Dashboard.git
2. Navigate to the Project Directory
cd Geospatial-BI-Dashboard
3. Create a Virtual Environment
python -m venv .venv
4. Activate the Virtual Environment
Windows
.venv\Scripts\activate
Linux / macOS
source .venv/bin/activate

5. Install Dependencies
pip install -r requirements.txt

### ▶️ Run the Application

After activating the virtual environment, run:

streamlit run app.py

The application will normally be available at:

http://localhost:8501
🔄 Git & GitHub

The project is maintained using Git and GitHub.

Basic Git Workflow
git status
git add .
git commit -m "Update dashboard"
git push origin main
Repository
https://github.com/ajxy1910/Geospatial-BI-Dashboard
🚀 Deployment

The Streamlit application can be deployed using a Streamlit-compatible cloud environment.

### The project requires:

GitHub repository
app.py
requirements.txt
Required datasets
Compatible Python environment

The application is designed to run as a Streamlit web application.

## 💡 Key Project Highlights

The project combines multiple analytical areas into a single dashboard:

Retail Sales
      +
Inventory
      +
Stock Transfer
      +
Logistics
      +
Geospatial Analysis
      +
MSME Data
      +
Census Data
      ↓
Business Intelligence Dashboard

### Major Highlights

Interactive dashboard
Retail sales analysis
Inventory analysis
Stock movement analysis
Geospatial visualization
MSME analysis
Census integration
City-wise analysis
SKU-level analysis
Category analysis
Interactive filters
KPI cards
Plotly visualizations
GitHub version control

## ⚠️ Data Limitations

The dashboard is based on the datasets available in the project.

Important limitations include:

The original stock-transfer dataset does not provide explicit source and destination cities.
Therefore, source-to-destination routes are not artificially generated.
Stock-transfer analysis is based on city, SKU, date and quantity.
Geospatial analysis depends on the geographical information available in the datasets.
Census and MSME datasets provide supporting geographical and business context.
Dashboard results depend on the quality and completeness of the source datasets.
🔮 Future Scope

The project can be extended with additional capabilities such as:

Real-time sales data integration
Real-time inventory monitoring
Automated data pipelines
Demand forecasting
Sales forecasting
Inventory replenishment recommendations
Route optimization when source and destination data becomes available
Delivery-time analysis
Customer segmentation
Advanced GIS analysis
Geospatial clustering
Machine Learning-based prediction
Automated business alerts
Database integration
Role-based access
Advanced analytics
🎓 Academic Project Information

Project Title:
Geospatial Business Intelligence Dashboard

Domain:
Business Intelligence / Retail Analytics / Logistics / Geospatial Analytics

Programming Language:
Python

Dashboard Framework:
Streamlit

Data Processing:
Pandas, NumPy

Visualization:
Plotly

Version Control:
Git & GitHub

📌 Project Status

Status: Completed Academic Project

The project currently includes:

Retail Intelligence
Geospatial Intelligence
Logistics & Stock Transfer Intelligence
Inventory Intelligence
MSME Intelligence
Census & Location Intelligence
Interactive filters
KPI cards
Interactive charts
Data tables
Stock movement analysis
Cleaned stock-transfer dataset
GitHub repository
Streamlit-compatible application

## 🏁 Conclusion

The Geospatial Business Intelligence Dashboard provides an interactive platform for analyzing retail, inventory, stock-transfer, logistics, geographical, MSME and demographic information.

By integrating multiple datasets into a single Streamlit application, the project provides a consolidated environment for exploring business performance across cities, categories, products, SKUs, dates and geographical locations.

The project demonstrates the practical implementation of:

Python
Pandas
NumPy
Streamlit
Plotly
Data Cleaning
Data Transformation
Business Intelligence
Geospatial Visualization
Interactive Dashboard Development

The stock-transfer component follows the actual structure of the available dataset. Since explicit source and destination fields are not available, the dashboard performs City-wise Stock Movement Analysis rather than creating unsupported transfer routes.

Overall, the project demonstrates an end-to-end Business Intelligence workflow starting from raw datasets, followed by data preprocessing, transformation, integration, analysis and interactive visualization.

## 👨‍💻 Author

Ajaykumar Nishad | Anand Sahani | Nikhil Prajapati

B.Tech Computer Science & Engineering (Data Science)

Lokmanya Tilak College of Engineering, Navi Mumbai

## 📜 License

This project is developed for academic and educational purposes.