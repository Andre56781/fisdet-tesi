import logging
from typing import Any, Dict, Callable
from dash import Output, Input, html, dcc
from .pages import home_page, input_page, output_page, rules_page, import_page

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
    """
    
    routes: Dict[str, Callable[[], html.Div]] = {
        "/": home_page.layout,
        "/input": input_page.layout,
        "/output": output_page.layout,
        "/rules": rules_page.layout,
        "/import": import_page.layout
    }
    
    # Verifica avanzata delle dipendenze
    missing_layouts = [path for path, layout in routes.items() if not callable(layout)]
    if missing_layouts:
        error_msg = f"Layout mancanti per le routes: {', '.join(missing_layouts)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


    # Callback per il rendering del contenuto
    @dash_app.callback(
        Output("page-content", "children"),
        Input("url", "pathname"),
        prevent_initial_callbacks=False
    )
    def render_page_content(pathname: str) -> html.Div:
        logger.info(f"Richiesta route: {pathname}")
        
        try:
            # Normalizzazione avanzata dei path
            normalized_path = pathname.strip().rstrip('/')
            if not normalized_path:
                normalized_path = '/'
                
            layout_func = routes.get(normalized_path, error_404_layout)
            return layout_func()
        except Exception as e:
            logger.error(f"Errore critico durante il rendering: {str(e)}", exc_info=True)
            return error_404_layout()

    # Funzione per eventuali callback aggiuntivi
    def register_additional_callbacks():
        pass  # Aggiungere qui eventuali altri callback

    register_additional_callbacks()