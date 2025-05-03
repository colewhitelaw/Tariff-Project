import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Register this page
dash.register_page(
    __name__,
    path='/',
    title='Global Tariff Dashboard - Home',
    name='Home'
)

# Layout for the home page
layout = dbc.Container([
    # Welcome Card
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-globe-americas fa-5x text-info mb-3"),
                            html.H1("Global Tariff Dashboard", className="text-info mb-3 fw-bold"),
                            html.P("Explore international trade tariffs and their economic impact.", 
                                   className="lead mb-4"),
                        ], className="text-center"),
                        
                        # Navigation cards
                        dbc.Row([
                            # Global Trends Card
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.I(className="fas fa-chart-line fa-3x text-info mb-3"),
                                        html.H3("Global Trends", className="mb-3"),
                                        html.P("Interactive visualization of US tariffs over time with global trade partners.", 
                                              className="mb-3"),
                                        dbc.Button("Explore Global Trends", href="/global-trends", color="primary", size="lg", className="w-100")
                                    ], className="text-center")
                                ], className="h-100 shadow hover-card")
                            ], width=12, md=4, className="mb-4"),
                            
                            # Tariff Trends Card
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.I(className="fas fa-chart-bar fa-3x text-info mb-3"),
                                        html.H3("Tariff Trends", className="mb-3"),
                                        html.P("Analyze historical tariff data and economic indicators over time.", 
                                              className="mb-3"),
                                        dbc.Button("View Tariff Trends", href="/tariff-trends", color="primary", size="lg", className="w-100")
                                    ], className="text-center")
                                ], className="h-100 shadow hover-card")
                            ], width=12, md=4, className="mb-4"),
                            
                            # State Analysis Card
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.I(className="fas fa-map-marked-alt fa-3x text-info mb-3"),
                                        html.H3("State Analysis", className="mb-3"),
                                        html.P("Examine impact of tariffs on different US states and regional trade.", 
                                              className="mb-3"),
                                        dbc.Button("State Analysis", href="/state-analysis", color="primary", size="lg", className="w-100")
                                    ], className="text-center")
                                ], className="h-100 shadow hover-card")
                            ], width=12, md=4, className="mb-4")
                        ], className="mb-4"),
                        
                        # Second Row of Cards
                        dbc.Row([
                            # Business Analytics Card
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.I(className="fas fa-briefcase fa-3x text-info mb-3"),
                                        html.H3("Business Analytics", className="mb-3"),
                                        html.P("Monitor tariff trends and calculate cost impact on your business operations.", 
                                              className="mb-3"),
                                        dbc.Button("Business Analytics", href="/business-analytics", color="primary", size="lg", className="w-100")
                                    ], className="text-center")
                                ], className="h-100 shadow hover-card")
                            ], width=12, md=6, className="mb-4"),
                            
                            # About Card
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.I(className="fas fa-info-circle fa-3x text-info mb-3"),
                                        html.H3("About", className="mb-3"),
                                        html.P("Learn more about the data sources, methodologies, and the team behind this dashboard.", 
                                              className="mb-3"),
                                        dbc.Button("About Page", href="/about", color="primary", size="lg", className="w-100")
                                    ], className="text-center")
                                ], className="h-100 shadow hover-card")
                            ], width=12, md=6, className="mb-4")
                        ], className="mb-4"),
                        
                        # Dashboard Summary
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("About This Dashboard", className="bg-primary text-white"),
                                    dbc.CardBody([
                                        html.P([
                                            "This interactive dashboard visualizes international tariff data, focusing on trade relationships ",
                                            "between the United States and its global partners. Explore tariff rates, trade volumes, and economic ",
                                            "indicators through various visualizations and analytical tools."
                                        ]),
                                        html.P([
                                            "Use the navigation cards above to explore different aspects of the data, or visit the ",
                                            html.A("About page", href="/about", className="text-info"), 
                                            " for more information about the data sources and methodology."
                                        ])
                                    ])
                                ], className="shadow")
                            ], width=12)
                        ])
                    ], className="p-4")
                ])
            ], className="shadow border-0")
        ], width=12)
    ], className="my-4")
], fluid=True)

# Custom CSS for hover effects
custom_css = """
<style>
    .hover-card {
        transition: transform 0.3s ease-in-out;
    }
    .hover-card:hover {
        transform: translateY(-10px);
    }
</style>
"""

# Inject custom CSS
layout.children.append(dcc.Markdown(custom_css, dangerously_allow_html=True)) 