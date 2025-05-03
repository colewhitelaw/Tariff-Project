import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

# Register this page
dash.register_page(
    __name__,
    path='/state-analysis',
    title='State Trade Analysis',
    name='State Analysis'
)

# Generate synthetic data for state trade volumes
def generate_state_trade_data():
    # Dictionary of US states with their abbreviations
    states = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
        'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
        'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
        'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    
    # Generate data for years 2015-2022
    years = range(2015, 2023)
    data = []
    
    # Create a base distribution of trade volumes
    base_volumes = {}
    for state in states:
        # Generate a base volume between 1000 and 10000
        base_volumes[state] = np.random.uniform(1000, 10000)
    
    for year in years:
        for state, abbr in states.items():
            # Get the base volume for this state
            base_volume = base_volumes[state]
            
            # Add year-over-year growth (5% per year)
            growth_factor = 1 + (year - 2015) * 0.05
            
            # Add some random variation
            variation = np.random.normal(1, 0.1)
            
            # Calculate total volume
            total_volume = base_volume * growth_factor * variation
            
            # Split into imports and exports (roughly 60-40 split on average)
            import_ratio = np.random.normal(0.6, 0.1)
            import_volume = total_volume * import_ratio
            export_volume = total_volume * (1 - import_ratio)
            
            # Split total volume into agricultural and non-agricultural
            agri_ratio = np.random.normal(0.35, 0.1)  # 35% agricultural on average
            agri_volume = total_volume * agri_ratio
            non_agri_volume = total_volume * (1 - agri_ratio)
            
            data.append({
                'State': state,
                'State_Abbr': abbr,
                'Year': year,
                'Total_Volume': round(total_volume, 2),
                'Import_Volume': round(import_volume, 2),
                'Export_Volume': round(export_volume, 2),
                'Agricultural_Volume': round(agri_volume, 2),
                'Non_Agricultural_Volume': round(non_agri_volume, 2)
            })
    
    return pd.DataFrame(data)

# Create the layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("State Trade Analysis", className="text-info mt-2 mb-0 fw-bold"),
            html.P("Explore how tariffs have affected trade volumes across US states", 
                  className="text-muted mb-4")
        ])
    ]),
    
    # Filters Row with all filters
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters", className="bg-primary text-white"),
                dbc.CardBody([
                    dbc.Row([
                        # Year Filter (affects both maps)
                        dbc.Col([
                            html.P("Select Year:", className="mb-2"),
                            dcc.Slider(
                                id='year-slider',
                                min=2015,
                                max=2022,
                                step=1,
                                marks={year: str(year) for year in range(2015, 2023)},
                                value=2022,
                                className="mb-4"
                            )
                        ], width=12),
                        
                        # Trade Volume Filter (affects both maps)
                        dbc.Col([
                            html.P("Select Trade Metric (both maps):", className="mb-2"),
                            dbc.Select(
                                id='trade-metric-select',
                                options=[
                                    {'label': 'Total Volume', 'value': 'Total_Volume'},
                                    {'label': 'Import Volume', 'value': 'Import_Volume'},
                                    {'label': 'Export Volume', 'value': 'Export_Volume'}
                                ],
                                value='Total_Volume',
                                style={
                                    'backgroundColor': '#2b3035',
                                    'color': 'white',
                                    'border': '1px solid #495057'
                                },
                                className="mb-4"
                            )
                        ], md=6),
                        
                        # Agricultural Filter (affects only right map)
                        dbc.Col([
                            html.P("Select Product Category (right map only):", className="mb-2"),
                            dbc.RadioItems(
                                id='product-category-radio',
                                options=[
                                    {'label': 'Agricultural', 'value': 'Agricultural_Volume'},
                                    {'label': 'Non-Agricultural', 'value': 'Non_Agricultural_Volume'}
                                ],
                                value='Agricultural_Volume',
                                inline=True,
                                className="mb-4"
                            )
                        ], md=6)
                    ])
                ])
            ], className="shadow")
        ], width=12)
    ], className="mb-4"),
    
    # Maps Row - No filters in the cards
    dbc.Row([
        # LEFT MAP COLUMN
        dbc.Col([
            # Left Map
            dbc.Card([
                dbc.CardHeader("Trade Volume by State", className="bg-primary text-white"),
                dbc.CardBody([
                    dcc.Graph(id='state-choropleth')
                ], className="p-0")
            ], className="shadow mb-3"),
            
            # Left Map Stats
            dbc.Card([
                dbc.CardHeader("Top 5 States by Trade Volume", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(id='top-states-list')
                ])
            ], className="shadow")
        ], width=12, lg=6),
        
        # RIGHT MAP COLUMN
        dbc.Col([
            # Right Map
            dbc.Card([
                dbc.CardHeader("Product Category Breakdown", className="bg-primary text-white"),
                dbc.CardBody([
                    dcc.Graph(id='product-category-choropleth')
                ], className="p-0")
            ], className="shadow mb-3"),
            
            # Right Map Stats
            dbc.Card([
                dbc.CardHeader("Product Category Stats", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div(id='category-breakdown')
                ])
            ], className="shadow")
        ], width=12, lg=6)
    ], className="mb-4")
], fluid=True)

# Callback for the left map - responds to year-slider and trade-metric-select
@callback(
    [Output('state-choropleth', 'figure'),
     Output('top-states-list', 'children')],
    [Input('year-slider', 'value'),
     Input('trade-metric-select', 'value')]
)
def update_left_map(year, metric):
    # Get the data
    df = generate_state_trade_data()
    year_df = df[df['Year'] == year]
    
    # Create main choropleth map (left) - shows volume based on selected metric
    fig = px.choropleth(
        year_df,
        locations='State_Abbr',
        locationmode='USA-states',
        color=metric,
        scope='usa',
        color_continuous_scale='Viridis',
        title=f'State {metric.replace("_", " ")} - {year}',
        labels={metric: 'Trade Volume (Millions USD)'},
        hover_data={
            'State': True,
            'State_Abbr': False,
            metric: ':.0f'
        }
    )
    
    # Update layout for main map
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#212529',
        plot_bgcolor='#212529',
        font=dict(color='white'),
        geo=dict(
            bgcolor='#212529',
            lakecolor='#212529',
            landcolor='#343a40',
            subunitcolor='white',
            subunitwidth=0.5,
            showlakes=True,
            showland=True,
            showcountries=True,
            countrycolor='white',
            countrywidth=0.5
        ),
        coloraxis_colorbar=dict(
            title='Trade Volume (Millions USD)',
            tickformat=',.0f'
        )
    )
    
    # Update traces for main map
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color='white'
    )
    
    # Get the metric title for display
    metric_title = metric.replace('_', ' ')
    
    # Calculate total volume for context
    total_national_volume = year_df[metric].sum()
    
    # Get top 5 states
    top_states = year_df.nlargest(5, metric)
    
    # Create top states list matching the image style
    top_states_list = html.Div([
        # Dark background for the summary
        html.Div(
            style={
                'backgroundColor': '#212529',
                'padding': '20px 15px',
                'marginBottom': '20px'
            },
            children=[
                html.H6(f"National {metric_title.split('_')[0]} Summary", 
                        className="text-center text-white mb-3"),
                html.H3(f"${total_national_volume:,.0f}M", 
                        className="text-center text-primary mb-2"),
                html.P(f"Total US {metric_title.lower()}", 
                       className="text-center text-muted")
            ]
        ),
        
        # Top 5 States section
        html.H5(f"Top 5 States by {metric_title}", 
                className="text-white mb-3"),
        
        # State list
        html.Div(
            style={
                'backgroundColor': '#212529'
            },
            children=[
                # State 1
                html.Div([
                    html.Div([
                        html.Span(f"1. {top_states.iloc[0]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"${top_states.iloc[0][metric]:,.0f}M", 
                                 className="text-primary"),
                        html.Span(f" ({(top_states.iloc[0][metric]/total_national_volume*100):.1f}% of US total)", 
                                 className="text-muted small")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 2
                html.Div([
                    html.Div([
                        html.Span(f"2. {top_states.iloc[1]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"${top_states.iloc[1][metric]:,.0f}M", 
                                 className="text-primary"),
                        html.Span(f" ({(top_states.iloc[1][metric]/total_national_volume*100):.1f}% of US total)", 
                                 className="text-muted small")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 3
                html.Div([
                    html.Div([
                        html.Span(f"3. {top_states.iloc[2]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"${top_states.iloc[2][metric]:,.0f}M", 
                                 className="text-primary"),
                        html.Span(f" ({(top_states.iloc[2][metric]/total_national_volume*100):.1f}% of US total)", 
                                 className="text-muted small")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 4
                html.Div([
                    html.Div([
                        html.Span(f"4. {top_states.iloc[3]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"${top_states.iloc[3][metric]:,.0f}M", 
                                 className="text-primary"),
                        html.Span(f" ({(top_states.iloc[3][metric]/total_national_volume*100):.1f}% of US total)", 
                                 className="text-muted small")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 5
                html.Div([
                    html.Div([
                        html.Span(f"5. {top_states.iloc[4]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"${top_states.iloc[4][metric]:,.0f}M", 
                                 className="text-primary"),
                        html.Span(f" ({(top_states.iloc[4][metric]/total_national_volume*100):.1f}% of US total)", 
                                 className="text-muted small")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'})
            ]
        )
    ])
    
    return fig, top_states_list

# Callback for the right map - responds to year-slider, trade-metric-select, and product-category-radio
@callback(
    [Output('product-category-choropleth', 'figure'),
     Output('category-breakdown', 'children')],
    [Input('year-slider', 'value'),
     Input('trade-metric-select', 'value'),
     Input('product-category-radio', 'value')]
)
def update_right_map(year, trade_metric, product_category):
    # Get the data
    df = generate_state_trade_data()
    year_df = df[df['Year'] == year]
    
    # Get the titles based on selected metrics
    trade_title = trade_metric.replace('_', ' ')
    product_title = product_category.replace('_', ' ').replace(' Volume', '')
    
    # Calculate percentage of the selected trade metric
    year_df['Category_Percentage'] = (year_df[product_category] / year_df[trade_metric]) * 100
    
    # Create product category choropleth map (right)
    category_fig = px.choropleth(
        year_df,
        locations='State_Abbr',
        locationmode='USA-states',
        color='Category_Percentage',  # Color represents percentage rather than absolute value
        scope='usa',
        color_continuous_scale='RdBu',  # Red to Blue scale for percentage
        range_color=[0, 100],  # Set range for percentage (0-100%)
        title=f'{product_title} as % of {trade_title} - {year}',
        labels={
            'Category_Percentage': '% of Trade',
            product_category: f'{product_title} (Millions USD)',
            trade_metric: f'{trade_title} (Millions USD)'
        },
        hover_data={
            'State': True,
            'State_Abbr': False,
            product_category: ':.0f',
            trade_metric: ':.0f',
            'Category_Percentage': ':.1f'
        }
    )
    
    # Update layout for category map
    category_fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='#212529',
        plot_bgcolor='#212529',
        font=dict(color='white'),
        geo=dict(
            bgcolor='#212529',
            lakecolor='#212529',
            landcolor='#343a40',
            subunitcolor='white',
            subunitwidth=0.5,
            showlakes=True,
            showland=True,
            showcountries=True,
            countrycolor='white',
            countrywidth=0.5
        ),
        coloraxis_colorbar=dict(
            title='Percentage (%)',
            ticksuffix='%'
        )
    )
    
    # Update traces for category map
    category_fig.update_traces(
        marker_line_width=0.5,
        marker_line_color='white'
    )
    
    # Get top 5 states by percentage
    top_states_by_percentage = year_df.sort_values('Category_Percentage', ascending=False).head(5)
    
    # Calculate totals for display
    total_product_volume = year_df[product_category].sum()
    total_trade_volume = year_df[trade_metric].sum()
    overall_percentage = (total_product_volume / total_trade_volume) * 100
    
    # Create breakdown matching the style in the image
    category_breakdown = html.Div([
        # Dark background for the summary
        html.Div(
            style={
                'backgroundColor': '#212529',
                'padding': '20px 15px',
                'marginBottom': '20px'
            },
            children=[
                html.H6(f"National {product_title} Summary", 
                        className="text-center text-white mb-3"),
                html.H3(f"${total_product_volume:,.0f}M", 
                        className="text-center text-primary mb-2"),
                html.P(f"Total {product_title.lower()} volume", 
                       className="text-center text-muted mb-2"),
                html.P(f"{overall_percentage:.1f}% of total volume", 
                       className="text-center text-white mb-2"),
                # Progress bar
                html.Div(
                    className="progress mx-auto", 
                    style={"height": "10px", "maxWidth": "80%", "backgroundColor": "#343a40"},
                    children=[
                        html.Div(
                            className="progress-bar bg-primary", 
                            style={"width": f"{min(overall_percentage, 100)}%"}
                        )
                    ]
                )
            ]
        ),
        
        # Top 5 States section
        html.H5(f"Top 5 States by {product_title} Percentage", 
                className="text-white mb-3"),
        
        # State list
        html.Div(
            style={
                'backgroundColor': '#212529'
            },
            children=[
                # State 1
                html.Div([
                    html.Div([
                        html.Span(f"1. {top_states_by_percentage.iloc[0]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"{top_states_by_percentage.iloc[0]['Category_Percentage']:.1f}%", 
                                 className="text-primary")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 2
                html.Div([
                    html.Div([
                        html.Span(f"2. {top_states_by_percentage.iloc[1]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"{top_states_by_percentage.iloc[1]['Category_Percentage']:.1f}%", 
                                 className="text-primary")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 3
                html.Div([
                    html.Div([
                        html.Span(f"3. {top_states_by_percentage.iloc[2]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"{top_states_by_percentage.iloc[2]['Category_Percentage']:.1f}%", 
                                 className="text-primary")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 4
                html.Div([
                    html.Div([
                        html.Span(f"4. {top_states_by_percentage.iloc[3]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"{top_states_by_percentage.iloc[3]['Category_Percentage']:.1f}%", 
                                 className="text-primary")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'}),
                
                # State 5
                html.Div([
                    html.Div([
                        html.Span(f"5. {top_states_by_percentage.iloc[4]['State']}", 
                                 className="text-white")
                    ], style={'flex': '1'}),
                    html.Div([
                        html.Span(f"{top_states_by_percentage.iloc[4]['Category_Percentage']:.1f}%", 
                                 className="text-primary")
                    ], style={'textAlign': 'right'})
                ], className="d-flex justify-content-between py-2",
                    style={'borderBottom': '1px solid #343a40'})
            ]
        )
    ])
    
    return category_fig, category_breakdown 