# Creator Economy Retention & Monetization Engine
An interactive, pure-Python dashboard designed to analyze microtransaction velocity, viewer retention, and lifetime value (LTV) within live-stream creator economies. 
Built with Streamlit, Pandas, and Plotly, this project processes raw chat telemetry to extract actionable business insights—mirroring the analytical workflows used in live-service gaming economies.

## Core Features
*   **Zero-Database Architecture:** Reads directly from raw JSON exports and pre-computed CSV rollups, eliminating the need for local SQL databases or hardcoded credentials.
*   **Financial Rollups:** Calculates key live-service metrics including Lifetime Value (LTV), Repeat-Purchase Rates, and Expansion Revenue from over 76,000 telemetry events.
*   **Inter-arrival Time Analysis:** Utilizes Pandas to recreate SQL window functions, calculating the exact time delta between repeat purchases for individual users.
*   **Survival Analysis:** Implements a streamlined Kaplan-Meier estimator (without relying on heavy external libraries like `lifelines`) to model user churn and project the probability of repeat microtransactions over time.
*   **Interactive Visualizations:** Employs Plotly to generate clear, stakeholder-ready histograms, time-series line charts, and survival curves.

## Tech Stack
*   **Language:** Python
*   **Data Manipulation:** Pandas, NumPy
*   **Statistical Modeling:** SciPy (Exponential Distribution)
*   **Visualization:** Plotly
*   **Frontend:** Streamlit

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/<your-username>/creator-economy-retention.git
    cd creator-economy-retention
    ```

2.  **Install dependencies:**
    Ensure you have Python 3.8+ installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application locally:**
    ```bash
    streamlit run app.py
    ```

4.  **Access the Dashboard:**
    Open your browser and navigate to the URL provided in the terminal (typically `http://localhost:8501`).

## Data Structure
The application expects data to be located in a `data/` directory adjacent to `app.py`.
*   `data/raw_transactions.json`: Contains the raw telemetry events (e.g., chat messages, tips, super chats).
*   `data/user_financial_metrics.csv`: Contains the aggregated user-level financial data.)*


## Data Source
The raw JSON extraction is hosted as a public CC0 dataset on Kaggle. 
[Access the YouTube Livestream Microtransactions Dataset Here](https://www.kaggle.com/datasets/anantiku21/youtube-livestream-microtransactions-dataset)
