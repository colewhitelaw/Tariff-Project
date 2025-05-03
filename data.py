import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate synthetic tariff data
def generate_tariff_data():
    # Countries to include in the data
    countries = [
        'China', 'Canada', 'Mexico', 'Japan', 'Germany', 
        'South Korea', 'United Kingdom', 'France', 'India', 
        'Brazil', 'Australia', 'Russia', 'Italy', 'Spain', 
        'Vietnam', 'Malaysia', 'Netherlands', 'Thailand'
    ]
    
    # Start date for the data
    start_date = datetime(2015, 1, 1)
    
    # Create random tariff relationships
    data = []
    
    for year in range(2015, 2023):
        # Generate varying number of tariff events per year
        num_events = np.random.randint(10, 30)
        
        for _ in range(num_events):
            country = np.random.choice(countries)
            
            # Randomly choose direction (US imposing on country or country imposing on US)
            direction = np.random.choice(['imposed_by_us', 'imposed_on_us'])
            
            if direction == 'imposed_by_us':
                source = 'United States'
                target = country
            else:
                source = country
                target = 'United States'
            
            # Generate random date within the year
            event_date = start_date + timedelta(days=np.random.randint(0, 365))
            event_date = event_date.replace(year=year)
            
            # Random product category
            # Assign more specific product categories with agricultural or non-agricultural classification
            ag_categories = ['Agriculture', 'Food Products', 'Livestock', 'Dairy']
            non_ag_categories = ['Electronics', 'Automotive', 'Steel', 'Aluminum', 'Textiles', 
                                'Chemicals', 'Machinery', 'Consumer Goods', 'Energy']
            
            # Choose between agricultural and non-agricultural categories
            is_agricultural = np.random.choice([True, False])
            
            if is_agricultural:
                product_category = np.random.choice(ag_categories)
                # Agricultural products tend to have higher tariffs
                tariff_value = np.round(np.random.uniform(15, 45), 1)
                # Usually lower trade volumes
                trade_volume = np.round(np.random.uniform(50, 2000), 1)
            else:
                product_category = np.random.choice(non_ag_categories)
                # Non-agricultural products tend to have lower tariffs
                tariff_value = np.round(np.random.uniform(5, 25), 1)
                # Usually higher trade volumes
                trade_volume = np.round(np.random.uniform(500, 5000), 1)
            
            # Add a categorical field for filtering
            category_type = 'Agricultural' if is_agricultural else 'Non-Agricultural'
            
            data.append({
                'date': event_date.strftime('%Y-%m-%d'),
                'year': year,
                'source': source,
                'target': target,
                'tariff_rate': tariff_value,
                'product_category': product_category,
                'category_type': category_type,
                'trade_volume': trade_volume,
                'direction': direction
            })
    
    return pd.DataFrame(data)

# Create the data
tariff_data = generate_tariff_data()

# Function to get data
def get_tariff_data():
    return tariff_data

# Function to get aggregated average tariff data by year, source, target, and direction
def get_average_tariff_data():
    # Group by year, source, target, direction and compute average tariff rate and total trade volume
    avg_df = tariff_data.groupby(['year', 'source', 'target', 'direction', 'category_type']).agg({
        'tariff_rate': 'mean',  # Average tariff rate
        'trade_volume': 'sum',  # Sum of trade volume
        'date': 'min'  # Just take the first date for reference
    }).reset_index()
    
    # Round tariff rate to 1 decimal place
    avg_df['tariff_rate'] = avg_df['tariff_rate'].round(1)
    
    return avg_df

# Generate synthetic S&P 500 data
def generate_sp500_data():
    """Generate synthetic S&P 500 data from 2015 to 2022."""
    # Starting value of S&P 500 at the beginning of 2015
    start_value = 2058.20
    
    # Generate monthly dates from 2015-01-01 to 2022-12-31
    dates = pd.date_range(start='2015-01-01', end='2022-12-31', freq='ME')
    
    # Create tariff event dates for market reactions
    tariff_events = {
        '2018-03-22': -2.5,  # US announces steel and aluminum tariffs
        '2018-07-06': -1.8,  # US-China first round of tariffs
        '2019-05-10': -2.2,  # US increases tariffs on $200B of Chinese goods
        '2019-08-23': -2.6,  # China announces retaliatory tariffs
        '2019-12-13': 1.5,   # Phase One trade deal announcement
        '2020-01-15': 0.8,   # Phase One trade deal signing
    }
    
    # Base trend (general upward with some randomness)
    monthly_returns = np.random.normal(0.008, 0.02, len(dates))
    
    # Add COVID crash (March 2020)
    covid_crash_index = np.where(dates == pd.Timestamp('2020-03-31'))[0][0]
    monthly_returns[covid_crash_index] = -0.20
    monthly_returns[covid_crash_index + 1] = -0.10
    
    # Add recovery after COVID crash
    recovery_indices = range(covid_crash_index + 2, covid_crash_index + 6)
    monthly_returns[recovery_indices] = np.random.normal(0.05, 0.02, len(recovery_indices))
    
    # Add market correction (Late 2018)
    correction_index = np.where(dates == pd.Timestamp('2018-12-31'))[0][0]
    monthly_returns[correction_index] = -0.09
    monthly_returns[correction_index + 1] = 0.08  # Quick recovery
    
    # Apply tariff event effects to the closest monthly data points
    for event_date, effect in tariff_events.items():
        event_timestamp = pd.Timestamp(event_date)
        # Find the closest date in our monthly data
        closest_date_idx = np.argmin(np.abs(dates - event_timestamp))
        # Apply the effect - both immediate and slight follow-on effects
        monthly_returns[closest_date_idx] += effect / 100
        if closest_date_idx + 1 < len(monthly_returns):
            monthly_returns[closest_date_idx + 1] += effect / 200  # Half the effect next month
    
    # Generate cumulative S&P 500 values
    sp500_values = [start_value]
    for ret in monthly_returns:
        next_value = sp500_values[-1] * (1 + ret)
        sp500_values.append(next_value)
    
    # Remove the extra value from the calculation
    sp500_values = sp500_values[:-1]
    
    # Create DataFrame
    data = []
    for i, date in enumerate(dates):
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'year': date.year,
            'month': date.month,
            'sp500_value': round(sp500_values[i], 2),
            'monthly_return': round(monthly_returns[i] * 100, 2),
            'is_tariff_event': date.strftime('%Y-%m-%d')[:7] in [x[:7] for x in tariff_events.keys()]
        })
    
    return pd.DataFrame(data)

# Generate S&P 500 data
sp500_data = generate_sp500_data()

# Function to get S&P 500 data
def get_sp500_data():
    return sp500_data

def generate_employment_data():
    """Generate synthetic employment data that correlates with tariffs."""
    # Generate monthly data from 2015-01-01 to 2022-12-31
    dates = pd.date_range(start='2015-01-01', end='2022-12-31', freq='ME')
    
    # Create a base trend for unemployment rate (generally decreasing then affected by COVID)
    base_unemployment = np.linspace(5.7, 3.5, 48)  # Decreasing trend from 2015 to 2019
    covid_spike = np.concatenate([
        np.linspace(3.5, 14.8, 4),  # Sharp rise in March-April 2020
        np.linspace(14.8, 6.7, 8)    # Gradual decrease
    ])
    post_covid = np.linspace(6.7, 3.5, 44)  # Return to low unemployment
    
    # Combine all phases
    unemployment_rate = np.concatenate([base_unemployment, covid_spike, post_covid])
    
    # Define tariff events that impact employment in specific sectors
    tariff_events = {
        # Date: [Manufacturing effect, Agriculture effect, Services effect]
        '2018-03-22': [-0.2, 0.0, 0.0],   # Steel/Aluminum tariffs affect manufacturing 
        '2018-07-06': [-0.3, -0.5, -0.1],  # First US-China tariffs hit multiple sectors
        '2019-05-10': [-0.4, -0.7, -0.2],  # Escalation of tariffs on Chinese goods
        '2019-08-23': [-0.5, -0.8, -0.3],  # China retaliatory tariffs hit agriculture hard
        '2019-12-13': [0.2, 0.4, 0.1],    # Phase One deal - slight positive
        '2020-01-15': [0.3, 0.6, 0.2],    # Phase One signing - more positive
    }
    
    # Generate sectoral data with base trends and tariff effects
    manufacturing_jobs = 12500 + np.cumsum(np.random.normal(5, 15, len(dates)))
    agriculture_jobs = 2300 + np.cumsum(np.random.normal(1, 5, len(dates)))
    services_jobs = 105000 + np.cumsum(np.random.normal(50, 75, len(dates)))
    
    # Apply COVID effects
    covid_index = np.where(dates == pd.Timestamp('2020-03-31'))[0][0]
    manufacturing_jobs[covid_index:covid_index+3] *= np.array([0.92, 0.88, 0.90])  # 8-12% drop
    agriculture_jobs[covid_index:covid_index+3] *= np.array([0.95, 0.93, 0.94])  # 5-7% drop
    services_jobs[covid_index:covid_index+3] *= np.array([0.85, 0.75, 0.80])  # 15-25% drop (hit hardest)
    
    # Apply tariff event effects
    for event_date, effects in tariff_events.items():
        event_timestamp = pd.Timestamp(event_date)
        # Find the closest date in our monthly data
        closest_date_idx = np.argmin(np.abs(dates - event_timestamp))
        # Apply effects over 3 months (with diminishing impact)
        for i in range(3):
            if closest_date_idx + i < len(dates):
                factor = (3-i)/3  # Diminishing effect
                manufacturing_jobs[closest_date_idx + i] *= (1 + effects[0] * factor / 100)
                agriculture_jobs[closest_date_idx + i] *= (1 + effects[1] * factor / 100)
                services_jobs[closest_date_idx + i] *= (1 + effects[2] * factor / 100)
    
    # Create DataFrame
    data = []
    for i, date in enumerate(dates):
        # Add some monthly noise
        unemployment_with_noise = unemployment_rate[i] + np.random.normal(0, 0.2)
        
        # Is this month affected by a tariff event?
        is_tariff_month = date.strftime('%Y-%m-%d')[:7] in [x[:7] for x in tariff_events.keys()]
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'year': date.year,
            'month': date.month,
            'unemployment_rate': round(unemployment_with_noise, 1),
            'manufacturing_jobs': int(round(manufacturing_jobs[i])),
            'agriculture_jobs': int(round(agriculture_jobs[i])),
            'services_jobs': int(round(services_jobs[i])),
            'total_jobs': int(round(manufacturing_jobs[i] + agriculture_jobs[i] + services_jobs[i])),
            'is_tariff_event': is_tariff_month
        })
    
    return pd.DataFrame(data) 

def load_data():
    """Load all datasets."""
    return {
        'tariffs': get_tariff_data(),
        'sp500': get_sp500_data(),
        'employment': generate_employment_data()
    } 