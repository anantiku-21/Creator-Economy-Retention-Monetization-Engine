# Creator Monetization & Viewer Retention Analytics

A Python-based analytics project that studies **viewer monetization, repeat purchasing, customer lifetime value (LTV), and retention** using 76K+ YouTube livestream events.

The project transforms raw livestream telemetry into user-level financial metrics and retention analysis, helping identify **high-value viewers, repeat-purchase behavior, monetization patterns, and customer churn**.

## Business Questions

* Which viewers contribute the most to total monetization?
* How frequently do paying viewers make repeat purchases?
* How does the probability of another purchase change over time?
* How concentrated is revenue among high-value viewers?
* What patterns can help understand viewer retention and monetization?

## Key Analysis

### Financial & Customer Metrics

Calculated user-level metrics including:

* Lifetime Value (LTV)
* Total transaction value
* Repeat-purchase rate
* Purchase frequency
* Expansion revenue
* Revenue contribution by viewer

### Repeat-Purchase Analysis

Used Pandas grouped `.shift()` operations to calculate the **time between consecutive purchases for individual viewers**, reproducing SQL-style window-function logic without a database.

### Retention & Survival Analysis

Implemented a **Kaplan--Meier estimator from scratch using NumPy and Pandas** to estimate the probability of repeat purchase over time and study microtransaction churn.

### Interactive Dashboard

Built a Streamlit dashboard with Plotly visualizations for:

* Revenue and transaction trends
* Viewer-level financial metrics
* Purchase frequency
* Inter-purchase intervals
* Retention and survival curves
* High-value viewer analysis

## Dataset

The analysis uses **76K+ raw YouTube livestream telemetry events**, including chat activity, tips, Super Chats, and sponsorship-related transactions.

The underlying dataset was independently collected and published on Kaggle under a **CC0 license** to support reproducible analysis.

**Dataset:**
[YouTube Livestream Microtransactions Dataset](https://www.kaggle.com/datasets/anantiku21/youtube-livestream-microtransactions-dataset)

## Tech Stack

* **Language:** Python
* **Data Analysis:** Pandas, NumPy
* **Statistical Analysis:** SciPy
* **Visualization:** Plotly
* **Dashboard:** Streamlit
* **Data Formats:** JSON, CSV

## Project Structure

```text
creator-economy-retention/
│
├── app.py
├── requirements.txt
├── README.md
│
└── data/
    ├── raw_transactions.json
    └── user_financial_metrics.csv
```

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/anantiku-21/creator-economy-retention.git
cd creator-economy-retention
```

### 2. Install dependencies

Python 3.8+ is recommended.

```bash
pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
streamlit run app.py
```

The application will open locally at:

```text
http://localhost:8501
```

## Project Outcome

The project demonstrates how raw event-level data can be converted into **customer, revenue, and retention metrics** and presented through an interactive dashboard to support **data-driven monetization and retention analysis**.
