import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Paths
PREDICTIONS_FILE = "backend/predictions.json"

# Load historical data


def load_past_predictions():
    if not os.path.exists(PREDICTIONS_FILE):
        print("⚠️ No past predictions found!")
        return pd.DataFrame()

    with open(PREDICTIONS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not data:
        print("⚠️ No data in predictions.json!")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # Convert timestamps
    df["score"] = df["score"].astype(float)  # Convert scores to float
    df.set_index("timestamp", inplace=True)  # Set timestamp as index

    return df


def predict_future_threats(df, days=10):
    """Predict threat levels for the next 'days' days."""
    if df.empty:
        print("⚠️ No data to predict future threats!")
        return []

    # Train model on past data
    model = ExponentialSmoothing(
        df["score"], trend="add", seasonal="add", seasonal_periods=7)
    fitted_model = model.fit()

    # Predict for next 'days'
    future_dates = [df.index[-1] +
                    timedelta(days=i) for i in range(1, days + 1)]
    future_scores = fitted_model.forecast(steps=days)

    future_predictions = [{"timestamp": str(date), "predicted_score": round(score, 2)}
                          for date, score in zip(future_dates, future_scores)]

    return future_predictions


def save_future_predictions(future_predictions):
    """Save future predictions to a JSON file."""
    future_file = "backend/future_predictions.json"

    with open(future_file, "w", encoding="utf-8") as file:
        json.dump(future_predictions, file, indent=4)

    print(f"📈 Future predictions saved to {future_file}")


def plot_future_trends(df, future_predictions):
    """Plot historical and future threat trends."""
    plt.figure(figsize=(10, 5))

    # Plot past threat levels
    plt.plot(df.index, df["score"], marker="o", linestyle="-",
             color="blue", label="Past Threat Levels")

    # Plot future predictions
    future_dates = [datetime.strptime(
        p["timestamp"], "%Y-%m-%d %H:%M:%S") for p in future_predictions]
    future_scores = [p["predicted_score"] for p in future_predictions]
    plt.plot(future_dates, future_scores, marker="o", linestyle="--",
             color="red", label="Predicted Threat Levels")

    # Formatting
    plt.xlabel("Date")
    plt.ylabel("Threat Score")
    plt.title("Threat Level Forecast for Next 7 Days")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()

    plt.savefig("backend/static/future_trend.png")  # Save graph
    plt.show()


if __name__ == "__main__":
    print("🚀 Predicting Future Threat Levels...")

    # Load past data
    past_data = load_past_predictions()

    if not past_data.empty:
        # Predict next 7 days
        future_predictions = predict_future_threats(past_data, days=7)

        # Save results
        save_future_predictions(future_predictions)

        # Generate visualization
        plot_future_trends(past_data, future_predictions)
    else:
        print("⚠️ Not enough data to predict future trends!")
