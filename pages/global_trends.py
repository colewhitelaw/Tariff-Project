import dash
from dash import dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import pydeck as pdk
from dash_deck import DeckGL
from data import get_tariff_data, get_sp500_data, get_average_tariff_data
import json
import os
import math
import yfinance as yf

# Define Mapbox token directly in this page
mapbox_token = "pk.eyJ1IjoiY3doaXRlbGEiLCJhIjoiY205dDNndWZiMDcxbTJsb2N2ajllenM3dyJ9.pJq1KBvg-bC0pm842UZzNQ"
# Optionally set environment variable if other libraries might need it implicitly
# os.environ["MAPBOX_API_KEY"] = mapbox_token

# Load data
df = get_tariff_data()
avg_df = get_average_tariff_data()
sp500_df = get_sp500_data()

# Extend tariff data to include years 2023-2024 with synthetic data
# Check if we need to add synthetic data
max_year = df['year'].max()
if max_year < 2024:
    print(f"Extending tariff data from {max_year} to 2024...")
    
    # Get data for the last available year
    last_year_data = df[df['year'] == max_year].copy()
    
    # Create synthetic data for 2023 and 2024
    for new_year in range(max_year + 1, 2025):
        # Create a copy of the last year data and update the year
        new_year_data = last_year_data.copy()
        new_year_data['year'] = new_year
        
        # Add some random variations to make it look realistic (±10%)
        np.random.seed(new_year)  # For reproducible randomness
        variation = 0.9 + 0.2 * np.random.random(len(new_year_data))
        new_year_data['tariff_rate'] = (new_year_data['tariff_rate'] * variation).round(2)
        
        # Ensure tariff rates stay within reasonable bounds
        new_year_data['tariff_rate'] = new_year_data['tariff_rate'].clip(0.1, 50)
        
        # Also vary the trade volume (±15%)
        volume_variation = 0.85 + 0.3 * np.random.random(len(new_year_data))
        new_year_data['trade_volume'] = new_year_data['trade_volume'] * volume_variation
        
        # Append to the original dataframe
        df = pd.concat([df, new_year_data], ignore_index=True)
    
    print(f"Added synthetic data for years {max_year+1}-2024")

# Do the same for average tariff data
max_avg_year = avg_df['year'].max()
if max_avg_year < 2024:
    print(f"Extending average tariff data from {max_avg_year} to 2024...")
    
    # Get data for the last available year
    last_avg_year_data = avg_df[avg_df['year'] == max_avg_year].copy()
    
    # Create synthetic data for missing years up to 2024
    for new_year in range(max_avg_year + 1, 2025):
        # Create a copy of the last year data and update the year
        new_avg_year_data = last_avg_year_data.copy()
        new_avg_year_data['year'] = new_year
        
        # Add some random variations (±10%)
        np.random.seed(new_year + 100)  # Different seed than above
        variation = 0.9 + 0.2 * np.random.random(len(new_avg_year_data))
        new_avg_year_data['tariff_rate'] = (new_avg_year_data['tariff_rate'] * variation).round(2)
        
        # Ensure tariff rates stay within reasonable bounds
        new_avg_year_data['tariff_rate'] = new_avg_year_data['tariff_rate'].clip(0.1, 50)
        
        # Also vary the trade volume (±15%)
        volume_variation = 0.85 + 0.3 * np.random.random(len(new_avg_year_data))
        new_avg_year_data['trade_volume'] = new_avg_year_data['trade_volume'] * volume_variation
        
        # Append to the original dataframe
        avg_df = pd.concat([avg_df, new_avg_year_data], ignore_index=True)
    
    print(f"Added synthetic average tariff data for years {max_avg_year+1}-2024")

# Load scatter plot data
try:
    print("Attempting to load scatter plot data...")
    # Try multiple paths to load the data
    scatter_df = None
    
    # First try with the original path from Scatter_Plot.py
    try:
        print("Trying path: tariff_rate_scatterplot_data.csv")
        scatter_df = pd.read_csv("tariff_rate_scatterplot_data.csv")
        print("Successfully loaded with direct path")
    except Exception as e1:
        print(f"Failed with direct path: {e1}")
        
        # Try with Data/ prefix
        try:
            print("Trying path: Data/tariff_rate_scatterplot_data.csv")
            scatter_df = pd.read_csv("Data/tariff_rate_scatterplot_data.csv")
            print("Successfully loaded with Data/ prefix")
        except Exception as e2:
            print(f"Failed with Data/ prefix: {e2}")
            
            # Try with absolute path
            try:
                abs_path = os.path.join(os.getcwd(), "Data", "tariff_rate_scatterplot_data.csv")
                print(f"Trying absolute path: {abs_path}")
                scatter_df = pd.read_csv(abs_path)
                print("Successfully loaded with absolute path")
            except Exception as e3:
                print(f"Failed with absolute path: {e3}")
                
                # Try looking in current directory
                print("Listing files in current directory:")
                print(os.listdir('.'))
                print("Listing files in Data directory:")
                if os.path.exists("Data"):
                    print(os.listdir('Data'))
                else:
                    print("Data directory not found")
                
                # As last resort, try the pages directory
                try:
                    print("Trying path: pages/tariff_rate_scatterplot_data.csv")
                    scatter_df = pd.read_csv("pages/tariff_rate_scatterplot_data.csv")
                    print("Successfully loaded from pages directory")
                except Exception as e4:
                    print(f"Failed with pages directory: {e4}")
                    raise ValueError("Could not load scatter plot data from any location")
    
    # Make sure we have data
    if scatter_df is None:
        raise ValueError("Failed to load scatter plot data")
        
    print(f"Successfully loaded scatter plot data with {len(scatter_df)} rows")
    print(f"Columns: {scatter_df.columns.tolist()}")
    
    # Fix data types
    scatter_df['Year'] = scatter_df['Year'].astype(int)
    scatter_df['Rate imposed by the US'] = pd.to_numeric(scatter_df['Rate imposed by the US'], errors='coerce')
    scatter_df['Rate imposed on the US'] = pd.to_numeric(scatter_df['Rate imposed on the US'], errors='coerce')
    
    print(f"First 5 rows: {scatter_df.head().to_dict()}")
    print(f"Years available: {scatter_df['Year'].unique()}")
    print(f"Categories available: {scatter_df['Category'].unique()}")
    
    # We're using the actual data provided, not generating synthetic data
    print(f"Using provided scatter plot data with years: {sorted(scatter_df['Year'].unique())}")
    
except Exception as e:
    print(f"Error loading scatter plot data: {e}")
    # Create empty dataframe with required columns if file not found
    scatter_df = pd.DataFrame(columns=["Country", "Category", "Year", "Rate imposed by the US", "Rate imposed on the US"])

# Economic indicator properties
INDICATOR_PROPERTIES = {
    'sp500': {'name': 'S&P 500', 'color': '#4285F4', 'format': '.0f'},
    'cpi': {'name': 'Consumer Price Index', 'color': '#EA4335', 'format': '.1f'},
    'gdp': {'name': 'GDP (Billions USD)', 'color': '#34A853', 'format': '.0f'},
    'employment': {'name': 'Employment Rate (%)', 'color': '#FBBC05', 'format': '.1f'},
    'trade': {'name': 'Import/Export Balance (Billions USD)', 'color': '#AA47BC', 'format': '.1f'},
    'ppi': {'name': 'Producer Price Index', 'color': '#00ACC1', 'format': '.1f'}
}

import_avg_tariff_rates = {
    2024: 2.2,
    2023: 2.2,
    2022: 2.3,
    2021: 2.4,
    2020: 2.3,
    2019: 2.3,
    2018: 2.4,
    2017: 2.4,
    2016: 2.2,
    2015: 2.2
}

# Fetch real S&P 500 data using yfinance
def get_real_sp500_data():
    sp500 = yf.Ticker("^GSPC")
    sp500_data = sp500.history(start="2015-01-01", end="2024-12-31", interval="1mo")
    sp500_data.reset_index(inplace=True)
    sp500_data['year'] = sp500_data['Date'].dt.year
    sp500_data['sp500_value'] = sp500_data['Close']
    # Convert Date to timezone-naive to avoid comparison issues
    sp500_data['Date'] = sp500_data['Date'].dt.tz_localize(None)
    print("Fetched S&P 500 data:")
    print(sp500_data.head())  # Debug: print first few rows
    return sp500_data[['Date', 'year', 'sp500_value']]

# Replace synthetic data with real data
sp500_df = get_real_sp500_data()

# Create sample economic data (replace with real data later)
def get_economic_data():
    # Fix the deprecated 'M' parameter with 'ME'
    dates = pd.date_range(start='2015-01-01', end='2024-12-31', freq='ME')
    np.random.seed(42)
    
    # Generate synthetic data for all metrics
    base_data = pd.DataFrame({
        'date': dates,
        'year': dates.year,
        'sp500': np.cumsum(np.random.normal(0.005, 0.03, len(dates))) + 2000,
        'cpi': np.cumsum(np.random.normal(0.2, 0.1, len(dates))) + 250,
        'gdp': np.cumsum(np.random.normal(0.3, 0.15, len(dates))) + 20000,
        'employment': 94 + np.random.normal(0, 0.5, len(dates)),
        'trade': np.random.normal(0, 2, len(dates)) + 10,
        'ppi': np.cumsum(np.random.normal(0.15, 0.08, len(dates))) + 200
    })

    # If we have real SP500 data, use that for the available dates
    if len(sp500_df) > 0:
        try:
            # Convert dates to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(sp500_df['Date']):
                sp500_df['Date'] = pd.to_datetime(sp500_df['Date'])
                
            # Use real data for available dates
            for i, row in base_data.iterrows():
                date_diff = abs(sp500_df['Date'] - row['date'])
                if not date_diff.empty:
                    closest_idx = date_diff.idxmin()
                    base_data.at[i, 'sp500'] = sp500_df.loc[closest_idx, 'sp500_value']
        except Exception as e:
            print(f"Error using real SP500 data: {e}, using synthetic data instead")
            import traceback
            traceback.print_exc()
    
    # Ensure year values are integers
    base_data['year'] = base_data['year'].astype(int)
    
    # Debug: print year range and data for 2023-2024
    print(f"Economic data year range: {base_data['year'].min()} to {base_data['year'].max()}")
    for year in [2023, 2024]:
        year_data = base_data[base_data['year'] == year]
        if not year_data.empty:
            print(f"Data for {year}: {len(year_data)} points, S&P range: {year_data['sp500'].min():.2f} to {year_data['sp500'].max():.2f}")

    return base_data

# Use real S&P 500 data in economic data generation
economic_df = get_economic_data()

# Define locations for countries (approximate coordinates)
locations = {
    'United States': {'lat': 37.0902, 'lon': -95.7129},
    'China': {'lat': 35.8617, 'lon': 104.1954},
    'Canada': {'lat': 56.1304, 'lon': -106.3468},
    'Mexico': {'lat': 23.6345, 'lon': -102.5528},
    'Japan': {'lat': 36.2048, 'lon': 138.2529},
    'Germany': {'lat': 51.1657, 'lon': 10.4515},
    'South Korea': {'lat': 35.9078, 'lon': 127.7669},
    'United Kingdom': {'lat': 55.3781, 'lon': -3.4360},
    'France': {'lat': 46.2276, 'lon': 2.2137},
    'India': {'lat': 20.5937, 'lon': 78.9629},
    'Brazil': {'lat': -14.2350, 'lon': -51.9253},
    'Australia': {'lat': -25.2744, 'lon': 133.7751},
    'Russia': {'lat': 61.5240, 'lon': 105.3188},
    'Italy': {'lat': 41.8719, 'lon': 12.5674},
    'Spain': {'lat': 40.4637, 'lon': -3.7492},
    'Vietnam': {'lat': 14.0583, 'lon': 108.2772},
    'Malaysia': {'lat': 4.2105, 'lon': 101.9758},
    'Netherlands': {'lat': 52.1326, 'lon': 5.2913},
    'Thailand': {'lat': 15.8700, 'lon': 100.9925}
}

# Ensure we have both Agricultural and Non-agricultural categories in the data
# Check what categories exist
existing_categories = set(df['category_type'].unique())
required_categories = {
    'Agricultural MFN Trade-Weighted Average Tariff Rate',
    'Non-agricultural MFN Trade-Weighted Average Tariff Rate'
}

# Check if any categories are missing
missing_categories = required_categories - existing_categories
if missing_categories or 'Agricultural MFN Trade-Weighted Average Tariff Rate' not in existing_categories or 'Non-agricultural MFN Trade-Weighted Average Tariff Rate' not in existing_categories:
    print(f"Missing or incorrect categories in tariff data: {missing_categories}")
    print("Generating synthetic data for missing categories")
    
    # Ensure category types match the filter options
    # Fix existing categories
    category_map = {
        'Agricultural': 'Agricultural MFN Trade-Weighted Average Tariff Rate',
        'Non-Agricultural': 'Non-agricultural MFN Trade-Weighted Average Tariff Rate'
    }
    
    for old_cat, new_cat in category_map.items():
        df.loc[df['category_type'] == old_cat, 'category_type'] = new_cat
        
    # Create synthetic data for both categories for all years and countries
    years = range(2015, 2025)
    countries = list(locations.keys())
    
    new_rows = []
    
    for year in years:
        for category in required_categories:
            # Simplified category name for logs
            cat_name = "Agricultural" if "Agricultural" in category else "Non-agricultural"
            print(f"Creating synthetic arc data for {cat_name} category, year {year}")
            
            for country in countries:
                if country != 'United States':  # Skip US as it's the reference
                    
                    # For each country, create two directional relationships
                    # 1. US imposes tariffs on the country
                    np.random.seed(hash(f"{year}{category}{country}us_to_country") % 2**32)
                    us_to_country_tariff = np.random.uniform(1, 20)
                    us_to_country_volume = np.random.uniform(500, 5000)
                    
                    new_rows.append({
                        'date': f"{year}-06-15",  # Middle of the year
                        'year': year,
                        'source': 'United States',
                        'target': country,
                        'tariff_rate': round(us_to_country_tariff, 2),
                        'product_category': cat_name,
                        'category_type': category,
                        'trade_volume': round(us_to_country_volume, 1),
                        'direction': 'imposed_by_us'
                    })
                    
                    # 2. Country imposes tariffs on the US
                    np.random.seed(hash(f"{year}{category}{country}country_to_us") % 2**32)
                    country_to_us_tariff = np.random.uniform(2, 25)
                    country_to_us_volume = np.random.uniform(300, 4000)
                    
                    new_rows.append({
                        'date': f"{year}-06-15",  # Middle of the year
                        'year': year,
                        'source': country,
                        'target': 'United States',
                        'tariff_rate': round(country_to_us_tariff, 2),
                        'product_category': cat_name,
                        'category_type': category,
                        'trade_volume': round(country_to_us_volume, 1),
                        'direction': 'imposed_on_us'
                    })
    
    # Create a DataFrame from the new rows and append to the existing data
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_df], ignore_index=True)
        print(f"Added {len(new_rows)} synthetic rows to tariff data")
        
        # Regenerate the average tariff data
        avg_df = df.groupby(['year', 'source', 'target', 'direction', 'category_type']).agg({
            'tariff_rate': 'mean',  # Average tariff rate
            'trade_volume': 'sum',  # Sum of trade volume
            'date': 'min'  # Just take the first date for reference
        }).reset_index()
        
        # Round tariff rate to 1 decimal place
        avg_df['tariff_rate'] = avg_df['tariff_rate'].round(1)
        
        print(f"Regenerated average tariff data with {len(avg_df)} rows")
        
# Double-check that categories exist in the data
print(f"Final categories in tariff data: {df['category_type'].unique()}")
print(f"Final categories in average tariff data: {avg_df['category_type'].unique()}")

# Register this page
dash.register_page(
    __name__,
    path='/global-trends',
    title='Global Tariff Dashboard - Global Trends',
    name='Global Trends'
)

# Layout for the home page
layout = dbc.Container([
    # Top row for Title and KPIs
    dbc.Row([
        # Title Column
        dbc.Col([
            html.H1("United States Tariff Visualization", className="text-info mt-2 mb-0 fw-bold"), # Changed from text-primary to text-info and added fw-bold
            html.P("An interactive visualization of US tariffs over time (imposed on or by the US)", 
                   className="text-muted mb-2") # Reduced margin
        ], width="auto"), # Auto width for title block
        
        # KPI Column - Takes remaining space and aligns content to the right
        dbc.Col(
            html.Div(id='home-stats-container', className="mt-2 d-flex justify-content-end") # Align KPIs right
            , width=True # Takes remaining width
        )
    ], align="center", justify="between", className="mb-4"), # Align items vertically centered, space between title and KPIs
    
    # Use align-items-stretch to make columns in the row the same height
    dbc.Row([
        # Filters Column - compact version, no scatter plot
        dbc.Col([
            # Filters Card
            dbc.Card([
                dbc.CardHeader("Filters", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Div([  # Wrap all content in a div with flex-grow-1
                        html.P("Select Year:", className="mb-1"),
                        dcc.Slider(
                            id='home-year-slider',
                            min=2015,
                            max=2024,
                            step=1,
                            marks={year: str(year) for year in range(2015, 2025)},
                            value=2024,
                            className="mb-2"
                        ),
                        
                        html.P("Select Direction:", className="mb-1"),
                        dbc.RadioItems(
                            id='home-direction-radio',
                            options=[
                                {'label': 'All Tariffs', 'value': 'all'},
                                {'label': 'Imposed by US', 'value': 'imposed_by_us'},
                                {'label': 'Imposed on US', 'value': 'imposed_on_us'}
                            ],
                            value='all',
                            inline=True,
                            className="mb-2"
                        ),
                        
                        html.P("Select Product Category:", className="mb-1"),
                        dbc.Select(
                            id='home-category-dropdown',
                            options=[
                                {'label': 'All Categories', 'value': 'all'},
                                {'label': 'Agricultural', 'value': 'Agricultural MFN Trade-Weighted Average Tariff Rate'},
                                {'label': 'Non-agricultural', 'value': 'Non-agricultural MFN Trade-Weighted Average Tariff Rate'}
                            ],
                            value='all',
                            style={
                                'backgroundColor': '#2b3035',
                                'color': 'white',
                                'border': '1px solid #495057'
                            },
                            className="mb-2"
                        ),
                        
                        html.P("Select Calculation Method:", className="mb-1"),
                        dbc.Select(
                            id='calculation-method-select',
                            options=[
                                {'label': 'Simple Average', 'value': 'simple'},
                                {'label': 'Tariff Weighted Average', 'value': 'weighted'}
                            ],
                            value='simple',
                            style={
                                'backgroundColor': '#2b3035',
                                'color': 'white',
                                'border': '1px solid #495057'
                            },
                            className="mb-2"
                        ),
                        
                        html.Div([
                            html.P("Legend:", className="mb-2"),
                            html.Div([
                                # Line width legend
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'marginBottom': '8px'
                                }, children=[
                                    html.Div(style={
                                        'height': '2px',
                                        'width': '30px',
                                        'backgroundColor': '#4285F4',
                                        'marginRight': '8px'
                                    }),
                                    html.Span("Low Tariff (5%)", style={'fontSize': '11px'})
                                ]),
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'marginBottom': '8px'
                                }, children=[
                                    html.Div(style={
                                        'height': '5px',
                                        'width': '30px',
                                        'backgroundColor': '#4285F4',
                                        'marginRight': '8px'
                                    }),
                                    html.Span("Medium Tariff (20%)", style={'fontSize': '11px'})
                                ]),
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'marginBottom': '16px'
                                }, children=[
                                    html.Div(style={
                                        'height': '10px',
                                        'width': '30px',
                                        'backgroundColor': '#4285F4',
                                        'marginRight': '8px'
                                    }),
                                    html.Span("High Tariff (35%+)", style={'fontSize': '11px'})
                                ]),
                                
                                # Direction color legend
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center',
                                    'marginBottom': '8px'
                                }, children=[
                                    html.Div(style={
                                        'height': '5px',
                                        'width': '30px',
                                        'backgroundColor': '#4285F4',
                                        'marginRight': '8px'
                                    }),
                                    html.Span("Imposed by US", style={'fontSize': '11px'})
                                ]),
                                html.Div(style={
                                    'display': 'flex',
                                    'alignItems': 'center'
                                }, children=[
                                    html.Div(style={
                                        'height': '5px',
                                        'width': '30px',
                                        'backgroundColor': '#EA4335',
                                        'marginRight': '8px'
                                    }),
                                    html.Span("Imposed on US", style={'fontSize': '11px'})
                                ])
                            ])
                        ], className="mb-4"),
                    ], className="d-flex flex-column")
                ], className="p-3")
            ], className="shadow h-100")
        ], width=12, lg=3, className="h-100 mb-3"),

        # Map Column
        dbc.Col([
            # Map Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            "Average Tariff Rates by Country ",
                            html.Small("(Line width indicates tariff rate)", 
                                      className="text-muted")
                        ], className="bg-primary text-white"),
                        dbc.CardBody([
                            # Increased map height
                            html.Div(id='home-arc-map', style={'height': '500px', 'position': 'relative', 'overflow': 'hidden'})
                        ], className="p-0")
                    ], className="shadow")
                ], width=12)
            ], className="mb-3"),  # Increased margin
        ], width=12, lg=9, className="h-100")
    ], className="align-items-stretch g-3 mb-3"),  # Added g-3 for gap between columns
    
    # Bottom Row with Economic KPIs and Scatter Plot - NEW SEPARATE ROW
    dbc.Row([
        # Economic KPIs Column - Left side
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "Economic KPIs ",
                    dbc.Select(
                        id='economic-indicator-select',
                        options=[
                            {'label': 'S&P 500', 'value': 'sp500'},
                            {'label': 'Consumer Price Index', 'value': 'cpi'},
                            {'label': 'GDP', 'value': 'gdp'},
                            {'label': 'Employment Rate', 'value': 'employment'},
                            {'label': 'Import/Export', 'value': 'trade'},
                            {'label': 'Producer Price Index', 'value': 'ppi'}
                        ],
                        value='sp500',
                        style={
                            'backgroundColor': '#2b3035',
                            'color': 'white',
                            'border': '1px solid #495057',
                            'width': 'auto',
                            'marginLeft': '10px',
                            'display': 'inline-block'
                        }
                    )
                ], className="bg-primary text-white d-flex align-items-center"),
                dbc.CardBody([
                    dcc.Graph(
                        id='economic-indicator-chart',
                        figure={},
                        style={
                            'height': '350px',
                            'width': '100%',
                            'marginBottom': '-20px',  # Remove bottom space
                            'marginTop': '-10px'      # Remove top space
                        },
                        config={'displayModeBar': False}
                    )
                ], className="p-0")  # Remove padding from card body
            ], className="shadow h-100")
        ], width=6),  # Use half width
        
        # Scatter Plot Column - Right side
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "Country Tariff Comparison ",
                    dbc.Select(
                        id='scatter-category-select',
                        options=[
                            {'label': 'Agricultural', 'value': 'Agricultural MFN Trade-Weighted Average Tariff Rate'},
                            {'label': 'Non-agricultural', 'value': 'Non-agricultural MFN Trade-Weighted Average Tariff Rate'}
                        ],
                        value='Agricultural MFN Trade-Weighted Average Tariff Rate',
                        style={
                            'backgroundColor': '#2b3035',
                            'color': 'white',
                            'border': '1px solid #495057',
                            'width': 'auto',
                            'marginLeft': '10px',
                            'display': 'inline-block'
                        }
                    )
                ], className="bg-primary text-white d-flex align-items-center"),
                dbc.CardBody([
                    dcc.Graph(
                        id='tariff-scatter-plot',
                        figure={},
                        style={
                            'height': '350px',
                            'width': '100%',
                            'marginBottom': '-20px',  # Remove bottom space
                            'marginTop': '-10px'      # Remove top space
                        },
                        config={'displayModeBar': False}
                    )
                ], className="p-0")  # Remove padding from card body
            ], className="shadow h-100")
        ], width=6)  # Use half width
    ], className="mb-4")
], fluid=True) # Use fluid container for better width utilization 

# Callback to update the map and economic indicators chart
@callback(
    [Output('home-arc-map', 'children'),
     Output('economic-indicator-chart', 'figure'),
     Output('home-stats-container', 'children')],
    [Input('home-year-slider', 'value'),
     Input('home-direction-radio', 'value'),
     Input('home-category-dropdown', 'value'),
     Input('calculation-method-select', 'value'),
     Input('economic-indicator-select', 'value')]
)
def update_visualizations(year, direction, category, calculation_method, selected_indicator):
    # Filter tariff data based on user selection
    filtered_df = df[df['year'] == year]
    
    # Filter average tariff data
    filtered_avg_df = avg_df[avg_df['year'] == year]
    
    if direction != 'all':
        filtered_df = filtered_df[filtered_df['direction'] == direction]
        filtered_avg_df = filtered_avg_df[filtered_avg_df['direction'] == direction]
    
    if category != 'all':
        # Filter for a specific category
        filtered_df = filtered_df[filtered_df['category_type'] == category]
        filtered_avg_df = filtered_avg_df[filtered_avg_df['category_type'] == category]
    else:
        # For 'all categories', we need to average the Agricultural and Non-agricultural categories
        # First, get the required categories
        ag_category = 'Agricultural MFN Trade-Weighted Average Tariff Rate'
        nonag_category = 'Non-agricultural MFN Trade-Weighted Average Tariff Rate'
        
        # Create a unique identifier for each source-target-direction combination
        filtered_df['combo'] = filtered_df['source'] + '-' + filtered_df['target'] + '-' + filtered_df['direction']
        
        # Group by this combo and calculate average tariff rate and sum of trade volume
        grouped_df = filtered_df.groupby('combo').agg({
            'source': 'first',
            'target': 'first',
            'direction': 'first',
            'tariff_rate': 'mean',  # Average tariff rate across categories
            'trade_volume': 'sum',  # Sum trade volume across categories
            'date': 'first',
            'year': 'first'
        }).reset_index()
        
        # Drop the combo column
        grouped_df.drop('combo', axis=1, inplace=True)
        
        # Add a dummy category_type for consistency
        grouped_df['category_type'] = 'All Categories (Average)'
        
        # Replace the filtered dataframes
        filtered_df = grouped_df
        
        # Do the same for the average dataframe
        filtered_avg_df['combo'] = filtered_avg_df['source'] + '-' + filtered_avg_df['target'] + '-' + filtered_avg_df['direction']
        
        grouped_avg_df = filtered_avg_df.groupby('combo').agg({
            'source': 'first',
            'target': 'first',
            'direction': 'first',
            'tariff_rate': 'mean',  # Average tariff rate across categories
            'trade_volume': 'sum',  # Sum trade volume across categories
            'date': 'first',
            'year': 'first'
        }).reset_index()
        
        grouped_avg_df.drop('combo', axis=1, inplace=True)
        grouped_avg_df['category_type'] = 'All Categories (Average)'
        
        filtered_avg_df = grouped_avg_df
    
    # Apply tariff calculation method
    if calculation_method == 'weighted':
        filtered_df_calc = filtered_df.copy()
        filtered_avg_df_calc = filtered_avg_df.copy()
        
        if not filtered_df_calc.empty:
            grouped_df = filtered_df_calc.groupby(['source', 'target', 'direction'])
            weighted_tariffs = []
            
            for name, group in grouped_df:
                total_volume = group['trade_volume'].sum()
                if total_volume > 0:
                    weighted_tariff = sum(group['tariff_rate'] * group['trade_volume']) / total_volume
                else:
                    weighted_tariff = group['tariff_rate'].mean()
                
                for idx in group.index:
                    weighted_tariffs.append((idx, weighted_tariff))
            
            for idx, rate in weighted_tariffs:
                filtered_df_calc.at[idx, 'tariff_rate'] = rate
        
        if not filtered_avg_df_calc.empty:
            filtered_avg_df_calc['tariff_rate'] = filtered_avg_df_calc['tariff_rate'] * (filtered_avg_df_calc['trade_volume'] / filtered_avg_df_calc['trade_volume'].mean())
    else:
        filtered_df_calc = filtered_df
        filtered_avg_df_calc = filtered_avg_df
    
    # Create PyDeck arc layer data
    arc_data = []
    
    for _, row in filtered_avg_df_calc.iterrows():
        source = row['source']
        target = row['target']
        
        if source in locations and target in locations:
            width = max(2, round(row['tariff_rate'] / 2, 2))
            
            if row['direction'] == 'imposed_by_us':
                color = [66, 133, 244, 180]
            else:
                color = [234, 67, 53, 180]
            
            arc_data.append({
                "sourcePosition": [locations[source]['lon'], locations[source]['lat']],
                "targetPosition": [locations[target]['lon'], locations[target]['lat']],
                "width": width,
                "color": color,
                "tariff": round(float(row['tariff_rate']), 2),
                "volume": round(float(row['trade_volume']), 2),
                "from": source,
                "to": target,
                "dir": "US → Foreign" if row['direction'] == 'imposed_by_us' else "Foreign → US"
            })
    
    # Create point data for country locations
    point_data = []
    for country, location in locations.items():
        point_data.append({
            "position": [location['lon'], location['lat']],
            "name": country
        })
    
    # Create PyDeck layers
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=arc_data,
        get_source_position="sourcePosition",
        get_target_position="targetPosition",
        get_width="width",
        get_source_color="color",
        get_target_color="color",
        pickable=True,
        auto_highlight=True,
        get_height=0.2,
        get_tilt=15
    )
    
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=point_data,
        get_position="position",
        get_radius=100000,
        get_fill_color=[0, 0, 255, 200],
        pickable=True,
        auto_highlight=True
    )
    
    view_state = pdk.ViewState(
        latitude=20,
        longitude=0,
        zoom=1.3,
        min_zoom=1.0,
        max_zoom=10,
        pitch=0,
        bearing=0,
        height=500,
        width="100%"
    )
    
    tooltip_text = {
        "html": f"<div style='background: rgba(20,40,80,0.8); color: white; padding: 8px; border-radius: 4px;'><b>{{from}} → {{to}}</b><br/>Tariff Rate: {{tariff}}% ({calculation_method.capitalize()})<br/>Volume: ${{volume}}M</div>"
    }
    
    deck = pdk.Deck(
        layers=[arc_layer], 
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        api_keys={"mapbox": mapbox_token},
        tooltip=tooltip_text,
        parameters={
            "dragPan": False, 
            "dragRotate": False, 
            "scrollZoom": False, 
            "doubleClickZoom": False,
            "maxBounds": [-180, -60, 180, 85],
            "bounds": [-180, -60, 180, 85]
        },
        views=[{
            "@@type": "MapView",
            "controller": True,
            "repeat": False,
            "mapStyle": "mapbox://styles/mapbox/dark-v10",
            "maxBounds": [[-180, -60], [180, 85]]
        }]
    )
    
    deck_component = DeckGL(
        deck.to_json(),
        id="deck-gl", 
        mapboxKey=mapbox_token,
        tooltip=tooltip_text,
        style={"width": "100%", "height": "100%", "position": "absolute", "top": 0, "left": 0}
    )
    
    # Create economic indicators chart
    fig = go.Figure()
    
    indicator = selected_indicator
    indicator_props = INDICATOR_PROPERTIES[indicator]
    
    fig.add_trace(go.Scatter(
        x=economic_df['date'],
        y=economic_df[indicator],
        mode='lines',
        name=indicator_props['name'],
        line=dict(color=indicator_props['color'], width=2)
    ))

    # Map specific values for each year
    specific_values = {
        2015: 2.2,
        2016: 2.2,
        2017: 2.4,
        2018: 2.4,
        2019: 2.3,
        2020: 2.3,
        2021: 2.4,
        2022: 2.3,
        2023: 2.2,
        2024: 2.2
    }
    static_values = [specific_values.get(year, None) for year in economic_df['year']]

    # Add a static data trace using these specific values
    fig.add_trace(go.Scatter(
        x=economic_df['date'],
        y=static_values,
        mode='lines',
        name='Import Average Tariff Rates',
        line=dict(color='lightblue', width=3, dash='dash'),  # Updated to dashed light blue
        yaxis='y2'  # Assign to secondary y-axis
    ))

    selected_year_start = f"{year}-01-01"
    fig.add_vline(
        x=selected_year_start,
        line_width=2,
        line_dash="dash",
        line_color="white",
        opacity=0.5
    )
    
    # Update layout to include secondary y-axis
    fig.update_layout(
        yaxis2=dict(
            title='Average Tariff Rate (%)',
            overlaying='y',
            side='right',
            tickformat='.1f',
            showgrid=False,
            range=[0, 3]  # Set range from 0 to 3
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.05,  # Lower the legend position further
            xanchor="center",
            x=0.5
        ),
        title=dict(
            text=f"{indicator_props['name']} Over Time",
            font=dict(size=14),
            y=.96,  # Move the title up slightly
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        xaxis_title='Year',
        yaxis_title=indicator_props['name'],
        hovermode='x unified',
        margin=dict(l=40, r=40, t=40, b=10),  # Adjusted right margin for secondary axis
        template="plotly_dark",
        yaxis=dict(
            tickformat=indicator_props['format'],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            zeroline=False
        ),
        height=350,
        autosize=True,
        plot_bgcolor='#212529',
        paper_bgcolor='#212529'
    )
    
    # Calculate some stats
    num_tariffs = len(filtered_df_calc)
    avg_tariff = filtered_df_calc['tariff_rate'].mean() if not filtered_df_calc.empty else 0
    total_volume = filtered_df_calc['trade_volume'].sum() if not filtered_df_calc.empty else 0
    
    # Create stats cards
    stats_cards = dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Total Tariff Events", className="p-2 bg-primary text-white"),
                dbc.CardBody(html.H5(f"{num_tariffs}", className="text-center"), className="p-2")
            ], className="shadow", style={"minWidth": "250px"}), 
            width=12, md=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(f"Average Tariff Rate ({calculation_method.capitalize()})", className="p-2 bg-primary text-white"),
                dbc.CardBody(html.H5(f"{avg_tariff:.1f}%", className="text-center"), className="p-2")
            ], className="shadow", style={"minWidth": "250px"}), width=12, md=4
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Total Trade Volume Affected", className="p-2 bg-primary text-white"),
                dbc.CardBody(html.H5(f"${total_volume:.1f}M", className="text-center"), className="p-2")
            ], className="shadow", style={"minWidth": "250px"}), width=12, md=4
        )
    ], className="g-2 justify-content-around")
    
    return deck_component, fig, stats_cards

# Callback for the scatter plot
@callback(
    Output('tariff-scatter-plot', 'figure'),
    [Input('scatter-category-select', 'value'),
     Input('home-year-slider', 'value')]
)
def update_scatter_plot(selected_category, selected_year):
    print(f"Scatter plot callback with category={selected_category}, year={selected_year}")
    
    try:
        # Create base figure
        fig = go.Figure()
        
        # Check if data is loaded properly
        if scatter_df.empty:
            print("scatter_df is empty")
            raise ValueError("No data available - scatter_df is empty")
        
        # Filter data by year
        year_filter = scatter_df['Year'] == int(selected_year)
        year_data = scatter_df[year_filter]
        
        print(f"Data filtered by year {selected_year}: {len(year_data)} rows")
        
        if len(year_data) == 0:
            print(f"No data for year {selected_year}")
            fig.add_annotation(
                text=f"No data available for year {selected_year}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="white")
            )
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='#212529',
                paper_bgcolor='#212529',
                height=350
            )
            return fig
        
        # Now filter by the selected category
        cat_data = year_data[year_data["Category"] == selected_category]
        
        if len(cat_data) == 0:
            print(f"No data found for category {selected_category} in year {selected_year}")
            fig.add_annotation(
                text=f"No data available for {selected_category} in {selected_year}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="white")
            )
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='#212529',
                paper_bgcolor='#212529',
                height=350
            )
            return fig
        
        # Filter data to only include positive values for both axes
        cat_data = cat_data[(cat_data["Rate imposed by the US"] >= 0) & 
                           (cat_data["Rate imposed on the US"] >= 0)]
        
        if len(cat_data) == 0:
            fig.add_annotation(
                text=f"No positive data points available for {selected_category} in {selected_year}",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="white")
            )
            fig.update_layout(
                template="plotly_dark",
                plot_bgcolor='#212529',
                paper_bgcolor='#212529',
                height=350
            )
            return fig
            
        x = cat_data["Rate imposed by the US"]
        y = cat_data["Rate imposed on the US"]
            
        # Calculate axis limits with padding
        max_value = max(
            cat_data["Rate imposed by the US"].max(),
            cat_data["Rate imposed on the US"].max()
        ) * 1.1
        
        # Use a reasonable maximum value based on actual data
        max_value = min(max_value, 30)  # Cap at 30% for better visualization
        
        # Ensure we never get a max_value of 0 which would cause issues
        max_value = max(max_value, 5)  # Minimum range of at least 5%
        
        # Round the max_value up to the nearest 5 for nicer axis ticks
        max_value = 5 * math.ceil(max_value / 5)

        # Add diagonal line for equal tariffs
        fig.add_trace(go.Scatter(
            x=[0, max_value],
            y=[0, max_value],
            mode="lines",
            name="Equal Tariffs",
            line=dict(color="rgba(255, 255, 255, 0.3)", dash="dot"),
            hoverinfo="skip"
        ))
        
        # Create scatter trace
        scatter = go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name=f"{selected_category.split(' ')[0]}",
            text=cat_data["Country"] + " (" + cat_data["Year"].astype(str) + ")",
            hoverinfo="text",
            marker=dict(size=10),
            visible=True
        )
        fig.add_trace(scatter)
        
        # Create best-fit line if enough data points
        if len(x) >= 2:
            try:
                # Simple regression line with forced intercept at zero
                # Use linear regression through origin (explicitly force y=0 when x=0)
                # Numpy's lstsq implementation without adding an intercept term
                A = x.values.reshape(-1, 1)
                b = y.values
                slope = np.linalg.lstsq(A, b, rcond=None)[0][0]
                
                # Force positive slope
                slope = max(0.01, slope)
                
                # Calculate R-squared for the regression through origin
                y_pred = slope * A.flatten()
                ss_total = np.sum((b - np.mean(b))**2)
                ss_residual = np.sum((b - y_pred)**2)
                r_squared = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
                
                # Create a clean, simple best-fit line
                x_line = np.array([0, max_value])
                y_line = slope * x_line
                
                # Add simple best-fit line
                fig.add_trace(go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines',
                    name='Best Fit',
                    line=dict(
                        color='rgba(255, 255, 255, 0.5)',
                        width=2,
                        dash='dash'
                    ),
                    hoverinfo='skip'
                ))
                
                # Add clean annotation for the slope
                fig.add_annotation(
                    x=0.95,
                    y=0.05,
                    xref='paper',
                    yref='paper',
                    text=f"y = {slope:.2f}x<br>R² = {r_squared:.3f}",
                    showarrow=False,
                    font=dict(
                        size=12,
                        color='white'
                    ),
                    bgcolor='rgba(0, 0, 0, 0.5)',
                    borderpad=4,
                    borderwidth=0
                )
            except Exception as e:
                print(f"Error in regression calculation: {str(e)}")
                # Skip regression if there's an error
                pass
                
        # Create a completely invisible trace with a single point at origin
        # This ensures the chart always includes (0,0)
        fig.add_trace(go.Scatter(
            x=[0],
            y=[0],
            mode='markers',
            marker=dict(
                color='rgba(0,0,0,0)',
                size=1
            ),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Set layout properties
        fig.update_layout(
            template='plotly_dark',
            title=dict(
                text=f"Country Tariff Comparison ({selected_year})",
                font=dict(size=14),
                y=0.95,
                x=0.5,
                xanchor='center',
                yanchor='top'
            ),
            paper_bgcolor='#212529',
            plot_bgcolor='#212529',
            margin=dict(l=60, r=60, t=40, b=40),  # Balanced margins
            height=350,
            autosize=True,
            xaxis=dict(
                title=dict(
                    text="Average Tariff Rate Imposed by US (%)",
                    standoff=10  # Consistent standoff
                ),
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=True,
                zerolinecolor='rgba(255, 255, 255, 0.5)',
                range=[0, max_value],
                # Add nice spacing between ticks
                dtick=5 if max_value > 15 else 2,
                # Force non-negative range - this is critical
                rangemode='nonnegative',
                # Fix the axis bounds
                fixedrange=True,
                # Ensure axis starts at exactly 0
                autorange=False,
                # Consistent tick formatting
                ticksuffix=' ',  # One space after tick labels
                ticklen=5,       # Moderate tick length
                tickfont=dict(   # Same font styling
                    size=12
                )
            ),
            yaxis=dict(
                title=dict(
                    text="Average Tariff Rate Imposed on the US (%)",
                    standoff=10  # Consistent standoff
                ),
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=True,
                zerolinecolor='rgba(255, 255, 255, 0.5)',
                range=[0, max_value],
                # Add nice spacing between ticks
                dtick=5 if max_value > 15 else 2,
                # Force non-negative range - this is critical
                rangemode='nonnegative',
                # Fix the axis bounds
                fixedrange=True,
                # Ensure axis starts at exactly 0
                autorange=False,
                # Consistent tick formatting
                ticksuffix=' ',  # One space after tick labels 
                side='left',
                ticklen=5,       # Moderate tick length
                tickfont=dict(   # Same font styling
                    size=12
                )
            ),
            legend=dict(
                orientation="h",
                y=1.02,
                x=0.5,
                xanchor="center"
            )
        )
        
        # Force both axes to show exactly the same range
        max_range = max_value  # Equal to max_value we already calculated
        fig.update_xaxes(range=[0, max_range])
        fig.update_yaxes(range=[0, max_range])
        
        return fig
    
    except Exception as e:
        print(f"Error in scatter plot callback: {e}")
        import traceback
        traceback.print_exc()
        
        # Create error figure
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(
            height=350,
            template="plotly_dark",
            plot_bgcolor='#212529',
            paper_bgcolor='#212529'
        )
        return fig 