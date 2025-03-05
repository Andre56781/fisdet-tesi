import logging
from typing import Any, Dict, Callable
from dash import Output, Input, html, dcc
from .pages import home, input_page, output, rules

# Configurazione del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def error_404_layout() -> html.Div:
    """Layout per la pagina 404 personalizzata"""
    return html.Div(
        className="error-container",
        children=[
            html.H1("404 - Pagina non trovata", className="error-title"),
            html.P("La pagina che stai cercando non esiste."),
            dcc.Link(
                "Torna alla Home",
                href="/",
                className="error-link",
                style={'color': 'white', 'textDecoration': 'underline'}
            )
        ],
        style={
            'textAlign': 'center',
            'marginTop': '50px',
            'padding': '20px',
            'backgroundColor': '#f8d7da',
            'borderRadius': '5px'
        }
    )

def register_routing(dash_app: Any) -> None:
    """
    Registra tutte le route dell'applicazione Dash
    
    Args:
        dash_app (dash.Dash): Istanza dell'applicazione Dash
    """
    
    # Mappa delle route con controllo di tipo
    routes: Dict[str, Callable[[], html.Div]] = {
        "/": home.layout,
        "/input": input_page.layout,
        "/output": output.layout,
        "/rules": rules.layout
    }
    
    # Verifica avanzata delle dipendenze
    missing_layouts = [path for path, layout in routes.items() if not callable(layout)]
    if missing_layouts:
        error_msg = f"Layout mancanti per le routes: {', '.join(missing_layouts)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    @dash_app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
        prevent_initial_callbacks=False  # Modificato per permettere il primo rendering
    )
    def render_page_content(pathname: str) -> html.Div:
        """
        Gestisce il rendering dinamico del contenuto in base al percorso
        
        Args:
            pathname (str): Percorso corrente dell'URL
            
        Returns:
            html.Div: Layout della pagina richiesta
        """
        logger.info(f"Richiesta route: {pathname}")
        
        try:
            normalized_path = pathname.rstrip('/') if pathname != '/' else pathname
            layout_func = routes.get(normalized_path, lambda: error_404_layout())
            return layout_func()
        except Exception as e:
            logger.error(f"Errore critico durante il rendering: {str(e)}", exc_info=True)
            return error_404_layout()

    # Aggiungi qui eventuali callback aggiuntivi
    def register_additional_callbacks():
        pass

    register_additional_callbacks()