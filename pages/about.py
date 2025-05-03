import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Register this page
dash.register_page(
    __name__,
    path='/about',
    title='Global Tariff Dashboard - About',
    name='About'
)

# Layout for the about page
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("About the Global Tariff Dashboard", className="text-info mt-2 mb-1 fw-bold"),
            html.P(
                "An interactive tool to explore trade tariffs between the United States and key trading partners.",
                className="lead mb-2"
            ),
            
            # Project Info, Data Usage, and Team in a single card to save space
            dbc.Card([
                dbc.CardHeader("Project Information", className="bg-primary text-white py-2"),
                dbc.CardBody([
                    dbc.Row([
                        # Left column - Purpose and Data Sources
                        dbc.Col([
                            html.Div([
                                html.H5("Purpose", className="mb-1"),
                                html.P(
                                    "This dashboard visualizes global tariffs, focusing on those imposed by and on the United States.",
                                    className="mb-2"
                                ),
                                
                                html.H5("Data Sources", className="mb-1 mt-2"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Ul([
                                            html.Li("Trade tariff data: World Trade Organization (WTO)"),
                                            html.Li("Trade volume data: UN Comtrade Database"),
                                            html.Li("S&P 500 data: Yahoo Finance")
                                        ], className="mb-0 ps-4"),
                                    ], width=8),
                                ]),
                                
                                html.H5("Synthetic Data Usage", className="mb-1 mt-2"),
                                html.P(
                                    "Synthetic data was generated for the years 2015-2024 and used in the following sections: "
                                    "Business Analytics Page, Global Trends page (except for the Country Comparison Scatterplot, S&P 500 KPI, and Import Avg Tariff Rates), "
                                    "and the State Analysis page. This synthetic data ensures comprehensive coverage and "
                                    "consistent visualization across all time periods.",
                                    className="mb-2"
                                ),
                            ]),
                        ], md=6),
                        
                        # Right column - Features and Technology
                        dbc.Col([
                            html.Div([
                                html.H5("Features", className="mb-1"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Ul([
                                            html.Li("Interactive global map with trade routes"),
                                            html.Li("Tariff rate visualization with width-encoded arcs"),
                                            html.Li("Time-series analysis capabilities"),
                                            html.Li("Country and product category filtering")
                                        ], className="mb-0 ps-4"),
                                    ], width=12),
                                ]),
                                
                                html.H5("Team", className="mb-1 mt-2"),
                                html.P(
                                    "Developed as part of USC's DSCI 554 course on Visual Analytics by graduate students "
                                    "specializing in data science and visualization.",
                                    className="mb-0"
                                ),
                            ]),
                        ], md=6)
                    ])
                ], className="py-2")
            ], className="shadow mb-2"),
            
            # Glossary of Terms 
            dbc.Card([
                dbc.CardHeader("Glossary of Terms", className="bg-primary text-white py-2"),
                dbc.CardBody([
                    dbc.Row([
                        # Left column - First three terms
                        dbc.Col([
                            html.Dl([
                                html.Dt("MFN (Most Favored Nation)", className="fw-bold mb-1"),
                                html.Dd(
                                    "Tariffs charged to WTO members, unless a special trade agreement exists.",
                                    className="mb-2"
                                ),
                                
                                html.Dt("Bound", className="fw-bold mb-1"),
                                html.Dd(
                                    "Maximum tariff rate a WTO member country has committed to not exceed.",
                                    className="mb-2"
                                ),
                                
                                html.Dt("Pref. Margin", className="fw-bold mb-1"),
                                html.Dd(
                                    "Trade-weighted average difference between MFN and most advantageous duty (e.g., NAFTA rates).",
                                    className="mb-0"
                                ),
                            ], className="mb-0"),
                        ], md=6),
                        
                        # Right column - Remaining terms
                        dbc.Col([
                            html.Dl([
                                html.Dt("Non ad valorem", className="fw-bold mb-1"),
                                html.Dd(
                                    "A tariff not expressed in percentages (e.g., 5¢ per pair of shoes).",
                                    className="mb-2"
                                ),
                                
                                html.Dt("Tariff line", className="fw-bold mb-1"),
                                html.Dd(
                                    "Tariff rate on a specific product sub-category (e.g., \"Live purebred breeding horses\").",
                                    className="mb-0"
                                ),
                            ], className="mb-0"),
                        ], md=6)
                    ])
                ], className="py-2")
            ], className="shadow")
        ], width=12)
    ])
], fluid=True, className="py-2") 