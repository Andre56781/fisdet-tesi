from dash import html, dcc
import plotly.express as px
import pandas as pd

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"],
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

def layout():
    return html.Div([
        html.H1("Visualizzazione Dati"),
        dcc.Graph(id="example-graph", figure=fig),
    ])
