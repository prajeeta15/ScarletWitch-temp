import pandas as pd


def generate_report(log_file="threat_alerts.log", output_file="threat_report.txt"):
    """Generates a summary report of threats detected."""
    df = pd.read_csv(log_file, delimiter="|", names=[
                     "Date", "Message"], parse_dates=["Date"])

    total_threats = df.shape[0]
    daily_avg = total_threats / df["Date"].nunique()

    with open(output_file, "w") as f:
        f.write(f"🚨 Dark Web Threat Report 🚨\n")
        f.write(f"Total Threats Detected: {total_threats}\n")
        f.write(f"Daily Average: {daily_avg:.2f}\n")

    print(f"Report saved to {output_file}")


# Run the report generator
generate_report()
