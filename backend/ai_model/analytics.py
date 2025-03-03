import pandas as pd
import matplotlib.pyplot as plt
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

    # Read log file
    df = pd.read_csv(log_file, delimiter="|", names=[
                     "Date", "Message", "Score"], parse_dates=["Date"], skipinitialspace=True)

    # Ensure Date column is parsed correctly
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)

    # Set Date as index
    df.set_index("Date", inplace=True)

    return df


def predict_future_threats(df, days_ahead=7):
    """Predicts future threats using Linear Regression."""
    if df.empty:
        print("⚠️ No data available for prediction.")
        return []

    df["Count"] = 1  # Every log entry is a threat event
    daily_counts = df.resample("D").sum().reset_index()

    # Convert dates to numerical values for regression
    daily_counts["DayNum"] = (
        daily_counts["Date"] - daily_counts["Date"].min()).dt.days
    X = daily_counts["DayNum"].values.reshape(-1, 1)
    y = daily_counts["Count"].values

    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict future threat counts
    future_dates = [df.index.max() + timedelta(days=i)
                    for i in range(1, days_ahead + 1)]
    future_days = [(date - daily_counts["Date"].min()
                    ).days for date in future_dates]
    predicted_counts = model.predict(
        np.array(future_days).reshape(-1, 1)).astype(int)

    # Format predictions
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


def generate_threat_trends(log_file=LOG_FILE, days_ahead=7):
    """Generates threat trends, predicts future threats, and updates logs."""
    df = load_data(log_file)

    # Predict and append future threats
    future_logs = predict_future_threats(df, days_ahead)
    append_predictions_to_log(future_logs, log_file)

    # Reload updated data
    df = load_data(log_file)
    df["Count"] = 1
    daily_counts = df.resample("D").sum()

    # Separate past 7 days, current, and future threats
    past_7_days = daily_counts.loc[daily_counts.index.max(
    ) - timedelta(days=7):daily_counts.index.max()]
    future_dates = [datetime.strptime(
        log["Date"], "%Y-%m-%d %H:%M:%S") for log in future_logs]
    future_scores = [log["Score"] for log in future_logs]

    # Plot threat trends
    plt.figure(figsize=(12, 6))

    # Past 7 days (Green)
    if not past_7_days.empty:
        plt.plot(past_7_days.index, past_7_days["Count"], marker="o",
                 linestyle="-", color="green", label="Past 7 Days")

    # Recorded Threats (Red)
    plt.plot(daily_counts.index, daily_counts["Count"], marker="o",
             linestyle="-", color="red", label="Recorded Threats")

    # Predicted Threats (Blue Dashed)
    if future_logs:
        plt.plot(future_dates, future_scores, marker="o",
                 linestyle="--", color="blue", label="Predicted Threats")

    plt.title("Daily Threat Trends (Past, Present & Predictions)")
    plt.xlabel("Date")
    plt.ylabel("Number of Threats")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()

    # Show and save plot
    plt.savefig("threat_trends.png")
    plt.show()

    print("✅ Updated threat trends graph saved as 'threat_trends.png'.")


# Run the analytics with predictions
generate_threat_trends()
