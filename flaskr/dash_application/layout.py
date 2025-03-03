import dash
from dash import html, dcc

def serve_layout():
    return html.Div([
        # Sidebar
        html.Div([
            html.Img(src=dash.get_asset_url('images/LogoInt.png'), style={"width": "100px"}),
            html.H2("Menu"),
            html.Nav([
                dcc.Link("Home", href="/"),
                dcc.Link("Input", href="/input"),
                dcc.Link("Output", href="/output"),
                dcc.Link("Rules", href="/rules"),
            ], className="sidebar-nav"),
        ], className="sidebar"),
        
        # Contenuto principale (verrà sostituito dalle pagine)
        html.Div(id="page-content", className="content"),

        # Footer
        html.Footer("© 2025 FISDeT", className="footer"),
    ])
