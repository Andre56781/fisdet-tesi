import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flaskr.dash_application import dash_app


@dash_app.callback(
    Output("output-message", "children"),
    [Input("submit-button", "n_clicks")],
    [dash.State("user-input", "value")]
)
def update_output(n_clicks, value):
    if n_clicks:
        return f"Hai inserito: {value}"
    return ""
