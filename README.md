[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ASTlQQ5B)

# Global Tariff Visualization

An interactive Dash application for visualizing global tariff data over time, focusing on tariffs imposed by or on the United States.

## Features

- Interactive arc map visualization showing tariff relationships between the US and other countries
- Filter by year range, tariff direction, and product categories
- Summary statistics on tariff events, rates, and affected trade volume
- Responsive design with Bootstrap styling

## Setup and Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your web browser and navigate to http://127.0.0.1:8050/

## Data

The application uses synthetic data generated in the `data.py` file, which simulates tariff events between the US and various countries from 2015 to 2022. Each tariff event includes:

- Source and target countries
- Tariff rate
- Product category
- Trade volume affected
- Date of implementation

## Technologies Used

- Dash - Web application framework
- Plotly - Interactive visualization library
- Pandas - Data manipulation
- Dash Bootstrap Components - Responsive UI components
