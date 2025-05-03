import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import pydeck as pdk
from dash_deck import DeckGL
# from data import get_tariff_data, get_sp500_data, get_average_tariff_data # Moved to pages/home.py
import json
import os
from dash import page_registry, register_page

# Set Mapbox access token from environment variable
mapbox_token = os.environ.get('MAPBOX_API_KEY')
if mapbox_token:
    os.environ["MAPBOX_API_KEY"] = mapbox_token

# Initialize the app with Bootstrap
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME],
    use_pages=True,  # Enable pages
    suppress_callback_exceptions=True  # Suppress callback exceptions
)

app.title = "Global Tariff Visualization"

# Navbar Definition (Keep this here as it's part of the main layout)
navbar = dbc.Navbar(
    dbc.Container(
        [
            # Left side - Brand with no margins
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.I(className="fas fa-globe fa-2x text-info me-2"), width="auto"),
                        dbc.Col(dbc.NavbarBrand("Global Tariff Dashboard", className="fw-bold fs-4")),
                    ],
                    align="center",
                    className="g-0", # Remove gutters
                ),
                href="/",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            # Right side - Navigation links with improved styling
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Home", href="/", className="px-3 fw-bold text-white", active="exact")),
                        dbc.NavItem(dbc.NavLink("Business Analytics", href="/business-analytics", className="px-3 fw-bold text-white", active="exact")),
                        dbc.NavItem(dbc.NavLink("Global Trends", href="/global-trends", className="px-3 fw-bold text-white", active="exact")),
                        dbc.NavItem(dbc.NavLink("Tariff Trends", href="/tariff-trends", className="px-3 fw-bold text-white", active="exact")),
                        dbc.NavItem(dbc.NavLink("State Analysis", href="/state-analysis", className="px-3 fw-bold text-white", active="exact")),
                        dbc.NavItem(dbc.NavLink("About", href="/about", className="px-3 fw-bold text-white", active="exact")),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ], 
        fluid=True, # Make the container full-width
        className="px-4" # Add horizontal padding
    ),
    color="primary",
    dark=True,
    className="mb-4 py-2", # Add vertical padding
)

# App layout
app.layout = html.Div([
    navbar,
    dbc.Container([
        html.Div(
            dash.page_container,
            style={"minHeight": "calc(100vh - 140px)"}
        )
    ], fluid=True)
])

# Create server variable for Gunicorn
server = app.server

# Make the server callable
def create_app():
    return app.server

# Make the app directly callable
app = app.server

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050))) 