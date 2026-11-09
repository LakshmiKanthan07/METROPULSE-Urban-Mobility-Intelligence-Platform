"""
METROPULSE — Static Figure Generator
Generates high-resolution PNG visualizations in reports/figures/
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.config.settings import DATA_PROCESSED, REPORTS_DIR

FIG_DIR = REPORTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Styling palette
BG_DARK = "#0a0f1e"
CARD_BG = "#111827"
TEXT_COLOR = "#f1f5f9"
GRID_COLOR = "#1e3a5f"
PRIMARY_BLUE = "#3b82f6"
ACCENT_CYAN = "#06b6d4"
ALERT_RED = "#ef4444"
SUCCESS_GREEN = "#10b981"

TFL_COLORS = {
    "Bakerloo": "#B36305",
    "Central": "#E32017",
    "District": "#00782A",
    "H&C and Circle": "#FFD300",
    "Jubilee": "#A0A5A9",
    "Metropolitan": "#9B0056",
    "Northern": "#000000",
    "Piccadilly": "#003688",
    "Victoria": "#0098D4",
    "Waterloo & City": "#95CDBA",
}

plt.rcParams.update({
    "figure.facecolor": BG_DARK,
    "axes.facecolor": CARD_BG,
    "axes.edgecolor": GRID_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "grid.linestyle": "--",
    "grid.alpha": 0.5,
})

def generate_all_figures():
    csv_dir = DATA_PROCESSED / "csv"

    # 1. Line Demand Rankings
    p_line = csv_dir / "demand_line_demand.csv"
    if p_line.exists():
        df_line = pd.read_csv(p_line)
        df_agg = df_line.groupby("line_name")["daily_boarders"].mean().reset_index()
        df_agg = df_agg.sort_values(by="daily_boarders", ascending=True)

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = [TFL_COLORS.get(name, PRIMARY_BLUE) for name in df_agg["line_name"]]
        bars = ax.barh(df_agg["line_name"], df_agg["daily_boarders"] / 1000, color=colors, edgecolor=GRID_COLOR)
        ax.set_title("Average Daily Boarders by London Underground Line (Thousands)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Daily Boarders (in Thousands)")
        ax.grid(True, axis="x")
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 10, bar.get_y() + bar.get_height()/2, f"{w:.1f}k", va="center", color=TEXT_COLOR, fontsize=10, fontweight="bold")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "line_demand_rankings.png", dpi=300)
        plt.close()
        print("Generated: line_demand_rankings.png")

    # 2. Top Stations Demand
    p_stat = csv_dir / "demand_station_demand.csv"
    if p_stat.exists():
        df_stat = pd.read_csv(p_stat)
        df_top = df_stat.groupby(["asc", "station"])["daily_entries"].mean().reset_index()
        df_top = df_top.sort_values(by="daily_entries", ascending=False).head(15).iloc[::-1]

        fig, ax = plt.subplots(figsize=(10, 7))
        bars = ax.barh(df_top["station"], df_top["daily_entries"] / 1000, color=ACCENT_CYAN, edgecolor=GRID_COLOR)
        ax.set_title("Top 15 Busiest London Underground Stations (Average Daily Entries)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Daily Entries (Thousands)")
        ax.grid(True, axis="x")
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, f"{w:.1f}k", va="center", color=TEXT_COLOR, fontsize=10)
        plt.tight_layout()
        plt.savefig(FIG_DIR / "top_stations_demand.png", dpi=300)
        plt.close()
        print("Generated: top_stations_demand.png")

    # 3. 15-Minute Time-of-Day Curve
    p_time = csv_dir / "demand_time_profile.csv"
    if p_time.exists():
        df_time = pd.read_csv(p_time)
        df_twt = df_time[df_time["day_type"] == "TWT"].groupby(["time_interval", "start_minute"])["passengers"].sum().reset_index()
        df_twt = df_twt.sort_values("start_minute")

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df_twt["start_minute"] / 60, df_twt["passengers"] / 1000, color=PRIMARY_BLUE, lw=2.5, label="Midweek (TWT)")
        ax.fill_between(df_twt["start_minute"] / 60, 0, df_twt["passengers"] / 1000, color=PRIMARY_BLUE, alpha=0.25)
        ax.set_title("London Underground System-Wide 15-Minute Passenger Demand Profile", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Hour of Day (24-hour clock)")
        ax.set_ylabel("Total Passengers per 15-min (Thousands)")
        ax.set_xlim(5, 24)
        ax.axvspan(7.5, 8.75, color=ALERT_RED, alpha=0.15, label="AM Peak (07:30 - 08:45)")
        ax.axvspan(17.25, 18.75, color="#f59e0b", alpha=0.15, label="PM Peak (17:15 - 18:45)")
        ax.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR)
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(FIG_DIR / "time_of_day_profile.png", dpi=300)
        plt.close()
        print("Generated: time_of_day_profile.png")

    # 4. Weekday vs Weekend Profile Comparison
    if p_time.exists():
        df_time = pd.read_csv(p_time)
        fig, ax = plt.subplots(figsize=(12, 6))
        for dt, col, lbl in [("TWT", PRIMARY_BLUE, "Midweek (TWT)"), ("SAT", SUCCESS_GREEN, "Saturday"), ("SUN", "#a855f7", "Sunday")]:
            sub = df_time[df_time["day_type"] == dt].groupby("start_minute")["passengers"].sum().reset_index().sort_values("start_minute")
            if not sub.empty:
                ax.plot(sub["start_minute"] / 60, sub["passengers"] / 1000, color=col, lw=2.2, label=lbl)

        ax.set_title("Weekday vs. Weekend Passenger Demand Dynamics", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Hour of Day")
        ax.set_ylabel("Passengers per 15-min (Thousands)")
        ax.set_xlim(5, 24)
        ax.legend(facecolor=CARD_BG, edgecolor=GRID_COLOR)
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(FIG_DIR / "weekday_vs_weekend.png", dpi=300)
        plt.close()
        print("Generated: weekday_vs_weekend.png")

    # 5. ML Model Performance Comparison
    p_ml = csv_dir / "ml_demand_model_results.csv"
    if p_ml.exists():
        df_ml = pd.read_csv(p_ml)
        df_avg = df_ml.groupby("model")[["mae", "rmse", "r2"]].mean().reset_index()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        ax1.bar(df_avg["model"], df_avg["mae"], color=PRIMARY_BLUE, edgecolor=GRID_COLOR)
        ax1.set_title("Mean Absolute Error (Lower is Better)", fontweight="bold")
        ax1.set_ylabel("MAE (Passengers)")
        ax1.grid(True, axis="y")

        ax2.bar(df_avg["model"], df_avg["r2"], color=SUCCESS_GREEN, edgecolor=GRID_COLOR)
        ax2.set_title("Out-of-Sample R² Score (Higher is Better)", fontweight="bold")
        ax2.set_ylabel("R² Score")
        ax2.set_ylim(0.85, 1.0)
        ax2.grid(True, axis="y")

        plt.suptitle("Leave-One-Year-Out Cross-Validation Benchmark", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plt.savefig(FIG_DIR / "ml_model_benchmark.png", dpi=300)
        plt.close()
        print("Generated: ml_model_benchmark.png")

    # 6. Service Adequacy Index Distribution
    p_sai = csv_dir / "service_adequacy.csv"
    if p_sai.exists():
        df_sai = pd.read_csv(p_sai)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df_sai["service_adequacy_index"], bins=30, kde=True, color=ALERT_RED, ax=ax, edgecolor=GRID_COLOR)
        ax.set_title("Distribution of Service Adequacy Deficit Index (SAI)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Service Adequacy Index (Higher = Severe Capacity Deficit)")
        ax.set_ylabel("Frequency (Link-Intervals)")
        ax.grid(True)
        plt.tight_layout()
        plt.savefig(FIG_DIR / "service_adequacy_index.png", dpi=300)
        plt.close()
        print("Generated: service_adequacy_index.png")

    print("All figures successfully created in reports/figures/")

if __name__ == "__main__":
    generate_all_figures()
