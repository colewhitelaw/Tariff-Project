import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Register this page
dash.register_page(
    __name__,
    path='/tariff-trends',
    title='Global Tariff Dashboard - Tariff Trends',
    name='Tariff Trends'
)

import dash
from dash import dcc, html, callback, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import locale
import os

# Set locale to ensure dots are used for decimals
try:
    locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_NUMERIC, 'C')
    except locale.Error:
        pass  # Continue without setting locale

# Define data directory
DATA_DIR = 'Data'

# Load all data
tariff_df = pd.read_csv(os.path.join(DATA_DIR, 'tariff_frequency_by_rate_over_time.csv'))
import_df = pd.read_csv(os.path.join(DATA_DIR, 'example_import_data.csv'))
product_group_df = pd.read_csv(os.path.join(DATA_DIR, 'Product Group Imports Over Time.csv'))

# Load import share data
import_share_df = pd.read_csv(os.path.join(DATA_DIR, 'Tariff Rates and Imports by Product Group.csv'))
import_share_df.columns = import_share_df.columns.str.strip()  # Strip extra whitespace

# Get min and max years from the data
min_year = int(min(tariff_df['Year']))
max_year = int(max(tariff_df['Year']))

# List of tariff columns to analyze
tariff_columns = [
    'Duty-free (No Tariff)',
    '0 <= 5% Tariff',
    '5 <= 10% Tariff',
    '10 <= 15% Tariff',
    '15 <= 25% Tariff', 
    '25 <= 50% Tariff',
    '50 <= 100% Tariff',
    '> 100 % Tariff',
    'Non-Ad Valorem Duties'
]

# Define midpoint values for tariff ranges for x-axis
tariff_midpoints = {
    'Duty-free (No Tariff)': 0,
    '0 <= 5% Tariff': 2.5,
    '5 <= 10% Tariff': 7.5,
    '10 <= 15% Tariff': 12.5,
    '15 <= 25% Tariff': 20,
    '25 <= 50% Tariff': 37.5,
    '50 <= 100% Tariff': 75,
    '> 100 % Tariff': 125,
    'Non-Ad Valorem Duties': 150
}

# Get unique values for selections
countries = product_group_df['Country'].unique()
years = sorted(tariff_df['Year'].unique())
# Ensure value_types contains only the exact values that exist in the dataset
value_types = sorted(tariff_df['Value'].unique().tolist())
print(f"Available value types: {value_types}")

# Get unique countries for import share analysis
import_share_countries = [str(c).strip() for c in import_share_df['Country'].unique()]

# Custom CSS for better styling
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap']

# Custom colors - using dark theme
colors = {
    'background': '#212529',  # Match home page dark background
    'text': '#ffffff',
    'header': '#ffffff',
    'card': '#212529',  # Match home page card background
    'accent': '#3182ce',
    'dark_blue': '#ffffff',
    'medium_blue': '#63b3ed',
    'light_blue': '#90cdf4',
    'tab_selected': '#3182ce',
    'tab_background': '#2d2d2d',
    'row_light': '#3d3d3d',
    'row_dark': '#2d2d2d'
}

# Create Dash app
app = dash.Dash(__name__, 
                title="Comprehensive Tariff Analysis Dashboard",
                external_stylesheets=external_stylesheets)

# Define the layout for the page
layout = dbc.Container([
    # Header Row
    dbc.Row([
        dbc.Col([
            html.H1("Comprehensive Tariff Analysis", className="text-info mt-2 mb-0 fw-bold"),
            html.P("Explore detailed tariff trends and their impact on trade", className="text-muted mb-2")
        ], width="auto")
    ], align="center", justify="between", className="mb-4"),
    
    # Tabs with Bootstrap styling
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs(id='tabs', active_tab='tab-1', children=[
                dbc.Tab(label='Scatter Plot Analysis', tab_id='tab-1'),
                dbc.Tab(label='Trend Analysis', tab_id='tab-2'),
                dbc.Tab(label='Distribution Analysis', tab_id='tab-3'),
                dbc.Tab(label='Import Share Analysis', tab_id='tab-4'),
                dbc.Tab(label='Product Treemap', tab_id='tab-5')
            ], className="card-header-tabs")
        , className="bg-primary"),
        dbc.CardBody([
            html.Div(id='tab-content', className="mt-2")
        ], className="p-2")
    ], className="shadow mb-4")
], fluid=True)

# Callback to manage tab content
@callback(
    Output('tab-content', 'children'),
    Input('tabs', 'active_tab')
)
def render_tab_content(tab):
    if tab == 'tab-1':
        # Scatter Plot Tab
        return dbc.Container([
            # Controls section
            dbc.Card([
                dbc.CardHeader("Analysis Controls", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Year:", className="mb-2"),
                            dcc.Slider(
                                id='scatter-year-slider',
                                min=min_year,
                                max=max_year,
                                value=max_year,
                                marks={str(year): str(year) for year in range(min_year, max_year + 1)},
                                step=None,
                                className="mb-4"
                            ),
                            
                            html.Label("Select Product Type:", className="mb-2"),
                            dbc.RadioItems(
                                id='scatter-product-type',
                                options=[
                                    {'label': 'Agricultural Products', 'value': 'Agricultural Products'},
                                    {'label': 'Non-agricultural Products', 'value': 'Non-agricultural Products'}
                                ],
                                value='Agricultural Products',
                                className="mb-4"
                            ),
                            
                            html.Label("Select Tariff Type:", className="mb-2"),
                            dbc.RadioItems(
                                id='scatter-tariff-type',
                                options=[
                                    {'label': 'MFN', 'value': 'MFN'},
                                    {'label': 'Final Bound', 'value': 'Final Bound'}
                                ],
                                value='MFN'
                            )
                        ])
                    ])
                ])
            ], className="shadow mb-4"),
            
            # Main content area
            dbc.Row([
                # Scatter plot section
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Tariff Rate vs Import Volume Analysis", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(
                                id='tariff-import-scatter',
                                style={'height': '750px'},
                                config={'displayModeBar': True}
                            )
                        ], className="p-0")
                    ], className="shadow")
                ], width=8),
                
                # Correlation analysis
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Correlation Analysis", className="bg-primary text-white"),
                        dbc.CardBody([
                            html.Div(id='correlation-stats')
                        ], className="p-0")
                    ], className="shadow")
                ], width=4)
            ])
        ], fluid=True)
    
    elif tab == 'tab-2':
        # Trend Analysis Tab
        return dbc.Container([
            # Controls section
            dbc.Card([
                dbc.CardHeader("Analysis Controls", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Product Type:", className="mb-2"),
                            dbc.Select(
                                id='trend-product-type',
                                options=[
                                    {'label': 'Agricultural Products', 'value': 'Agricultural Products'},
                                    {'label': 'Non-agricultural Products', 'value': 'Non-agricultural Products'}
                                ],
                                value='Agricultural Products',
                                className="mb-4"
                            ),
                            
                            html.Label("Select Tariff Type:", className="mb-2"),
                            dbc.Select(
                                id='trend-tariff-type',
                                options=[
                                    {'label': 'Final Bound', 'value': 'Final Bound'},
                                    {'label': 'MFN', 'value': 'MFN'}
                                ],
                                value='MFN',
                                className="mb-4"
                            ),
                            
                            html.Label("Select Tariff Category:", className="mb-2"),
                            dbc.Select(
                                id='trend-tariff-category',
                                options=[{'label': cat, 'value': cat} for cat in tariff_columns],
                                value='10 <= 15% Tariff',
                                className="mb-4"
                            ),
                            
                            html.Label("Select Year Range:", className="mb-2"),
                            dcc.RangeSlider(
                                id='trend-year-slider',
                                min=min_year,
                                max=max_year,
                                value=[min_year, max_year],
                                marks={str(year): str(year) for year in range(min_year, max_year + 1)},
                                step=None
                            )
                        ])
                    ])
                ])
            ], className="shadow mb-4"),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Tariff Rate Trends", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id='tariff-rate-chart')
                        ], className="p-0")
                    ], className="shadow")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Import Volume Trends", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id='import-volume-chart')
                        ], className="p-0")
                    ], className="shadow")
                ], width=6)
            ], className="mb-4"),
            
            # Explanation section
            dbc.Card([
                dbc.CardHeader("Understanding Trend Analysis", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(id='trend-explanation')
                ])
            ], className="shadow")
        ], fluid=True)
    
    elif tab == 'tab-3':
        # Distribution Analysis Tab
        return dbc.Container([
            # Controls section
            dbc.Card([
                dbc.CardHeader("Analysis Controls", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Year:", className="mb-2"),
                            dbc.Select(
                                id='dist-year',
                                options=[{'label': str(y), 'value': int(y)} for y in years],
                                value=int(max_year),
                                className="mb-4"
                            ),
                            
                            html.Label("Select Value Type:", className="mb-2"),
                            dbc.Select(
                                id='dist-value-type',
                                options=[{'label': v, 'value': v} for v in value_types],
                                value=value_types[0],
                                className="mb-4"
                            )
                        ])
                    ])
                ])
            ], className="shadow mb-4"),
            
            # Pie Chart and Histogram side by side
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Pie Chart", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id='dist-pie-chart')
                        ], className="p-0")
                    ], className="shadow")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Cumulative Distribution", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id='dist-cumulative-distribution')
                        ], className="p-0")
                    ], className="shadow")
                ], width=6)
            ], className="mb-4"),
            
            # Explanation section
            dbc.Card([
                dbc.CardHeader("Understanding Distribution Analysis", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(id='distribution-explanation')
                ])
            ], className="shadow")
        ], fluid=True)
    
    elif tab == 'tab-4':
        # Import Share Analysis Tab
        return dbc.Container([
            # Controls section
            dbc.Card([
                dbc.CardHeader("Analysis Controls", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Country (Tariff):", className="mb-2"),
                            dbc.Select(
                                id='share-country-tariff',
                                options=[{'label': c, 'value': c} for c in import_share_countries],
                                value=import_share_countries[0] if len(import_share_countries) > 0 else None,
                                className="mb-4"
                            )
                        ], width=6),
                        
                        dbc.Col([
                            html.Label("Select Country (Import):", className="mb-2"),
                            dbc.Select(
                                id='share-country-import',
                                options=[{'label': c, 'value': c} for c in import_share_countries],
                                value=import_share_countries[0] if len(import_share_countries) > 0 else None,
                                className="mb-4"
                            )
                        ], width=6)
                    ])
                ])
            ], className="shadow mb-4"),
            
            # Tariff and Import Share charts side by side
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Average Tariff Rate", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id='share-tariff-bar')
                        ], className="p-0")
                    ], className="shadow")
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Import Share", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id='share-import-bar')
                        ], className="p-0")
                    ], className="shadow")
                ], width=6)
            ], className="mb-4"),
            
            # Explanation section
            dbc.Card([
                dbc.CardHeader("Understanding Import Share Analysis", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(id='import-share-explanation')
                ])
            ], className="shadow")
        ], fluid=True)
    
    elif tab == 'tab-5':
        # Product Treemap Tab
        return dbc.Container([
            # Controls section
            dbc.Card([
                dbc.CardHeader("Analysis Controls", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Year:", className="mb-2"),
                            dcc.Slider(
                                id='treemap-year-slider',
                                min=min_year,
                                max=max_year,
                                value=max_year,  # Default to most recent year
                                marks={str(year): str(year) for year in range(min_year, max_year + 1)},
                                step=None,
                                className="mb-4"
                            )
                        ], style={'padding': '20px'})
                    ])
                ])
            ], className="shadow mb-4"),
            
            # Treemap visualization
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("US Imports Distribution", className="bg-primary text-white", 
                                      style={'border-radius': '0.375rem 0.375rem 0 0'}),
                        dbc.CardBody([
                            dcc.Graph(
                                id='import-treemap', 
                                style={
                                    'height': '800px',
                                    'width': '100%',
                                    'backgroundColor': '#212529'
                                },
                                config={
                                    'displayModeBar': False,  # Hide the mode bar completely
                                    'responsive': True
                                }
                            )
                        ], className="p-0", style={
                            'backgroundColor': '#212529', 
                            'border': 'none',
                            'padding': '0',
                            'margin': '0',
                            'overflow': 'hidden',
                            'borderRadius': '0 0 0.375rem 0.375rem'
                        })
                    ], className="shadow", style={
                        'backgroundColor': '#212529', 
                        'border': 'none',
                        'padding': '0',
                        'overflow': 'hidden',
                        'borderRadius': '0.375rem'
                    })
                ], width=12, style={'padding': '0'})
            ], className="mb-4", style={'margin': '0 0 1rem 0', 'padding': '0'}),
            
            # Statistics section
            dbc.Card([
                dbc.CardHeader("Import Distribution Statistics", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(id='product-stats')
                ])
            ], className="shadow")
        ], fluid=True)

# ==== Scatter Plot Tab Callbacks ====
@callback(
    [Output('tariff-import-scatter', 'figure'),
     Output('correlation-stats', 'children')],
    [Input('scatter-year-slider', 'value'),
     Input('scatter-product-type', 'value'),
     Input('scatter-tariff-type', 'value')]
)
def update_scatter(selected_year, product_type, tariff_type):
    # Filter data by selected criteria
    tariff_filtered = tariff_df[
        (tariff_df['Year'] == selected_year) & 
        (tariff_df['Value'].str.contains(product_type)) &
        (tariff_df['Value'].str.contains(tariff_type))
    ].copy()
    
    import_filtered = import_df[
        (import_df['Year'] == selected_year) &
        (import_df['Product_Type'] == product_type)
    ].copy()
    
    # Check if we have valid data
    if tariff_filtered.empty or import_filtered.empty:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for the selected criteria",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=30, color=colors['dark_blue'])
        )
        
        fig.update_layout(
            title=f'Tariff Rate vs Import Volume ({selected_year}, {product_type}, {tariff_type})',
            title_font_color=colors['dark_blue'],
            title_font_size=30,
            height=700,
            plot_bgcolor='rgba(45, 45, 45, 0.5)',
            paper_bgcolor=colors['card']
        )
        
        # Return empty stats
        stats_html = html.Div("No data available for the selected criteria", 
                              style={'textAlign': 'center', 'padding': '50px', 'color': colors['dark_blue'], 'fontSize': '24px'})
        return fig, stats_html
    
    # Prepare data for scatter plot
    # We need to join the tariff rate data with import volume data
    scatter_data = []
    
    # Using one row of the tariff data, since we've already filtered to specific criteria
    tariff_row = tariff_filtered.iloc[0]
    
    # For each tariff category, find the corresponding import volume
    for column in tariff_columns:
        # Find corresponding import data
        import_row = import_filtered[import_filtered['Category'] == column].iloc[0] if not import_filtered[import_filtered['Category'] == column].empty else None
        
        if import_row is not None:
            # Get tariff rate (x-axis)
            tariff_rate = tariff_midpoints[column]
            
            # Get import volume (y-axis)
            import_volume = import_row['Import_Volume_Billion_USD']
            
            # Tariff frequency percentage
            tariff_frequency = tariff_row[column]
            
            scatter_data.append({
                'Tariff_Rate': tariff_rate,
                'Import_Volume': import_volume,
                'Tariff_Frequency': tariff_frequency,
                'Category': column
            })
    
    # Convert to DataFrame for plotting
    scatter_df = pd.DataFrame(scatter_data)
    
    # Create scatter plot
    fig = px.scatter(
        scatter_df,
        x='Tariff_Rate',
        y='Import_Volume',
        size='Tariff_Frequency',
        color='Category',
        hover_name='Category',
        text='Category',
        title=f'Tariff Rate vs Import Volume ({selected_year}, {product_type}, {tariff_type})',
        labels={
            'Tariff_Rate': 'Tariff Rate (%)',
            'Import_Volume': 'Import Volume (Billion USD)',
            'Tariff_Frequency': 'Tariff Frequency (%)'
        },
        size_max=50,
        height=900,  # Increased height
        color_discrete_sequence=px.colors.sequential.Blues_r
    )

    # Calculate and add regression line with correlation coefficient
    if len(scatter_df) > 1:
        x_values = scatter_df['Tariff_Rate']
        y_values = scatter_df['Import_Volume']
        
        # Calculate regression line
        coefficients = np.polyfit(x_values, y_values, 1)
        polynomial = np.poly1d(coefficients)
        
        # Calculate correlation coefficient
        r = np.corrcoef(x_values, y_values)[0, 1]
        
        # Add regression line
        x_range = np.linspace(min(x_values), max(x_values), 100)
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=polynomial(x_range),
                mode='lines',
                name=f'Regression Line (r = {r:.3f})',
                line=dict(color='#ffffff', width=2, dash='dash'),
                hovertemplate='r = ' + f'{r:.3f}<extra></extra>'
            )
        )

    # Update layout
    fig = update_scatter_layout(fig)

    # Create analysis stats with improved table styling
    stats_html = html.Div([
        html.Table([
            html.Thead(html.Tr([
                html.Th("Tariff Category", style={
                    'backgroundColor': '#1a202c',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'padding': '12px 20px',
                    'fontSize': '16px',
                    'borderBottom': '2px solid #4299e1',
                    'textAlign': 'left'
                }),
                html.Th("Tariff Rate (%)", style={
                    'backgroundColor': '#1a202c',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'padding': '12px 20px',
                    'fontSize': '16px',
                    'borderBottom': '2px solid #4299e1',
                    'textAlign': 'right'
                }),
                html.Th("Import Volume (Billion USD)", style={
                    'backgroundColor': '#1a202c',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'padding': '12px 20px',
                    'fontSize': '16px',
                    'borderBottom': '2px solid #4299e1',
                    'textAlign': 'right'
                }),
                html.Th("Tariff Frequency (%)", style={
                    'backgroundColor': '#1a202c',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'padding': '12px 20px',
                    'fontSize': '16px',
                    'borderBottom': '2px solid #4299e1',
                    'textAlign': 'right'
                })
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(row['Category'], style={
                        'padding': '12px 20px',
                        'fontSize': '15px',
                        'borderBottom': '1px solid #2d3748',
                        'color': '#e2e8f0',
                        'textAlign': 'left'
                    }),
                    html.Td(f"{row['Tariff_Rate']:.1f}%".replace(',', '.'), style={
                        'padding': '12px 20px',
                        'fontSize': '15px',
                        'borderBottom': '1px solid #2d3748',
                        'color': '#e2e8f0',
                        'textAlign': 'right'
                    }),
                    html.Td(f"${row['Import_Volume']:.1f}B".replace(',', '.'), style={
                        'padding': '12px 20px',
                        'fontSize': '15px',
                        'borderBottom': '1px solid #2d3748',
                        'color': '#e2e8f0',
                        'textAlign': 'right'
                    }),
                    html.Td(f"{row['Tariff_Frequency']:.1f}%".replace(',', '.'), style={
                        'padding': '12px 20px',
                        'fontSize': '15px',
                        'borderBottom': '1px solid #2d3748',
                        'color': '#e2e8f0',
                        'textAlign': 'right'
                    })
                ], style={
                    'backgroundColor': '#1a1a1a',
                    'transition': 'background-color 0.2s',
                    ':hover': {'backgroundColor': '#2d3748'}
                })
                for _, row in scatter_df.sort_values('Import_Volume', ascending=False).iterrows()
            ])
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'backgroundColor': '#1a1a1a',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'
        })
    ], style={
        'padding': '10px',
        'backgroundColor': colors['background'],
        'borderRadius': '8px'
    })
    
    return fig, stats_html

# ==== Trend Analysis Tab Callbacks ====
@callback(
    [Output('tariff-rate-chart', 'figure'),
     Output('import-volume-chart', 'figure')],
    [Input('trend-product-type', 'value'),
     Input('trend-tariff-type', 'value'),
     Input('trend-tariff-category', 'value'),
     Input('trend-year-slider', 'value')]
)
def update_trend_charts(product_type, tariff_type, tariff_category, year_range):
    # Extract year range values
    start_year, end_year = year_range
    
    # Filter tariff data by product type, tariff type, and year range
    filtered_tariff_df = tariff_df[
        (tariff_df['Value'].str.contains(f"{product_type}, {tariff_type}")) &
        (tariff_df['Year'] >= start_year) &
        (tariff_df['Year'] <= end_year)
    ]
    
    # Create tariff rate chart with blue colors
    tariff_fig = go.Figure()
    
    tariff_fig.add_trace(
        go.Scatter(
            x=filtered_tariff_df['Year'],
            y=filtered_tariff_df[tariff_category],
            name='Tariff Rate',
            line=dict(color=colors['medium_blue'], width=3),
            mode='lines+markers',
            marker=dict(size=10, color=colors['dark_blue'])
        )
    )
    
    # Set y-axis title for tariff rate
    tariff_fig.update_yaxes(title_text="Tariff Rate (%)")
    
    tariff_fig = update_trend_layout(tariff_fig)
    
    # Filter import data by product type, category, and year range
    filtered_import_df = import_df[
        (import_df['Product_Type'] == product_type) & 
        (import_df['Category'] == tariff_category) &
        (import_df['Year'] >= start_year) &
        (import_df['Year'] <= end_year)
    ]
    
    # Create import volume chart
    import_fig = go.Figure()
    
    import_fig.add_trace(
        go.Scatter(
            x=filtered_import_df['Year'],
            y=filtered_import_df['Import_Volume_Billion_USD'],
            name='Import Volume',
            line=dict(color=colors['accent'], width=3),
            mode='lines+markers',
            marker=dict(size=10, color=colors['dark_blue'])
        )
    )
    
    # Set y-axis title for import volume
    import_fig.update_yaxes(title_text="Import Volume (Billion USD)")
    
    import_fig = update_trend_layout(import_fig)
    
    return tariff_fig, import_fig

# ==== Distribution Analysis Tab Callbacks ====
@callback(
    [Output('dist-pie-chart', 'figure'),
     Output('dist-cumulative-distribution', 'figure')],
    [Input('dist-year', 'value'),
     Input('dist-value-type', 'value')]
)
def update_distribution_charts(selected_year, selected_value):
    # Filter tariff data
    tariff_bins = [
        'Duty-free (No Tariff)', '0 <= 5% Tariff', '5 <= 10% Tariff', '10 <= 15% Tariff',
        '15 <= 25% Tariff', '25 <= 50% Tariff', '50 <= 100% Tariff', '> 100 % Tariff'
    ]
    
    # Convert selected_year to int if it's not already (dropdown might return it as a string)
    try:
        selected_year = int(selected_year)
    except (ValueError, TypeError):
        print(f"Error converting selected_year: {selected_year} to int")
    
    # Print debug info
    print(f"Selected Year: {selected_year}, type: {type(selected_year)}")
    print(f"Selected Value: {selected_value}")
    
    # Check if there's any data for the selected year
    years_in_df = tariff_df['Year'].unique()
    print(f"Years in DataFrame: {years_in_df}")
    
    # Improved filtering with strict type checking and debug information
    year_filter = tariff_df['Year'] == selected_year
    value_filter = tariff_df['Value'] == selected_value
    
    print(f"Year filter matches: {year_filter.sum()}")
    print(f"Value filter matches: {value_filter.sum()}")
    print(f"Combined filter matches: {(year_filter & value_filter).sum()}")
    
    row = tariff_df[year_filter & value_filter]
    
    if row.empty:
        print(f"No data found for Year: {selected_year}, Value: {selected_value}")
        # Return empty figures if no data
        empty_pie = px.pie(names=["No Data Available"], values=[1])
        empty_cdf = px.line(x=[0, 100], y=[0, 100])
        
        # Apply styling to empty figures
        empty_pie.update_layout(
            font=dict(family="Roboto", size=16, color=colors['dark_blue']),
            paper_bgcolor=colors['card'],
            height=500,
            showlegend=False,
            title=f"No data available for {selected_year}, {selected_value}"
        )
        
        empty_cdf.update_layout(
            font=dict(family="Roboto", size=16, color=colors['dark_blue']),
            paper_bgcolor=colors['card'],
            height=500,
            showlegend=False,
            title=f"No data available for {selected_year}, {selected_value}"
        )
        
        return empty_pie, empty_cdf
    
    row = row.iloc[0]
    print(f"Found data for selected criteria: {row['Year']}, {row['Value']}")

    # Define consistent colors for both charts
    color_sequence = ['#2c5282', '#3182ce', '#4299e1', '#63b3ed', '#90cdf4', '#bee3f8', '#ebf8ff', '#f7fafc']
    
    # Create pie chart with consistent colors
    pie_fig = px.pie(
        names=tariff_bins, 
        values=row[tariff_bins].values,
        color_discrete_sequence=color_sequence
    )
    
    # Update pie chart styling
    pie_fig = update_distribution_layout(pie_fig)
    
    pie_fig.update_traces(
        textposition='inside',
        textinfo='label+percent',
        textfont=dict(size=16, color='white', family='Roboto'),
        insidetextfont=dict(size=16, color='white', family='Roboto')
    )
    
    # Create cumulative distribution line plot (CDF)
    cdf_data = pd.DataFrame({
        'bin': tariff_bins,
        'value': row[tariff_bins].values
    })
    cdf_data['cumulative'] = cdf_data['value'].cumsum() / cdf_data['value'].sum() * 100

    cdf_fig = go.Figure()
    cdf_fig.add_trace(go.Scatter(
        x=cdf_data['bin'],
        y=cdf_data['cumulative'],
        mode='lines+markers',
        line=dict(color='#3182ce', width=4),
        marker=dict(size=12, color='#63b3ed'),
        name='Cumulative % of Imports',
        hovertemplate='%{y:.1f}% of imports ≤ %{x}'
    ))
    cdf_fig.update_layout(
        yaxis_title='Cumulative % of Imports',
        xaxis_title='Tariff Bin',
        font=dict(family="Roboto", size=16, color=colors['dark_blue']),
        paper_bgcolor=colors['card'],
        plot_bgcolor=colors['card'],
        title=f'Cumulative Distribution of Imports by Tariff Bin ({selected_year}, {selected_value})',
        height=500
    )

    return pie_fig, cdf_fig

# ==== Import Share Analysis Tab Callbacks ====
@callback(
    [Output('share-tariff-bar', 'figure'),
     Output('share-import-bar', 'figure')],
    [Input('share-country-tariff', 'value'),
     Input('share-country-import', 'value')]
)
def update_share_bars(country_tariff, country_import):
    # Print debug info
    print(f"Selected countries: '{country_tariff}', '{country_import}'")
    
    # Filter data for tariff chart
    df_tariff = import_share_df[import_share_df['Country'].str.strip() == country_tariff]
    df_tariff = df_tariff.sort_values(by='Import Share %', ascending=False)
    
    print(f"Tariff data shape: {df_tariff.shape}")
    
    # Filter data for import chart
    df_import = import_share_df[import_share_df['Country'].str.strip() == country_import]
    df_import = df_import.sort_values(by='Import Share %', ascending=False)
    
    print(f"Import data shape: {df_import.shape}")
    
    # Create tariff bar chart
    fig_tariff = px.bar(
        df_tariff,
        y='Product Group',
        x='Average Tariff Rate, MFN',
        orientation='h',
        title=f"Average Tariff Rate by Product Group - {country_tariff}",
        labels={'Average Tariff Rate, MFN': 'Tariff (%)'},
        color='Average Tariff Rate, MFN',
        color_continuous_scale=px.colors.sequential.Blues,
        height=600
    )
    
    fig_tariff = update_share_layout(fig_tariff)
    
    # Create import bar chart
    fig_import = px.bar(
        df_import,
        y='Product Group',
        x='Import Share %',
        orientation='h',
        title=f"Import Share by Product Group - {country_import}",
        labels={'Import Share %': 'Share (%)'},
        color='Import Share %',
        color_continuous_scale=px.colors.sequential.Blues,
        height=600
    )
    
    fig_import = update_share_layout(fig_import)
    
    return fig_tariff, fig_import

# Helper functions
def get_correlation_interpretation(r, product_type):
    """Return interpretation of correlation coefficient."""
    abs_r = abs(r)
    
    if abs_r < 0.2:
        strength = "very weak"
    elif abs_r < 0.4:
        strength = "weak"
    elif abs_r < 0.6:
        strength = "moderate"
    elif abs_r < 0.8:
        strength = "strong"
    else:
        strength = "very strong"
    
    direction = "positive" if r > 0 else "negative"
    
    if abs_r < 0.1:
        conclusion = f"This suggests there is almost no relationship between tariff rates and import volumes for {product_type.lower()} overall."
    elif 0.1 <= abs_r < 0.3:
        if r > 0:
            conclusion = f"This suggests that higher tariffs don't significantly deter imports for most {product_type.lower()}."
        else:
            conclusion = f"This suggests a slight tendency for imports to decrease as tariff rates increase for {product_type.lower()}, but the relationship is weak."
    elif 0.3 <= abs_r < 0.5:
        if r > 0:
            conclusion = f"This suggests that factors beyond tariffs significantly influence import volumes for {product_type.lower()}."
        else:
            conclusion = f"This shows some evidence that higher tariffs may reduce imports of {product_type.lower()}, but other factors also play important roles."
    elif 0.5 <= abs_r < 0.7:
        if r > 0:
            conclusion = f"This suggests a potential counterintuitive relationship where higher tariffs are associated with higher import volumes for {product_type.lower()}, possibly due to inelastic demand."
        else:
            conclusion = f"This indicates a substantial relationship where higher tariffs appear to reduce import volumes of {product_type.lower()} significantly."
    else:
        if r > 0:
            conclusion = f"This shows a strong relationship where import volumes increase with tariff rates for {product_type.lower()}, suggesting tariffs may be targeting high-demand products that continue to be imported despite higher costs."
        else:
            conclusion = f"This shows a clear relationship where higher tariffs strongly correspond to lower import volumes for {product_type.lower()}, indicating strong price sensitivity."
    
    return f"There is a {strength} {direction} correlation between tariff rates and import volumes for {product_type.lower()} (r = {r:.3f}). {conclusion}"

# Add new callback for trend explanation
@callback(
    Output('trend-explanation', 'children'),
    [Input('trend-product-type', 'value'),
     Input('trend-tariff-type', 'value'),
     Input('trend-tariff-category', 'value')]
)
def update_trend_explanation(product_type, tariff_type, category):
    trend_text = [
        html.P(f"This chart displays how {'all products' if product_type == 'all' else product_type} tariff rates and import volumes change over time.", 
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P(f"The left chart shows the evolution of the {tariff_type} tariff rates for {'specific categories' if category != 'all' else 'all categories'} from 2012 to 2021.",
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P("The right chart displays the corresponding import volumes over the same period, allowing you to observe potential relationships between tariff rates and trade volumes.",
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P([
            "Key insights: ",
            html.Ul([
                html.Li("Declining tariff rates often correlate with increased import volumes, reflecting trade liberalization effects", 
                      style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Li("Sharp increases in tariff rates may indicate trade disputes or protectionist policies", 
                      style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Li("Stable tariff periods typically show more predictable import volume patterns", 
                      style={'fontSize': '16px', 'marginBottom': '10px'})
            ])
        ], style={'fontSize': '16px', 'marginBottom': '15px'})
    ]
    return trend_text

# Add new callback for distribution explanation
@callback(
    Output('distribution-explanation', 'children'),
    [Input('dist-year', 'value'),
     Input('dist-value-type', 'value')]
)
def update_distribution_explanation(selected_year, value_type):
    value_desc = "tariff rates" if value_type == 'tariff' else "import volumes"
    
    dist_text = [
        html.P(f"These visualizations show the distribution of {value_desc} across different product categories for {selected_year}.", 
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P(f"The pie chart displays the proportional share of each product category, highlighting which sectors dominate in terms of {value_desc}.",
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P(f"The cumulative distribution line plot shows the cumulative percentage of {value_desc} up to each tariff bin.",
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P([
            "How to interpret these charts: ",
            html.Ul([
                html.Li("Larger pie segments represent categories with higher proportional values", 
                      style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Li("The cumulative distribution line plot shows the cumulative percentage of imports up to each tariff bin", 
                      style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Li("Higher bars on the cumulative distribution line plot indicate more products with high values", 
                      style={'fontSize': '16px', 'marginBottom': '10px'})
            ])
        ], style={'fontSize': '16px', 'marginBottom': '15px'})
    ]
    return dist_text

# Add new callback for import share explanation
@callback(
    Output('import-share-explanation', 'children'),
    [Input('share-country-tariff', 'value')]
)
def update_import_share_explanation(selected_countries):
    country_text = "the selected countries" if selected_countries else "no countries"
    
    share_text = [
        html.P(f"These bar charts compare the average tariff rates and import market shares for {country_text}.", 
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P("The left chart displays the average tariff rate applied to each country's exports, allowing you to compare trade policy treatment across nations.",
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P("The right chart shows each country's share of total imports, indicating their relative importance as trading partners.",
              style={'fontSize': '16px', 'marginBottom': '15px'}),
        html.P([
            "Key observations: ",
            html.Ul([
                html.Li("Countries with lower tariff rates often have preferential trade agreements or free trade deals", 
                      style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Li("Higher import shares typically indicate stronger economic relationships or strategic trade dependencies", 
                      style={'fontSize': '16px', 'marginBottom': '10px'}),
                html.Li("Comparing both charts can reveal potential correlations between tariff policies and trade volumes", 
                      style={'fontSize': '16px', 'marginBottom': '10px'})
            ])
        ], style={'fontSize': '16px', 'marginBottom': '15px'})
    ]
    return share_text

# ==== Product Treemap Tab Callbacks ====
@callback(
    [Output('import-treemap', 'figure'),
     Output('product-stats', 'children')],
    [Input('treemap-year-slider', 'value')]
)
def update_treemap(selected_year):
    try:
        # Hard-coded data for years 2015-2024
        hard_coded_data = {
            2015: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.4},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.2},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 10.5},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 9.8},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 8.9},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.4},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 2.0},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.0},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.8},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 18.5},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 11.2},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 7.4},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.6}
            ],
            2016: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.3},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.2},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 10.2},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 9.2},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.0},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.4},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.9},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.0},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.9},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 18.7},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 11.4},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 7.3},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.5}
            ],
            2017: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.3},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.1},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 10.6},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 9.5},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.1},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.5},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.8},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.1},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.7},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 18.4},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 11.6},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 7.2},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.4}
            ],
            2018: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.2},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.1},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 11.0},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 10.0},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.3},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.6},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.8},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.1},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.5},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 18.2},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 11.7},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 7.0},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.3}
            ],
            2019: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.2},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.1},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 11.2},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 9.2},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.4},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.6},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.7},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.2},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.5},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 18.2},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 12.0},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 7.1},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.2}
            ],
            2020: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.2},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.1},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 11.4},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 8.6},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.5},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.6},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.7},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.2},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.4},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 18.1},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 11.9},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 7.1},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.2}
            ],
            2021: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.1},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 2.0},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.6},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 1.0},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.6},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 12.2},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 9.4},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.7},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 4.1},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.8},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.3},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.1},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 17.5},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 11.5},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 6.9},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 3.0}
            ],
            2022: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 1.0},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 1.9},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 1.0},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 1.1},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.7},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 11.8},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 10.3},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 9.9},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.8},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.6},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.4},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.2},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 16.9},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 12.1},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 6.7},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 2.8}
            ],
            2023: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 1.8},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 1.1},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 1.2},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 11.5},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 8.9},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 10.1},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.5},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.5},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.5},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.5},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 16.8},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 12.7},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 6.5},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 2.7}
            ],
            2024: [
                {"Product Group": "Live animals and meat", "Category": "Agricultural", "Percent of Imports": 0.8},
                {"Product Group": "Dairy products", "Category": "Agricultural", "Percent of Imports": 0.2},
                {"Product Group": "Fruits and vegetables", "Category": "Agricultural", "Percent of Imports": 1.7},
                {"Product Group": "Coffee, tea, cocoa and spices", "Category": "Agricultural", "Percent of Imports": 1.2},
                {"Product Group": "Cereals and food preparations", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Oilseeds, fats and oils", "Category": "Agricultural", "Percent of Imports": 0.5},
                {"Product Group": "Sugars and confectionery", "Category": "Agricultural", "Percent of Imports": 0.3},
                {"Product Group": "Beverages and tobacco", "Category": "Agricultural", "Percent of Imports": 1.2},
                {"Product Group": "Cotton, silk and wool", "Category": "Agricultural", "Percent of Imports": 0.1},
                {"Product Group": "Other agricultural products", "Category": "Agricultural", "Percent of Imports": 0.9},
                {"Product Group": "Fish and fish products", "Category": "Agricultural", "Percent of Imports": 0.4},
                {"Product Group": "Minerals and metals", "Category": "Raw Materials", "Percent of Imports": 11.4},
                {"Product Group": "Petroleum", "Category": "Raw Materials", "Percent of Imports": 8.6},
                {"Product Group": "Chemicals", "Category": "Industrial", "Percent of Imports": 10.3},
                {"Product Group": "Wood, paper, furniture", "Category": "Industrial", "Percent of Imports": 3.3},
                {"Product Group": "Textiles", "Category": "Industrial", "Percent of Imports": 1.4},
                {"Product Group": "Rubber, leather and footwear", "Category": "Industrial", "Percent of Imports": 3.6},
                {"Product Group": "Mechanical, office and computing machinery", "Category": "Technology", "Percent of Imports": 14.4},
                {"Product Group": "Electrical machinery and electronic equipment", "Category": "Technology", "Percent of Imports": 17.1},
                {"Product Group": "Transport equipment", "Category": "Technology", "Percent of Imports": 13.0},
                {"Product Group": "Other Manufactures", "Category": "Other", "Percent of Imports": 6.6},
                {"Product Group": "Clothing", "Category": "Other", "Percent of Imports": 2.6}
            ]
        }
        
        # Ensure selected_year is an integer
        try:
            selected_year_int = int(selected_year)
        except (ValueError, TypeError):
            selected_year_int = 2022  # Default to 2022 if conversion fails
        print('DEBUG: selected_year_int used for treemap:', selected_year_int)

        # Default to closest available year if selected year is not in the dataset
        if selected_year_int not in hard_coded_data:
            available_years = sorted(list(hard_coded_data.keys()))
            if selected_year_int < min(available_years):
                selected_year_int = min(available_years)
            elif selected_year_int > max(available_years):
                selected_year_int = max(available_years)
            else:
                # Find the closest year
                selected_year_int = min(available_years, key=lambda x: abs(x - selected_year_int))
        print('DEBUG: selected_year_int after adjustment:', selected_year_int)

        # Get data for selected year
        year_data = hard_coded_data[selected_year_int]

        # Print debug information to understand the data
        print(f"DEBUG: Raw data for year {selected_year_int}:")
        for item in year_data[:3]:  # Print first 3 items as sample
            print(f"  {item}")
        
        # Ensure all data has proper category and product group values
        for item in year_data:
            if 'Category' not in item or not item['Category']:
                item['Category'] = 'Uncategorized'
            if 'Product Group' not in item or not item['Product Group']:
                item['Product Group'] = 'Other Products'
            if 'Percent of Imports' not in item or not isinstance(item['Percent of Imports'], (int, float)):
                item['Percent of Imports'] = 0.0

        # Convert to DataFrame for easier processing
        import pandas as pd
        df = pd.DataFrame(year_data)
        
        # Fallback: if df is empty, show a message
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text='No data available for this year or data is malformed.',
                xref='paper', yref='paper',
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color='red')
            )
            fig.update_layout(
                title='US Import Distribution by Product Group',
                height=800,
                plot_bgcolor='#212529',
                paper_bgcolor='#212529'
            )
            stats_html = html.Div(
                'No data available for this year or data is malformed.',
                style={'textAlign': 'center', 'padding': '50px', 'color': 'red', 'fontSize': '20px'}
            )
            return fig, stats_html
        
        # Debug output to verify the DataFrame is correct
        print(f"DEBUG: Data for {selected_year_int}:")
        print(df[['Category', 'Product Group', 'Percent of Imports']].head())
        print(f"Total categories: {df['Category'].nunique()}")
        print(f"Category sums:")
        for category in df['Category'].unique():
            cat_sum = df[df['Category'] == category]['Percent of Imports'].sum()
            print(f"  {category}: {cat_sum:.1f}%")
        
        print(f"Technology category value: {df[df['Category'] == 'Technology']['Percent of Imports'].sum():.1f}%")
        print(f"Electrical machinery value: {df[df['Product Group'] == 'Electrical machinery and electronic equipment']['Percent of Imports'].iloc[0] if not df[df['Product Group'] == 'Electrical machinery and electronic equipment'].empty else 'Not found'}%")
        
        # Process DataFrame to prepare for treemap
        # Create a more structured DataFrame with both levels of hierarchy
        # First get category totals
        category_totals = df.groupby('Category')['Percent of Imports'].sum().reset_index()
        
        # Create entry for each category (parent level)
        treemap_data = []
        for _, cat_row in category_totals.iterrows():
            treemap_data.append({
                'id': cat_row['Category'],
                'parent': '',
                'label': cat_row['Category'].upper(),
                'value': cat_row['Percent of Imports']
            })
            
            # Add product entries for this category (child level)
            category_products = df[df['Category'] == cat_row['Category']]
            for _, prod_row in category_products.iterrows():
                prod_id = f"{cat_row['Category']}_{prod_row['Product Group']}"
                treemap_data.append({
                    'id': prod_id,
                    'parent': cat_row['Category'],
                    'label': prod_row['Product Group'],
                    'value': prod_row['Percent of Imports']
                })
        
        # Convert to DataFrame
        treemap_df = pd.DataFrame(treemap_data)
        
        # Debug output
        print("DEBUG: Treemap data structure:")
        print(treemap_df.head(10))

        # Process data to create scaled text sizes based on values
        # Scale font sizes based on the percentage value
        def get_font_size(value):
            # Base size is 12, max is 18, scale logarithmically between them
            import math
            if value < 0.5:  # Very small values get minimum size
                return 8
            elif value < 1:
                return 10
            elif value < 3:
                return 12
            elif value < 10:
                return 14
            else:
                return 16
        
        # Add font size column to dataframe for scaling
        treemap_df['font_size'] = treemap_df['value'].apply(get_font_size)
        
        # Create a simpler treemap with basic, functional text display
        fig = go.Figure(go.Treemap(
            ids=treemap_df['id'],
            labels=treemap_df['label'],
            parents=treemap_df['parent'],
            values=treemap_df['value'],
            branchvalues='total',
            # Simple text format
            text=treemap_df['label'] + '<br>' + treemap_df['value'].apply(lambda x: f"{x:.1f}%"),
            hovertemplate='<b>%{label}</b><br>%{value:.1f}% of Imports<extra></extra>',
            # Configure tile settings
            tiling=dict(
                packing='squarify',
                pad=2
            ),
            # Add pathbar for easier navigation
            pathbar=dict(
                visible=True,
                side='top',
                thickness=20
            ),
            marker=dict(
                line=dict(width=1.5, color='#000000'),
                colors=[
                    '#2b6cb0' if row['id'] == 'Technology' or row['parent'] == 'Technology' else
                    '#38b2ac' if row['id'] == 'Industrial' or row['parent'] == 'Industrial' else
                    '#dd6b20' if row['id'] == 'Agricultural' or row['parent'] == 'Agricultural' else
                    '#805ad5' if row['id'] == 'Raw Materials' or row['parent'] == 'Raw Materials' else
                    '#3182ce' if row['id'] == 'Other' or row['parent'] == 'Other' else
                    '#90cdf4'  # Default color
                    for _, row in treemap_df.iterrows()
                ]
            ),
            textinfo="text",
            textposition="middle center",
            textfont=dict(
                family="Arial",
                size=12,
                color="white"
            )
        ))
        
        # Update layout with simplified settings
        fig.update_layout(
            margin=dict(t=70, l=20, r=20, b=20),  # More top margin for pathbar
            paper_bgcolor='#212529',
            plot_bgcolor='#212529',
            font=dict(
                family='Arial', 
                size=14, 
                color='white'
            ),
            height=800,
            hoverlabel=dict(
                bgcolor="rgba(10, 20, 30, 0.95)",
                font_size=16,
                font_family="Arial",
                font_color="#ffffff"
            )
        )
        
        # Prepare statistics
        # Calculate category totals using the DataFrame
        category_totals = df.groupby('Category')['Percent of Imports'].sum().reset_index()
        category_totals = category_totals.sort_values('Percent of Imports', ascending=False)
        
        # Get top products directly from the DataFrame
        product_totals = df.sort_values('Percent of Imports', ascending=False)
        top_products = product_totals.head(5)
        
        # Table styling
        table_header_style = {
            'backgroundColor': '#2c5282',
            'color': 'white', 
            'fontWeight': 'bold', 
            'padding': '16px 20px',
            'fontSize': '18px',
            'borderBottom': '2px solid #90cdf4',
            'textAlign': 'left'
        }
        
        table_cell_style = {
            'padding': '14px 20px',
            'fontSize': '16px',
            'color': '#e2e8f0',
            'borderBottom': '1px solid #4a5568',
            'backgroundColor': '#1a202c',
            'transition': 'background-color 0.2s'
        }
        
        percent_cell_style = {
            'padding': '14px 20px',
            'fontSize': '18px',
            'fontWeight': 'bold',
            'color': '#63b3ed',
            'borderBottom': '1px solid #4a5568',
            'backgroundColor': '#1a202c',
            'textAlign': 'right',
            'transition': 'background-color 0.2s'
        }
        
        table_style = {
            'width': '100%', 
            'borderCollapse': 'separate',
            'borderSpacing': '0',
            'backgroundColor': '#1a202c',
            'borderRadius': '8px',
            'overflow': 'hidden',
            'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.3)'
        }
        
        # Create category rows from DataFrame
        category_rows = []
        for _, row in category_totals.iterrows():
            category_rows.append(
                html.Tr([
                    html.Td(row['Category'], style=table_cell_style), 
                    html.Td(f"{row['Percent of Imports']:.1f}%", style=percent_cell_style)
                ], style={'hover': {'backgroundColor': '#2d3748'}})
            )
        
        # Create product rows from DataFrame
        product_rows = []
        for _, row in top_products.iterrows():
            product_rows.append(
                html.Tr([
                    html.Td(row['Product Group'], style=table_cell_style), 
                    html.Td(f"{row['Percent of Imports']:.1f}%", style=percent_cell_style)
                ], style={'hover': {'backgroundColor': '#2d3748'}})
            )
        
        # Create statistics HTML
        stats_html = [
            html.Div([
                html.Div([
                    html.H4("Top Import Categories", style={
                        'color': 'white', 
                        'fontSize': '22px', 
                        'fontWeight': 'bold',
                        'marginBottom': '15px',
                        'borderLeft': '4px solid #3182ce',
                        'paddingLeft': '10px'
                    }),
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Category", style=table_header_style), 
                            html.Th("% of Imports", style={**table_header_style, 'textAlign': 'right'})
                        ])),
                        html.Tbody(category_rows)
                    ], style=table_style)
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
                
                html.Div([
                    html.H4("Top 5 Product Groups", style={
                        'color': 'white', 
                        'fontSize': '22px', 
                        'fontWeight': 'bold',
                        'marginBottom': '15px',
                        'borderLeft': '4px solid #3182ce',
                        'paddingLeft': '10px'
                    }),
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Product Group", style=table_header_style), 
                            html.Th("% of Imports", style={**table_header_style, 'textAlign': 'right'})
                        ])),
                        html.Tbody(product_rows)
                    ], style=table_style)
                ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
            ], style={'padding': '15px 0'})
        ]
        
        return fig, stats_html
        
    except Exception as e:
        import traceback
        print(f"Error in update_treemap: {str(e)}")
        print(traceback.format_exc())
        
        # Create error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating treemap: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color='red')
        )
        fig.update_layout(
            title=f'US Import Distribution by Product Group',
            height=800,
            plot_bgcolor='rgba(45, 45, 45, 0.5)',
            paper_bgcolor=colors['card']
        )
        
        # Error message for stats
        stats_html = html.Div(
            f"Error processing data: {str(e)}",
            style={'textAlign': 'center', 'padding': '50px', 'color': 'red', 'fontSize': '20px'}
        )
        
        return fig, stats_html

# Add treemap explanation callback if needed
@callback(
    Output('treemap-explanation', 'children'),
    [Input('treemap-year-slider', 'value')]
)
def update_treemap_explanation(selected_year):
    # Simple empty placeholder since the explanation is not needed
    return html.Div([])

# Update the scatter plot layout
def update_scatter_layout(fig):
    # Dynamically calculate axis ranges with padding
    x_data = []
    y_data = []
    for trace in fig.data:
        if hasattr(trace, 'x') and hasattr(trace, 'y'):
            x_data.extend(trace.x)
            y_data.extend(trace.y)
    if x_data and y_data:
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        x_pad = (x_max - x_min) * 0.1 if x_max > x_min else 5
        y_pad = (y_max - y_min) * 0.1 if y_max > y_min else 5
        x_range = [x_min - x_pad, x_max + x_pad]
        y_range = [y_min - y_pad, y_max + y_pad]
    else:
        x_range = None
        y_range = None

    fig.update_layout(
        title_font_size=24,
        title_font_color='#ffffff',
        title_x=0.5,
        showlegend=True,
        height=750,
        plot_bgcolor='#212529',
        paper_bgcolor='#212529',
        font=dict(family="Roboto", size=14, color='#ffffff'),
        xaxis=dict(
            title=dict(
                text="Tariff Rate (%)",
                font=dict(size=16, color='#ffffff'),
                standoff=30
            ),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255, 255, 255, 0.1)',
            ticksuffix='%',
            automargin=True,
            range=x_range,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(
                text="Import Volume (Billion USD)",
                font=dict(size=16, color='#ffffff'),
                standoff=30
            ),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255, 255, 255, 0.1)',
            automargin=True,
            range=y_range,
            zeroline=False
        ),
        margin=dict(l=80, r=40, t=120, b=120),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(33, 37, 41, 0.8)',
            font=dict(size=12, color='#ffffff'),
            title=None
        )
    )
    return fig

# Update the trend charts layout
def update_trend_layout(fig):
    fig.update_layout(
        title_font_color='#ffffff',
        title_font_size=20,
        title_x=0.5,
        font=dict(family="Roboto", size=14, color='#ffffff'),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=16, color='#ffffff')),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            title=dict(text=fig.layout.yaxis.title.text if fig.layout.yaxis.title.text else "", font=dict(size=16, color='#ffffff')),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        plot_bgcolor='#212529',
        paper_bgcolor='#212529',
        separators='.',
        margin=dict(t=60, b=60, l=60, r=30)
    )
    return fig

# Update the distribution charts layout
def update_distribution_layout(fig):
    fig.update_layout(
        font=dict(family="Roboto", size=14, color='#ffffff'),
        paper_bgcolor='#212529',
        plot_bgcolor='#212529',
        separators='.',
        title_font_color='#ffffff',
        title_font_size=20,
        title_x=0.5
    )
    return fig

# Update the import share charts layout
def update_share_layout(fig):
    fig.update_layout(
        title_font_color='#ffffff',
        title_font_size=20,
        title_x=0.5,
        font=dict(family="Roboto", size=14, color='#ffffff'),
        paper_bgcolor='#212529',
        plot_bgcolor='#212529',
        separators='.',
        xaxis=dict(
            title=dict(font=dict(size=16, color='#ffffff')),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        yaxis=dict(
            title=dict(font=dict(size=16, color='#ffffff')),
            tickfont=dict(size=12, color='#ffffff'),
            gridcolor='rgba(255, 255, 255, 0.1)'
        )
    )
    return fig

# Update the treemap layout
def update_treemap_layout(fig):
    fig.update_layout(
        margin=dict(t=40, l=0, r=0, b=0),  # Top margin for pathbar
        coloraxis_showscale=False,
        title=None,  # Remove title completely
        paper_bgcolor='#212529',
        plot_bgcolor='#212529',
        separators='.',
        font=dict(family='Roboto', size=14, color='#ffffff'),
        dragmode=False,  # Disable drag interactions that can show borders
        autosize=True,   # Make sure it fills the container
        width=None,      # Let it expand to container width
        uniformtext=dict(minsize=8, mode='show'),  # Show text even in small sections
        hoverlabel=dict(
            bgcolor="rgba(26, 54, 93, 0.95)",
            font_size=16,
            font_family="Roboto",
            font_color="#ffffff",
            bordercolor="#4299e1",
            namelength=-1
        )
    )
    
    # Update the traces directly for better control
    fig.update_traces(
        marker=dict(
            line=dict(width=2, color='#1e293b'),  # Slightly thicker borders for sections
            pad=dict(t=2, r=2, b=2, l=2)  # Moderate padding to distinguish sections
        ),
        insidetextfont=dict(
            size=10,  # Smaller font size for better fit in small sections
            color='#ffffff', 
            family='Roboto Bold'
        ),
        texttemplate='<span style="text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000, 0px 0px 4px #000000;">%{label}<br>%{percentParent:.1f}%</span>',
        textposition='middle center',
        hovertemplate='<b>%{label}</b><br><b>Value:</b> %{value:.1f}%<br><b>Percentage:</b> %{percentRoot:.1f}% of total<extra></extra>',
        pathbar=dict(visible=True, side='top', thickness=20)  # Ensure pathbar is visible
    )
    
    return fig