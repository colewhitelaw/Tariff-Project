import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Custom CSS to style the dropdowns
dropdown_style = {
    'backgroundColor': 'transparent',
    'color': 'white',
    'border': 'none',
    'borderBottom': '1px solid #495057',
    'borderRadius': '0',
    'paddingLeft': '0'
}

# Add white text color to all possible dropdown elements
dropdown_text_style = {
    '--dropdown-text': 'white',
    '--dropdown-bg': 'transparent'
}

# Define common input style
input_style = {
    'backgroundColor': '#2b3035',
    'color': 'white',
    'border': '1px solid #495057'
}

# Register this page
dash.register_page(
    __name__,
    path='/business-analytics',
    title='Global Tariff Dashboard - Business Analytics',
    name='Business Analytics'
)

# Generate synthetic tariff trend data
def generate_tariff_trend_data():
    # Time range - create detailed daily data for the past 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # List of countries and products
    countries = ['China', 'Canada', 'Mexico', 'Japan', 'Germany', 'South Korea', 
                'United Kingdom', 'France', 'India', 'Brazil', 'Italy', 'Spain']
    
    product_categories = {
        'Electronics': ['Smartphones', 'Computers', 'Televisions', 'Semiconductors', 'Circuit Boards'],
        'Automotive': ['Vehicles', 'Auto Parts', 'Tires', 'Engines', 'Batteries'],
        'Textiles': ['Cotton', 'Silk', 'Wool', 'Synthetic Fabrics', 'Garments'],
        'Agricultural': ['Corn', 'Wheat', 'Soybeans', 'Beef', 'Dairy'],
        'Steel & Metals': ['Steel', 'Aluminum', 'Copper', 'Nickel', 'Zinc'],
        'Chemicals': ['Plastics', 'Fertilizers', 'Pharmaceuticals', 'Industrial Chemicals', 'Dyes']
    }
    
    # Flatten product list
    products = []
    for category, category_products in product_categories.items():
        for product in category_products:
            products.append({"name": product, "category": category})
    
    # Create base dataframe structure
    data = []
    
    # For each country and product, generate a tariff rate time series
    for country in countries:
        # Create random base rates per country (between 5% and 25%)
        base_rate = np.random.uniform(5, 25)
        
        # Create some seasonal patterns
        for product in products:
            # Slightly different base rate per product
            product_base_rate = base_rate + np.random.uniform(-3, 3)
            
            # Generate tariff rate time series with some trending and volatility
            rates = []
            events = []
            trend = np.random.choice([-0.005, 0, 0.005, 0.01])  # Slight trending
            
            # Keep track of the current rate
            current_rate = max(0, product_base_rate)
            
            for i, date in enumerate(dates):
                # Add some seasonality (higher in Q1 and Q3)
                month = date.month
                if month in [1, 2, 3, 7, 8, 9]:
                    seasonal = np.random.uniform(0, 1)
                else:
                    seasonal = np.random.uniform(-0.5, 0.5)
                
                # Add random noise
                noise = np.random.normal(0, 0.2)
                
                # Apply trend, seasonality, and noise
                current_rate += trend + seasonal + noise
                
                # Ensure rate doesn't go below 0
                current_rate = max(0, current_rate)
                
                # Generate occasional tariff events (policy changes, trade disputes, etc.)
                if np.random.random() < 0.03:  # 3% chance of event on any day
                    event_type = np.random.choice([
                        "New Tariff",
                        "Tariff Increase",
                        "Tariff Reduction",
                        "Trade Dispute",
                        "Trade Agreement",
                        "Supply Chain Disruption"
                    ])
                    
                    # Effect depends on event type
                    if event_type in ["New Tariff", "Tariff Increase", "Trade Dispute"]:
                        effect = np.random.uniform(0.5, 3.0)
                        current_rate += effect
                        direction = "increase"
                    else:
                        effect = np.random.uniform(0.5, 1.5)
                        current_rate -= effect
                        current_rate = max(0, current_rate)
                        direction = "decrease"
                        
                    # Create event details
                    events.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "type": event_type,
                        "effect": f"{effect:.2f}% {direction}",
                        "description": f"{event_type} affecting {product['name']} imports from {country}",
                        "impact": "High" if effect > 2 else ("Medium" if effect > 1 else "Low")
                    })
                
                # Add data point
                data.append({
                    "date": date,
                    "country": country,
                    "product": product["name"],
                    "category": product["category"],
                    "tariff_rate": current_rate,
                    "has_event": len(events) > 0 and events[-1]["date"] == date.strftime("%Y-%m-%d")
                })
                
                # Attach events to data
                if len(data) > 0 and len(events) > 0 and events[-1]["date"] == date.strftime("%Y-%m-%d"):
                    data[-1]["event"] = events[-1]
    
    return pd.DataFrame(data)

# Generate data once
tariff_df = generate_tariff_trend_data()

# Function to create events data based on filtered data
def create_events_data(filtered_df):
    events_data = []
    
    # Extract rows with events
    event_rows = filtered_df[filtered_df['has_event'] == True]
    
    for _, row in event_rows.iterrows():
        if 'event' in row:
            event = row['event']
            events_data.append({
                'date': event['date'],
                'product': row['product'],
                'country': row['country'],
                'type': event['type'],
                'effect': event['effect'],
                'description': event['description'],
                'impact': event['impact']
            })
    
    return pd.DataFrame(events_data)

# Function to apply custom styles to the page
def apply_custom_styles():
    return html.Div([
        dcc.Markdown(
            '''
            <style>
                /* COMPREHENSIVE DROPDOWN STYLING */
                
                /* Text label above dropdown */
                .fw-bold.text-white {
                    color: white !important;
                }
                
                /* All dropdown text elements */
                .Select, 
                .Select input, 
                .Select .Select-control, 
                .Select .Select-menu-outer, 
                .Select .Select-option, 
                .Select .Select-placeholder, 
                .Select .Select-value, 
                .Select .Select-value-label {
                    color: white !important;
                }
                
                /* Placeholder text - critical for initial state */
                .Select-placeholder {
                    color: white !important;
                }
                
                /* Input element */
                .Select input {
                    color: white !important;
                }
                
                /* Selected value text */
                .Select-value-label {
                    color: white !important;
                }
                
                /* Dropdown control container */
                .Select-control {
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
                    border-left: none !important;
                    border-right: none !important;
                    border-top: none !important;
                    border-radius: 0 !important;
                    background: transparent !important;
                    box-shadow: none !important;
                    color: white !important;
                }
                
                /* Ensure pseudo-focused state has white text */
                .Select.is-focused .Select-placeholder,
                .Select.is-focused .Select-value-label {
                    color: white !important;
                }
                
                /* Dropdown options container */
                .Select-menu-outer {
                    background-color: rgba(33, 37, 41, 0.9) !important;
                    border: none !important;
                    border-radius: 4px !important;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
                    margin-top: 3px !important;
                    max-height: 150px !important;
                    overflow-y: auto !important;
                }
                
                /* Dropdown menu */
                .Select-menu {
                    max-height: 148px !important;
                    overflow-y: auto !important;
                }
                
                /* Individual dropdown options */
                .Select-option {
                    background-color: transparent !important;
                    color: white !important;
                    padding: 8px 12px !important;
                }
                
                /* Hovered/focused dropdown option */
                .Select-option.is-focused, 
                .Select-option:hover {
                    background-color: rgba(73, 80, 87, 0.7) !important;
                    color: white !important;
                }
                
                /* Dropdown arrow */
                .Select-arrow {
                    border-color: white transparent transparent !important;
                }
                
                /* Opened dropdown arrow */
                .is-open .Select-arrow {
                    border-color: transparent transparent white !important;
                }
                
                /* Input wrapper */
                .Select-input {
                    padding-left: 0 !important;
                }
                
                /* Selected value container */
                .Select-value {
                    padding-left: 0 !important;
                    color: white !important;
                }
                
                /* Remove focus outline */
                .Select.is-focused > .Select-control {
                    border-color: transparent !important;
                    box-shadow: none !important;
                }
                
                /* Fade effect for dropdown options */
                .Select-menu-outer::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 10px;
                    background: linear-gradient(to bottom, rgba(33, 37, 41, 0.9), transparent);
                    z-index: 1;
                    pointer-events: none;
                }
                
                .Select-menu-outer::after {
                    content: '';
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    height: 10px;
                    background: linear-gradient(to top, rgba(33, 37, 41, 0.9), transparent);
                    z-index: 1;
                    pointer-events: none;
                }
                
                /* More specific selectors to override React-Select default styles */
                #country-dropdown .Select-control .Select-value-label,
                #category-dropdown .Select-control .Select-value-label,
                #product-dropdown .Select-control .Select-value-label {
                    color: white !important;
                }
                
                #country-dropdown .Select-placeholder,
                #category-dropdown .Select-placeholder,
                #product-dropdown .Select-placeholder {
                    color: white !important;
                }
                
                /* Ensure product dropdown menu has proper scrolling */
                #product-dropdown .Select-menu-outer {
                    max-height: 200px !important;
                    overflow-y: auto !important;
                }
                
                #product-dropdown .Select-menu {
                    max-height: 198px !important;
                }
            </style>
            ''',
            dangerously_allow_html=True
        )
    ], style={"display": "none"})

# Layout for the business analytics page
layout = dbc.Container([
    # Apply custom styles
    apply_custom_styles(),
    
    # Title and Description
    dbc.Row([
        dbc.Col([
            html.H1("Business Tariff Analytics", className="text-info mt-2 mb-0 fw-bold"),
            html.P("Monitor tariff trends and events to anticipate cost changes for your business", 
                  className="text-muted mb-2")
        ], width=12)
    ], className="mb-3"),
    
    # Filters and Key Metrics Row
    dbc.Row([
        # Filters Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters", className="bg-primary text-white"),
                dbc.CardBody([
                    # Time Range Filter
                    html.P("Time Range:", className="mb-1 fw-bold"),
                    dbc.RadioItems(
                        id='time-range-radio',
                        options=[
                            {'label': '1 Month', 'value': 30},
                            {'label': '3 Months', 'value': 90},
                            {'label': '6 Months', 'value': 180},
                            {'label': '1 Year', 'value': 365}
                        ],
                        value=90,
                        inline=True,
                        className="mb-3"
                    ),
                    
                    # Country Filter
                    html.P("Country:", className="mb-1 fw-bold text-white"),
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[{'label': country, 'value': country} for country in sorted(tariff_df['country'].unique())],
                        value=sorted(tariff_df['country'].unique())[0],
                        style={
                            'color': 'white', 
                            'backgroundColor': '#343a40'
                        },
                        className="mb-3"
                    ),
                    
                    # Product Category Filter
                    html.P("Product Category:", className="mt-3 mb-1 fw-bold text-white"),
                    dcc.Dropdown(
                        id='category-dropdown',
                        options=[{'label': category, 'value': category} for category in sorted(tariff_df['category'].unique())],
                        value=sorted(tariff_df['category'].unique())[0],
                        style={
                            'color': 'white', 
                            'backgroundColor': '#343a40'
                        },
                        className="mb-3"
                    ),
                    
                    # Product Filter
                    html.P("Product:", className="mt-3 mb-1 fw-bold text-white"),
                    dcc.Dropdown(
                        id='product-dropdown',
                        options=[],  # Will be populated by callback
                        value=None,
                        style={
                            'color': 'white', 
                            'backgroundColor': '#343a40'
                        },
                        className="mb-3",
                        maxHeight=200
                    ),
                ], className="p-3")
            ], className="shadow h-100")
        ], width=12, lg=3),
        
        # KPI Cards Column
        dbc.Col([
            dbc.Row([
                # Average Tariff Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-percentage me-2"),
                            "Average Tariff Rate"
                        ], className="bg-primary text-white"),
                        dbc.CardBody([
                            html.H3(id="avg-tariff-value", className="text-center text-primary mb-0"),
                            html.P("Current average tariff rate for selected product", className="text-center text-muted small mb-0")
                        ], className="p-2")
                    ], className="shadow text-center")
                ], width=12, md=4, className="mb-3"),
                
                # Tariff Change Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2"),
                            html.Span("Tariff Change ", className="me-1"),
                            html.Span(id="period-display", className="text-info")
                        ], className="bg-primary text-white"),
                        dbc.CardBody([
                            html.H3(id="tariff-change-value", className="text-center mb-0"),
                            html.P("Change in tariff rate over selected period", className="text-center text-muted small mb-0")
                        ], className="p-2")
                    ], className="shadow text-center")
                ], width=12, md=4, className="mb-3"),
                
                # Tariff Events Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-exclamation-circle me-2"),
                            "Tariff Events"
                        ], className="bg-primary text-white"),
                        dbc.CardBody([
                            html.H3(id="tariff-events-value", className="text-center text-warning mb-0"),
                            html.P("Number of tariff policy changes in period", className="text-center text-muted small mb-0")
                        ], className="p-2")
                    ], className="shadow text-center")
                ], width=12, md=4, className="mb-3")
            ]),
            
            # Rate History Chart
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-chart-area me-2"),
                    "Tariff Rate History", 
                    html.Small("(hover over points to see tariff events)", className="text-muted ms-2")
                ], className="bg-primary text-white"),
                dbc.CardBody([
                    dcc.Graph(
                        id='tariff-history-chart',
                        figure={},
                        style={'height': '300px'},
                        config={'displayModeBar': False}
                    )
                ], className="p-0")
            ], className="shadow mb-3")
        ], width=12, lg=9)
    ], className="mb-4 gx-4"),
    
    # Event Log and Cost Impact Row
    dbc.Row([
        # Event Log Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-list-alt me-2"),
                    "Tariff Event Log"
                ], className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(
                        id="event-log-container",
                        className="py-2",
                        style={'maxHeight': '400px', 'overflowY': 'auto'}
                    )
                ], className="p-3")
            ], className="shadow h-100")
        ], width=12, lg=7),
        
        # Cost Impact Column
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.I(className="fas fa-dollar-sign me-2"),
                    "Cost Impact Analysis"
                ], className="bg-primary text-white"),
                dbc.CardBody([
                    # Cost Calculator
                    html.Div([
                        html.P("Estimate the direct impact of tariffs on your import costs:", className="mb-3"),
                        
                        # Import Value
                        dbc.InputGroup([
                            dbc.InputGroupText("Import Value ($)"),
                            dbc.Input(
                                id="import-value-input",
                                type="number",
                                value=10000,
                                step=1000,
                                min=0,
                                style=input_style
                            )
                        ], className="mb-4"),
                        
                        # Results
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H5(id="filter-context", className="mb-3 text-info fw-bold")
                                    ], className="border-bottom pb-2 mb-3")
                                ], width=12),
                                dbc.Col([
                                    html.H6("Current Tariff Cost:", className="mb-2"),
                                    html.H4(id="current-tariff-cost", className="text-primary")
                                ], width=12, md=6),
                                dbc.Col([
                                    html.H6("Cost Change in Period:", className="mb-2"),
                                    html.H4(id="tariff-cost-change", className="")
                                ], width=12, md=6)
                            ]),
                            html.Div([
                                html.H6("Cost Trend:", className="mt-3 mb-2"),
                                html.P(id="tariff-trend-text", className="px-2 py-2 rounded")
                            ], className="border-top pt-3 mt-3")
                        ], id="impact-results", className="border-top pt-3 mt-3 bg-dark rounded p-3")
                    ])
                ], className="p-3")
            ], className="shadow h-100")
        ], width=12, lg=5)
    ]),
    
    # Add bottom padding
    html.Div(style={"height": "50px"})  # Spacer at the bottom
], fluid=True, className="pb-5")

# Basic callback approach for updating products based on category
@callback(
    Output('product-dropdown', 'options'),
    Output('product-dropdown', 'value'),
    [Input('category-dropdown', 'value')]
)
def update_products(selected_category):
    # Handle empty category selection
    if not selected_category:
        return [], None
    
    # Get filtered products from the dataset
    base_products = sorted(tariff_df[tariff_df['category'] == selected_category]['product'].unique())
    
    # Create extra product options that look like completely different items
    all_products = list(base_products)
    
    # Add category-specific additional products
    if selected_category == 'Electronics':
        additional = ['Wireless Earbuds', 'Smart Watches', 'Digital Cameras', 'Portable Speakers', 
                      'Gaming Consoles', 'E-readers', 'Bluetooth Devices', 'Power Banks', 
                      'USB Devices', 'Wireless Chargers', 'VR Headsets', 'Drones']
        all_products.extend(additional)
    elif selected_category == 'Automotive':
        additional = ['Brake Pads', 'Spark Plugs', 'Oil Filters', 'Transmission Parts', 
                      'Exhaust Systems', 'Navigation Systems', 'Turbochargers', 'Timing Belts',
                      'Suspension Components', 'Radiators', 'Air Filters', 'Headlights']
        all_products.extend(additional)
    elif selected_category == 'Textiles':
        additional = ['Polyester', 'Nylon', 'Acrylic', 'Rayon', 'Linen', 'Denim', 
                      'Canvas', 'Satin', 'Velvet', 'Flannel', 'Leather', 'Suede', 'Lace']
        all_products.extend(additional)
    elif selected_category == 'Agricultural':
        additional = ['Rice', 'Barley', 'Oats', 'Sugar', 'Coffee', 'Tea', 'Cocoa', 
                      'Fruits', 'Vegetables', 'Nuts', 'Pork', 'Poultry', 'Eggs']
        all_products.extend(additional)
    elif selected_category == 'Steel & Metals':
        additional = ['Gold', 'Silver', 'Platinum', 'Titanium', 'Lead', 'Tin', 
                      'Brass', 'Bronze', 'Stainless Steel', 'Cast Iron', 'Chrome', 'Tungsten']
        all_products.extend(additional)
    elif selected_category == 'Chemicals':
        additional = ['Acids', 'Alkalis', 'Solvents', 'Adhesives', 'Detergents', 
                      'Pigments', 'Resins', 'Polymers', 'Pesticides', 'Lubricants', 'Catalysts']
        all_products.extend(additional)
    else:
        # For any other category, add generic items to ensure scrolling
        additional = [f'Product Item {i}' for i in range(1, 15)]
        all_products.extend(additional)
    
    # Create options with unique items (no types/variants)
    options = [{'label': p, 'value': p} for p in sorted(all_products)]
    
    # Select first original product as default
    value = base_products[0] if len(base_products) > 0 else None
    
    return options, value

# Modify the update_tariff_trend callback to respond immediately to dropdown changes
@callback(
    [Output('tariff-history-chart', 'figure'),
     Output('avg-tariff-value', 'children'),
     Output('tariff-change-value', 'children'),
     Output('tariff-change-value', 'className'),
     Output('tariff-events-value', 'children'),
     Output('event-log-container', 'children')],
    [Input('time-range-radio', 'value'),
     Input('country-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('product-dropdown', 'value')]
)
def update_tariff_trend(days, country, category, product):
    # Ensure we have all necessary inputs before processing
    if not days or not country or not category or not product:
        # Return empty/placeholder values if any input is missing
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="Select filters to view data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(color="white", size=16)
        )
        empty_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#212529",
            plot_bgcolor="#212529",
            height=300
        )
        
        return empty_fig, "N/A", "N/A", "text-center text-muted mb-0", "0", "Select filters to view data"
    
    # Filter data based on selections
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    filtered_df = tariff_df[
        (tariff_df['date'] >= start_date) & 
        (tariff_df['date'] <= end_date)
    ]
    
    if country:
        filtered_df = filtered_df[filtered_df['country'] == country]
    
    if category:
        filtered_df = filtered_df[filtered_df['category'] == category]
    
    if product:
        filtered_df = filtered_df[filtered_df['product'] == product]
    
    # If no data after filtering, return empty chart
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available for the selected filters",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(color="white", size=16)
        )
        empty_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#212529",
            plot_bgcolor="#212529",
            height=300
        )
        
        return empty_fig, "N/A", "N/A", "text-center text-muted mb-0", "0", "No events found"
    
    # Create events dataframe
    events_df = create_events_data(filtered_df)
    
    # Calculate KPIs
    current_rate = filtered_df.iloc[-1]['tariff_rate']
    start_rate = filtered_df.iloc[0]['tariff_rate']
    rate_change = current_rate - start_rate
    rate_change_pct = (rate_change / start_rate) * 100 if start_rate > 0 else 0
    event_count = len(events_df)
    
    # Create the tariff trend chart
    fig = go.Figure()
    
    # Add line trace for tariff rate
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['tariff_rate'],
        mode='lines+markers',
        name='Tariff Rate',
        line=dict(color='#4285F4', width=2),
        marker=dict(
            size=8,
            color=filtered_df.apply(
                lambda row: '#FFC107' if row['has_event'] else '#4285F4', 
                axis=1
            ),
            line=dict(width=1, color='#FFFFFF')
        ),
        hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Rate:</b> %{y:.2f}%<extra></extra>'
    ))
    
    # Highlight event points
    event_df = filtered_df[filtered_df['has_event'] == True]
    if not event_df.empty:
        fig.add_trace(go.Scatter(
            x=event_df['date'],
            y=event_df['tariff_rate'],
            mode='markers',
            marker=dict(
                symbol='star',
                size=12,
                color='#FFC107',
                line=dict(width=1, color='#FFFFFF')
            ),
            name='Tariff Event',
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Rate:</b> %{y:.2f}%<br><b>Event:</b> %{text}<extra></extra>',
            text=event_df.apply(lambda row: row['event']['type'] if 'event' in row else 'Event', axis=1)
        ))
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Tariff Rate History: {product} from {country}",
            font=dict(size=14),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Date',
        yaxis_title='Tariff Rate (%)',
        hovermode='closest',
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="#212529",
        plot_bgcolor="#212529",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=300
    )
    
    # Create the event log
    if events_df.empty:
        event_log = html.P("No tariff events found for the selected filters.", className="text-muted p-3")
    else:
        event_rows = []
        for i, event in events_df.iterrows():
            impact_class = {
                "High": "text-danger",
                "Medium": "text-warning",
                "Low": "text-info"
            }.get(event['impact'], "text-muted")
            
            event_rows.append(
                dbc.Card([
                    dbc.CardHeader([
                        html.Span(f"{event['date']} - {event['type']}", className="fw-bold"),
                        html.Span(f" ({event['effect']})", className=impact_class)
                    ], className="p-2"),
                    dbc.CardBody([
                        html.P(f"{event['description']}", className="mb-0 small"),
                        html.Small(f"Impact: {event['impact']}", className=f"{impact_class} fw-bold")
                    ], className="p-2")
                ], className="mb-2 shadow-sm")
            )
        
        event_log = html.Div(event_rows)
    
    # Format KPI values
    avg_tariff = f"{current_rate:.2f}%"
    
    if rate_change > 0:
        tariff_change = f"+{rate_change:.2f}% (+{rate_change_pct:.1f}%)"
        change_class = "text-center text-danger mb-0"
    elif rate_change < 0:
        tariff_change = f"{rate_change:.2f}% ({rate_change_pct:.1f}%)"
        change_class = "text-center text-success mb-0"
    else:
        tariff_change = "0.00% (0.0%)"
        change_class = "text-center text-muted mb-0"
    
    events_value = f"{event_count}"
    
    return fig, avg_tariff, tariff_change, change_class, events_value, event_log

# Ensure cost impact updates when relevant values change
@callback(
    [Output('filter-context', 'children'),
     Output('current-tariff-cost', 'children'),
     Output('tariff-cost-change', 'children'),
     Output('tariff-cost-change', 'className'),
     Output('tariff-trend-text', 'children'),
     Output('tariff-trend-text', 'className'),
     Output('impact-results', 'style')],
    [Input('import-value-input', 'value'),
     Input('avg-tariff-value', 'children'),
     Input('tariff-change-value', 'children'),
     Input('time-range-radio', 'value'),
     Input('country-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('product-dropdown', 'value')]
)
def calculate_cost_impact(import_value, current_tariff, tariff_change, 
                          time_range, country, category, product):
    # Ensure we have all necessary inputs
    if not import_value or not country or not category or not product or import_value == 0:
        return "", "", "", "", "", "", {'display': 'none'}
    
    # Create filter context description
    time_range_text = {
        30: "past month",
        90: "past 3 months",
        180: "past 6 months",
        365: "past year"
    }.get(time_range, "selected period")
    
    filter_context = f"Impact analysis for {product} imports from {country}"
    
    # Parse current tariff rate from string (e.g. "15.75%")
    try:
        current_tariff_rate = float(current_tariff.replace("%", ""))
    except:
        current_tariff_rate = 0
    
    # Parse tariff change from the string
    try:
        # Extract first number from tariff change string (e.g. "+2.50% (+10.1%)" -> 2.50)
        tariff_change_value = float(tariff_change.split('%')[0].replace('+', ''))
    except:
        tariff_change_value = 0
    
    # Calculate tariff costs
    if import_value is not None:
        # Current tariff cost
        current_tariff_cost = (import_value * current_tariff_rate / 100)
        
        # Calculate change in tariff cost over period
        past_tariff_rate = current_tariff_rate - tariff_change_value
        past_tariff_cost = (import_value * past_tariff_rate / 100)
        tariff_cost_change = current_tariff_cost - past_tariff_cost
        
        # Format results
        current_cost = f"${current_tariff_cost:,.2f}"
        
        if tariff_cost_change > 0:
            cost_change = f"+${tariff_cost_change:,.2f}"
            change_class = "text-danger"
        elif tariff_cost_change < 0:
            cost_change = f"-${abs(tariff_cost_change):,.2f}"
            change_class = "text-success"
        else:
            cost_change = "$0.00"
            change_class = "text-muted"
        
        # Create trend text
        if tariff_cost_change > 0:
            trend_percentage = (tariff_cost_change / past_tariff_cost * 100) if past_tariff_cost > 0 else 0
            trend_text = f"Importing ${import_value:,} worth of {product} from {country} costs ${current_tariff_cost:,.2f} in tariffs, which has increased by {trend_percentage:.1f}% in the {time_range_text}."
            trend_class = "text-danger"
        elif tariff_cost_change < 0:
            trend_percentage = (abs(tariff_cost_change) / past_tariff_cost * 100) if past_tariff_cost > 0 else 0
            trend_text = f"Importing ${import_value:,} worth of {product} from {country} costs ${current_tariff_cost:,.2f} in tariffs, which has decreased by {trend_percentage:.1f}% in the {time_range_text}."
            trend_class = "text-success"
        else:
            trend_text = f"Importing ${import_value:,} worth of {product} from {country} costs ${current_tariff_cost:,.2f} in tariffs, which has remained stable in the {time_range_text}."
            trend_class = "text-info"
        
        return filter_context, current_cost, cost_change, change_class, trend_text, trend_class, {'display': 'block'}
    
    return "", "$0.00", "$0.00", "text-muted", "Enter a valid import value to calculate impact.", "text-muted", {'display': 'block'}

# Add a callback to update the period display based on time-range-radio
@callback(
    Output('period-display', 'children'),
    Input('time-range-radio', 'value')
)
def update_period_display(time_range):
    period_text = {
        30: "(Past Month)",
        90: "(Past 3 Months)",
        180: "(Past 6 Months)",
        365: "(Past Year)"
    }
    return period_text.get(time_range, "(Period)") 