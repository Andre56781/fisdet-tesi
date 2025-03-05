import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

def serve_layout():
    return html.Div([
        dcc.Location(id="url", refresh=False),
        
        # Font Awesome
        html.Link(
            rel='stylesheet',
            href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
        ),
        
        # Google Fonts
        html.Link(
            rel='stylesheet',
            href='https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap'
        ),
        
        # Sidebar
        html.Div([
            # Container per il logo (posizionato in alto)
            html.Div(
                html.A(
                    html.Img(
                        src=dash.get_asset_url('images/LogoInt.png')
                    ),
                    href="/"
                ),
                className="sidebar-logo"
            ),
            # Navigazione: centrata verticalmente
            html.Nav([
                dcc.Link(
                    [html.I(className="fas fa-edit mr-2"), "Input"],
                    href="/input",
                    className="nav-link"
                ),
                dcc.Link(
                    [html.I(className="fas fa-chart-bar mr-2"), "Output"],
                    href="/output",
                    className="nav-link"
                ),
                dcc.Link(
                    [html.I(className="fas fa-code-branch mr-2"), "Rules"],
                    href="/rules",
                    className="nav-link"
                ),
            ], className="sidebar-nav"),
        ], className="sidebar"),
        
        # Contenuto principale
        html.Div([
            html.Div(id="page-content", className="content-inner")
        ], className="content"),
        
    ], className="app-container")
