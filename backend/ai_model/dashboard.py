import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)


def load_threat_data(log_file="threat_alerts.log"):
    df = pd.read_csv(log_file, delimiter="|", names=[
                     "Date", "Message"], parse_dates=["Date"])
    df["Count"] = 1
    return df.resample("D", on="Date").sum()


df = load_threat_data()
fig = px.line(df, x=df.index, y="Count",
              title="Real-Time Threat Detection Trends")

app.layout = html.Div([
    html.H1("Dark Web Threat Dashboard"),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)
