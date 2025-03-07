from dash import html, dcc
import plotly.express as px
import pandas as pd


def layout():
    return html.Div([
        html.H1("Visualizzazione Dati"),
        dcc.Graph(id="example-graph", figure=fig),
    ])
