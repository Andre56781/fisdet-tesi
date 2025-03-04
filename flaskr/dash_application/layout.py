import dash
from dash import html, dcc

def serve_layout():
    return html.Div([
        dcc.Location(id="url", refresh=False),
        
        # Sidebar
        html.Div([
            html.A(
                html.Img(
                    src=dash.get_asset_url('images/LogoInt.png'),
                    style={"width": "100px", "cursor": "pointer"}
                ),
                href="/"
            ),
            html.Nav([
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

