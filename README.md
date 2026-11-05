# Healthcare Diagnostics Business Intelligence & Strategic Analytics

## Project Overview

This project presents an end-to-end business intelligence and strategic analytics solution for a fictional genomics-based healthcare diagnostics company operating in India.

The project simulates the analytical responsibilities of a Business Analyst working in the Corporate Development and Investor Relations function of a healthcare diagnostics organisation.

It combines Python-based data cleaning and statistical analysis, SQL-based business intelligence, financial forecasting, M&A target screening, and interactive Power BI dashboards to generate actionable business insights.

**Note:** All company names, transactions, financial figures, competitors, market estimates and acquisition targets used in this project are synthetic and created exclusively for portfolio and educational purposes. This project is not affiliated with or based on the actual internal data of MedGenome.

## Business Objectives

The project aims to:

- Evaluate revenue, profitability and financial performance.
- Compare actual financial performance against budgets.
- Analyse diagnostic test and centre-level performance.
- Identify operational inefficiencies, including failed orders and turnaround-time breaches.
- Assess geographic market opportunities.
- Benchmark competitors and pricing.
- Develop a revenue forecasting model.
- Screen potential acquisition targets using strategic and financial criteria.

## Tools and Technologies

| Tool | Application |
|---|---|
| Python | Data cleaning, exploratory analysis, statistical testing and forecasting |
| Pandas, NumPy | Data manipulation and analysis |
| Matplotlib, Seaborn | Data visualisation |
| SciPy | Statistical hypothesis testing |
| SQL (SQLite) | Database creation, joins, aggregations and window functions |
| Power BI | Interactive dashboards and DAX measures |
| Excel | Dataset preparation and financial data management |

## Project Workflow

### 1. Data Preparation and Cleaning — Python

- Imported and processed multiple datasets.
- Checked missing values, duplicate records and referential integrity.
- Validated revenue calculations and business rules.
- Identified turnaround-time outliers without automatically removing them.
- Created additional analytical variables, including gross profit, gross margin, turnaround-time breach flags and monthly identifiers.
- Exported cleaned datasets for further analysis.

### 2. Exploratory Data Analysis and Statistical Testing

Conducted exploratory analysis to understand financial and operational performance.

Key techniques included:

- Spearman correlation to examine the relationship between discounting and gross margin.
- Kruskal-Wallis testing to compare turnaround-time performance across groups.
- Chi-square testing to examine associations between referral channels and order failures.
- Revenue and profitability analysis across diagnostic categories and centres.

### 3. SQL Database and Business Analysis

Created a relational SQLite database using structured tables, primary keys and foreign keys.

Developed analytical SQL queries involving:

- Aggregations and conditional calculations.
- Common Table Expressions (CTEs).
- Joins and subqueries.
- Window functions such as `LAG()`, `ROW_NUMBER()` and `RANK()`.
- Rolling averages and cumulative revenue contributions.
- Financial-year and quarterly performance analysis.
- Data reconciliation between transaction-level and monthly financial records.

### 4. Revenue Forecasting

Developed and compared multiple forecasting approaches using historical monthly revenue data.

- Moving average forecasting.
- Linear trend forecasting.
- Seasonal naive forecasting.
- Trend and seasonality-based forecasting.

Models were evaluated using a six-month holdout period and Mean Absolute Percentage Error (MAPE).

The best-performing approach was selected based on backtesting performance.

### 5. M&A Target Screening

Developed an illustrative acquisition screening framework using weighted criteria:

- Strategic fit — 30%
- Capability fit — 25%
- Geographic fit — 15%
- EBITDA margin — 20%
- Market growth — 10%

Also conducted sensitivity analysis by changing the weighting of financial criteria.

Enterprise valuation ranges were estimated using an illustrative EBITDA multiple assumption.

### 6. Power BI Dashboard Development

Developed a three-page interactive dashboard.

**Page 1 — Executive Overview**
- Revenue and profitability KPIs.
- Gross and operating margins.
- Failed-order rate and turnaround-time breaches.
- Monthly revenue trends.
- Revenue contribution by diagnostic category.

**Page 2 — Financial Performance**
- Monthly actual versus budget revenue.
- Financial-year and quarterly performance.
- Gross profit and operating profit.
- Operating margin and budget variance.

**Page 3 — Centres and Operations**
- Revenue contribution by diagnostic centre.
- Centre-level gross margins.
- Failed-order rates.
- Turnaround-time breach rates.
- Indicative capacity utilisation.

## Key Business Insights

The synthetic dataset generated the following illustrative findings:

1. **Revenue and profitability:** Total revenue was approximately ₹8.03 crore, with a gross margin of approximately 61.5% and operating margin of approximately 19.7%.

2. **Budget performance:** Revenue was approximately 1.9% below budget.

3. **Diagnostic portfolio:** Three major diagnostic tests contributed approximately 51% of total revenue.

4. **Discounting:** Higher discount levels were associated with lower gross margins. The relationship should be interpreted as an association, not proof of causation.

5. **Operational performance:** Approximately 50% of completed orders breached their respective turnaround-time targets.

6. **Failed orders:** Approximately 6.3% of orders were unsuccessful, resulting in direct costs without corresponding revenue.

7. **Geographic opportunity:** Maharashtra emerged as the highest-scoring state in the illustrative market opportunity assessment.

8. **M&A screening:** Aarogya Genomics and Coastal Genomics emerged as leading acquisition candidates under different weighting assumptions.

## Business Recommendations

- Review discounting practices and introduce clearer discount controls.
- Investigate turnaround-time workflows and review target-setting procedures.
- Reduce failed orders through improved sample handling and operational controls.
- Prioritise geographic expansion based on market headroom and growth.
- Conduct detailed financial and strategic due diligence before pursuing acquisition opportunities.
- Strengthen repeat-client engagement and retention.

## Limitations and Assumptions

- The dataset is entirely synthetic and does not represent actual healthcare company performance.
- Market estimates and competitor information are illustrative assumptions.
- Capacity utilisation should be interpreted as a relative indicator because the sample transaction volume and estimated capacity are not representative of a real operating environment.
- Forecasts are based on historical synthetic data and are not guaranteed predictions.
- M&A valuation multiples are illustrative and would require validation using comparable transactions and detailed due diligence.
- Statistical associations do not necessarily establish causation.

## Project Structure

```text
medgenome_bi_project/
│
├── data/
│   ├── raw/
│   ├── clean/
│   └── raw/csv/
│
├── python/
│   ├── 00_export_raw.py
│   ├── 01_clean.py
│   ├── 02_eda.py
│   └── 03_forecast_ma.py
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_queries.sql
│   ├── 04_build_db.py
│   └── diagnostics.db
│
├── powerbi/
│   └── Healthcare_Diagnostics_Business_Analytics.pbix
│
├── docs/
│   └── charts/
│
└── README.md
```

*The structure above describes the intended organisation of the project; filenames can be adjusted to match the final repository.*

## Conclusion

This project demonstrates an end-to-end analytical workflow connecting healthcare diagnostics operations, financial performance, market assessment and strategic decision-making.

It combines technical skills in Python, SQL and Power BI with business-oriented analysis to translate operational and financial data into actionable recommendations.
