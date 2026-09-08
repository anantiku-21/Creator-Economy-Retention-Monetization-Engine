"""
Creator Economy Microtransaction & Retention Engine
----------------------------------------------------
A pure-Python Streamlit dashboard. No JavaScript / Node.js anywhere.

Reads directly from the raw data files exported by the YouTube live-chat
scraper (raw_transactions.json) and the pre-computed financial rollup
(user_financial_metrics.csv) -- no database connection required, so this
runs anywhere Streamlit runs, including Streamlit Community Cloud.

Run locally with:   streamlit run app.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import expon

# ----------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Creator Economy Retention Engine",
    page_icon="📈",
    layout="wide",
)

DATA_DIR = Path(__file__).parent / "data"
TRANSACTIONS_PATH = DATA_DIR / "raw_transactions.json"
FINANCIALS_PATH = DATA_DIR / "user_financial_metrics.csv"


@st.cache_data
def load_transactions(path: Path) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    df = pd.DataFrame(raw)
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df.dropna(subset=["datetime"])


@st.cache_data
def load_financials(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data
def compute_inter_arrival(df: pd.DataFrame, max_gap_seconds: float) -> pd.DataFrame:
    """Recreates the SQL window-function step from the notebook in pandas:
    for each user, the time since their previous paid event."""
    paid = df[df["amount"] > 0].sort_values(["author", "datetime"]).copy()
    paid["prev_time"] = paid.groupby("author")["datetime"].shift(1)
    paid["seconds_since_last_txn"] = (
        paid["datetime"] - paid["prev_time"]
    ).dt.total_seconds()
    valid = paid.dropna(subset=["seconds_since_last_txn"])
    valid = valid[valid["seconds_since_last_txn"] < max_gap_seconds]
    return valid


def kaplan_meier(durations: np.ndarray) -> pd.DataFrame:
    """A minimal Kaplan-Meier estimator (no external survival-analysis
    package needed). Every row here is an *observed* repeat-purchase
    event, so this reduces to the empirical survival function, computed
    the KM way so it generalizes cleanly if censored data is added later."""
    durations = np.sort(durations)
    n = len(durations)
    unique_times, counts = np.unique(durations, return_counts=True)
    at_risk = n
    survival = 1.0
    rows = [(0.0, 1.0)]
    for t, d in zip(unique_times, counts):
        survival *= 1 - d / at_risk
        at_risk -= d
        rows.append((t, survival))
    return pd.DataFrame(rows, columns=["time", "survival"])


# ----------------------------------------------------------------------
# Sidebar controls
# ----------------------------------------------------------------------
st.sidebar.title("Controls")

if not TRANSACTIONS_PATH.exists() or not FINANCIALS_PATH.exists():
    st.error(
        "Data files not found. Place `raw_transactions.json` and "
        "`user_financial_metrics.csv` inside a `data/` folder next to this app."
    )
    st.stop()

max_gap_hours = st.sidebar.slider(
    "Max gap between purchases to count as 'repeat' (hours)",
    min_value=1,
    max_value=72,
    value=24,
    help="Matches the notebook's 24-hour outlier filter by default.",
)

txns = load_transactions(TRANSACTIONS_PATH)
fin = load_financials(FINANCIALS_PATH)

# ----------------------------------------------------------------------
# Header + top-line KPIs
# ----------------------------------------------------------------------
st.title("📈 Creator Economy Microtransaction & Retention Engine")
st.caption(
    "Live-chat monetization analytics: Super Chats, sponsorships and viewer "
    "financial retention — rebuilt as a single Python app (no JS/Node)."
)

paid_events = txns[txns["amount"] > 0]
total_revenue_inr_equiv = fin["lifetime_value"].sum()
paying_users = fin["user_id"].nunique()
repeat_buyers = (fin["total_purchases"] > 1).sum()
repeat_rate = repeat_buyers / paying_users if paying_users else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Paying viewers", f"{paying_users:,}")
k2.metric("Total Super Chat / tip events", f"{len(paid_events):,}")
k3.metric("Repeat-purchase rate", f"{repeat_rate:.1%}")
k4.metric("Total lifetime value (as recorded)", f"{total_revenue_inr_equiv:,.0f}")

st.divider()

tab_overview, tab_financials, tab_survival, tab_explorer = st.tabs(
    ["Overview", "Financial Metrics", "Retention / Survival Analysis", "Transaction Explorer"]
)

# ----------------------------------------------------------------------
# Tab 1: Overview
# ----------------------------------------------------------------------
with tab_overview:
    st.subheader("Event mix")
    type_counts = txns["type"].value_counts().reset_index()
    type_counts.columns = ["event_type", "count"]
    fig = go.Figure(
        go.Bar(x=type_counts["event_type"], y=type_counts["count"], marker_color="#4C78A8")
    )
    fig.update_layout(
        xaxis_title="Event type", yaxis_title="Count", height=400, margin=dict(t=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Super Chat volume over time")
    ts = (
        paid_events.set_index("datetime")
        .resample("5min")["amount"]
        .agg(["count", "sum"])
        .reset_index()
    )
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(x=ts["datetime"], y=ts["count"], mode="lines", name="# of Super Chats")
    )
    fig2.update_layout(
        xaxis_title="Time", yaxis_title="Super Chats per 5-min window", height=400, margin=dict(t=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

# ----------------------------------------------------------------------
# Tab 2: Financial metrics (from the CSV rollup)
# ----------------------------------------------------------------------
with tab_financials:
    st.subheader("Viewer lifetime value distribution")
    fig3 = go.Figure(go.Histogram(x=fin["lifetime_value"], nbinsx=40, marker_color="#F58518"))
    fig3.update_layout(
        xaxis_title="Lifetime value", yaxis_title="Number of viewers", height=400, margin=dict(t=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Top spenders")
    top_n = st.slider("Show top N spenders", 5, 50, 15)
    top_spenders = fin.sort_values("lifetime_value", ascending=False).head(top_n)
    fig4 = go.Figure(
        go.Bar(
            x=top_spenders["lifetime_value"],
            y=top_spenders["user_id"],
            orientation="h",
            marker_color="#54A24B",
        )
    )
    fig4.update_layout(
        xaxis_title="Lifetime value",
        yaxis_title="",
        height=max(400, top_n * 22),
        margin=dict(t=20),
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Expansion revenue (2nd+ tip growth)")
    expanders = fin[fin["expansion_revenue"] > 0]
    st.write(
        f"**{len(expanders):,}** viewers ({len(expanders)/len(fin):.1%} of all payers) "
        f"increased their spend after their first tip, contributing "
        f"**{expanders['expansion_revenue'].sum():,.0f}** in expansion revenue."
    )

    st.subheader("Raw financial data")
    st.dataframe(fin.sort_values("lifetime_value", ascending=False), use_container_width=True, height=350)

# ----------------------------------------------------------------------
# Tab 3: Survival / retention analysis (recreates the notebook, no DB needed)
# ----------------------------------------------------------------------
with tab_survival:
    st.subheader("Inter-arrival time between repeat purchases")
    valid = compute_inter_arrival(txns, max_gap_seconds=max_gap_hours * 3600)
    intervals = valid["seconds_since_last_txn"].astype(float)

    if len(intervals) < 2:
        st.warning("Not enough repeat-purchase pairs at this gap threshold to fit a model.")
    else:
        expected_time = intervals.mean()
        lambda_rate = 1 / expected_time

        c1, c2 = st.columns(2)
        c1.metric("Mean time between repeat purchases", f"{expected_time:,.0f} sec")
        c2.metric("Rate λ (purchases/sec)", f"{lambda_rate:.5f}")

        hist_fig = go.Figure()
        hist_fig.add_trace(
            go.Histogram(
                x=intervals,
                histnorm="probability density",
                nbinsx=30,
                name="Empirical data",
                marker_color="#4C78A8",
                opacity=0.6,
            )
        )
        x_axis = np.linspace(0, intervals.max(), 500)
        hist_fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=expon.pdf(x_axis, scale=expected_time),
                mode="lines",
                name="Exponential fit",
                line=dict(color="#E45756", width=3),
            )
        )
        hist_fig.update_layout(
            title="Probability distribution of inter-arrival times",
            xaxis_title="Seconds since previous transaction",
            yaxis_title="Probability density",
            height=420,
            margin=dict(t=40),
        )
        st.plotly_chart(hist_fig, use_container_width=True)

        st.subheader("Kaplan-Meier survival curve")
        km = kaplan_meier(intervals.to_numpy())
        median_row = km[km["survival"] <= 0.5].head(1)
        median_time = median_row["time"].iloc[0] if not median_row.empty else None

        km_fig = go.Figure()
        km_fig.add_trace(
            go.Scatter(
                x=km["time"],
                y=km["survival"],
                mode="lines",
                line=dict(shape="hv", color="#B279A2", width=3),
                name="Survival probability",
            )
        )
        km_fig.update_layout(
            title="Probability of NOT making another Super Chat over time",
            xaxis_title="Seconds after initial Super Chat",
            yaxis_title="Survival probability",
            height=420,
            margin=dict(t=40),
        )
        st.plotly_chart(km_fig, use_container_width=True)

        if median_time is not None:
            st.metric("Median time to next transaction", f"{median_time:,.0f} sec")
        else:
            st.info("Survival never drops to 50% within the observed window (retention is strong).")

# ----------------------------------------------------------------------
# Tab 4: Raw transaction explorer
# ----------------------------------------------------------------------
with tab_explorer:
    st.subheader("Browse raw chat / transaction events")
    col_a, col_b = st.columns(2)
    with col_a:
        event_types = st.multiselect(
            "Event type", options=sorted(txns["type"].dropna().unique()), default=["superChat"]
        )
    with col_b:
        search_user = st.text_input("Filter by author (partial match)", "")

    filtered = txns.copy()
    if event_types:
        filtered = filtered[filtered["type"].isin(event_types)]
    if search_user:
        filtered = filtered[filtered["author"].str.contains(search_user, case=False, na=False)]

    st.write(f"{len(filtered):,} events")
    st.dataframe(
        filtered[["datetime", "author", "message", "amount", "currency", "type"]],
        use_container_width=True,
        height=450,
    )

st.divider()
st.caption(
    "Built with Streamlit, Pandas and Plotly only — no JavaScript, no Node.js, "
    "no database connection required."
)
