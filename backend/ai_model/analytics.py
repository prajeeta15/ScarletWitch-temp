import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import numpy as np
import os

LOG_FILE = "threat_alerts.log"


def load_data(log_file=LOG_FILE):
    """Loads threat alert logs and prepares the dataset."""
    if not os.path.exists(log_file):
        print("⚠️ No log file found! Creating a new one.")
        return pd.DataFrame(columns=["Date", "Message", "Score"])

    df = pd.read_csv(log_file, delimiter="|", names=["Date", "Message", "Score"],
                     parse_dates=["Date"], skipinitialspace=True)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df.set_index("Date", inplace=True)

    return df


def predict_future_threats(df, days_ahead=7):
    """Predicts future threats using Linear Regression."""
    if df.empty:
        print("⚠️ No data available for prediction.")
        return []

    df["Count"] = 1  # Every log entry is a threat event
    daily_counts = df.resample("D").sum().reset_index()

    daily_counts["DayNum"] = (
        daily_counts["Date"] - daily_counts["Date"].min()).dt.days
    X = daily_counts["DayNum"].values.reshape(-1, 1)
    y = daily_counts["Count"].values

    model = LinearRegression()
    model.fit(X, y)

    future_dates = [df.index.max() + timedelta(days=i)
                    for i in range(1, days_ahead + 1)]
    future_days = [(date - daily_counts["Date"].min()
                    ).days for date in future_dates]
    predicted_counts = model.predict(
        np.array(future_days).reshape(-1, 1)).astype(int)

    future_logs = [{"Date": future_dates[i].strftime("%Y-%m-%d %H:%M:%S"),
                    "Message": "Predicted threat",
                    "Score": predicted_counts[i]} for i in range(days_ahead)]

    return future_logs


def append_predictions_to_log(future_logs, log_file=LOG_FILE):
    """Appends predicted threats to the log file."""
    if not future_logs:
        return

    with open(log_file, "a") as file:
        for entry in future_logs:
            file.write(
                f"{entry['Date']} | {entry['Message']} | {entry['Score']}\n")

    print(f"✅ {len(future_logs)} predicted threats added to {log_file}!")


def plot_heatmap(df):
    """Generates a heatmap of threats over time."""
    df["Hour"] = df.index.hour
    df["Day"] = df.index.date

    heatmap_data = df.pivot_table(
        values="Score", index="Hour", columns="Day", aggfunc="count").fillna(0)

    plt.figure(figsize=(12, 6))
    sns.heatmap(heatmap_data, cmap="coolwarm", linewidths=0.5, annot=True)
    plt.title("Threat Heatmap (Hourly Distribution)")
    plt.xlabel("Date")
    plt.ylabel("Hour of the Day")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("threat_heatmap.png")
    plt.show()

    print("✅ Heatmap saved as 'threat_heatmap.png'.")


def plot_threat_trends(df, future_logs):
    """Generates threat trends, past & future predictions."""
    df["Count"] = 1
    daily_counts = df.resample("D").sum()

    past_7_days = daily_counts.loc[daily_counts.index.max(
    ) - timedelta(days=7):daily_counts.index.max()]
    future_dates = [datetime.strptime(
        log["Date"], "%Y-%m-%d %H:%M:%S") for log in future_logs]
    future_scores = [log["Score"] for log in future_logs]

    plt.figure(figsize=(12, 6))

    if not past_7_days.empty:
        plt.plot(past_7_days.index, past_7_days["Count"], marker="o",
                 linestyle="-", color="green", label="Past 7 Days")

    plt.plot(daily_counts.index, daily_counts["Count"], marker="o",
             linestyle="-", color="red", label="Recorded Threats")

    if future_logs:
        plt.plot(future_dates, future_scores, marker="o",
                 linestyle="--", color="blue", label="Predicted Threats")

    plt.title("Daily Threat Trends (Past, Present & Predictions)")
    plt.xlabel("Date")
    plt.ylabel("Number of Threats")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.savefig("threat_trends.png")
    plt.show()

    print("✅ Threat trends graph saved as 'threat_trends.png'.")


def plot_threat_distribution(df):
    """Displays a histogram of threat scores."""
    plt.figure(figsize=(10, 5))
    sns.histplot(df["Score"].astype(float), bins=10, kde=True, color="red")
    plt.title("Threat Score Distribution")
    plt.xlabel("Threat Score")
    plt.ylabel("Frequency")
    plt.grid()
    plt.savefig("threat_distribution.png")
    plt.show()

    print("✅ Threat distribution histogram saved as 'threat_distribution.png'.")


def plot_hourly_threats(df):
    """Visualizes threats at different hours of the day."""
    df["Hour"] = df.index.hour
    hourly_counts = df.groupby("Hour").size()

    plt.figure(figsize=(10, 5))
    plt.bar(hourly_counts.index, hourly_counts.values,
            color="purple", alpha=0.7)
    plt.title("Hourly Threat Activity")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Threat Count")
    plt.xticks(range(0, 24))
    plt.grid()
    plt.savefig("hourly_threats.png")
    plt.show()

    print("✅ Hourly threat activity graph saved as 'hourly_threats.png'.")


def generate_threat_analytics(log_file=LOG_FILE, days_ahead=7):
    """Generates various threat visualizations including heatmaps, trends, and distributions."""
    df = load_data(log_file)

    future_logs = predict_future_threats(df, days_ahead)
    append_predictions_to_log(future_logs, log_file)

    df = load_data(log_file)

    plot_threat_trends(df, future_logs)
    plot_heatmap(df)
    plot_threat_distribution(df)
    plot_hourly_threats(df)


# Run the analytics
generate_threat_analytics()
