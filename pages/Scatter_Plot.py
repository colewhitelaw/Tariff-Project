import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Load the data
df = pd.read_csv("tariff_rate_scatterplot_data.csv")

# Extract all unique categories
categories = df["Category"].unique()

# Store all traces and annotations
traces = []
regression_info = []

# Loop through each category and prepare traces and annotations
for idx, cat in enumerate(categories):
    filtered_df = df[df["Category"] == cat]
    x = filtered_df["Rate imposed by the US"]
    y = filtered_df["Rate imposed on the US"]

    # Scatter points for this category
    scatter = go.Scatter(
        x=x,
        y=y,
        mode="markers",
        name=f"{cat} (Data)",
        text=filtered_df["Country"] + " (" + filtered_df["Year"].astype(str) + ")",
        hoverinfo="text",
        marker=dict(size=8),
        visible=True if idx == 0 else False  # Make the first category visible by default
    )
    traces.append(scatter)

    # Best fit line (if enough data points)
    if len(x) >= 2:
        slope, intercept = np.polyfit(x, y, 1)
        r_value = np.corrcoef(x, y)[0, 1]
        r_squared = r_value ** 2

        x_fit = np.linspace(x.min(), x.max(), 100)
        y_fit = slope * x_fit + intercept

        fit_line = go.Scatter(
            x=x_fit,
            y=y_fit,
            mode="lines",
            name=f"{cat} (Best Fit)",
            line=dict(dash="dash", color="gray"),
            hoverinfo="skip",
            visible=True if idx == 0 else False  # Make the first category's line visible by default
        )
        traces.append(fit_line)

        # Equation and R² text for annotation
        eqn_text = f"y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.3f}"

        annotation = dict(
            x=1.02,
            y=0.75 - (0.1 * idx),  # Adjusts the position of each annotation
            xref='paper',
            yref='paper',
            text=eqn_text,
            showarrow=False,
            align='left',
            font=dict(size=12),
            visible=True if idx == 0 else False  # Make only the first annotation visible initially
        )
        regression_info.append(annotation)

# Create dropdown buttons for category selection
dropdown_buttons = []
for idx, cat in enumerate(categories):
    visibility = [False] * len(traces)
    visibility[2 * idx] = True        # scatter
    visibility[2 * idx + 1] = True    # best-fit line

    # Show the corresponding annotation for the selected category
    updated_annotation = [regression_info[idx]]

    button = dict(
        label=cat,
        method="update",
        args=[
            {"visible": visibility},  # Set visibility for scatter and best-fit line
            {
                "title": f"Tariff Rates - Category: {cat}",
                "annotations": updated_annotation  # Update the annotation for the selected category
            }
        ]
    )
    dropdown_buttons.append(button)

# Create the figure with the initial traces and annotations
fig = go.Figure(data=traces)
fig.update_layout(
    title=f"Tariff Rates - Category: {categories[0]}",
    xaxis_title="Rate imposed by the US",
    yaxis_title="Rate imposed on the US",
    annotations=[regression_info[0]],  # Show the first annotation by default
    updatemenus=[dict(
        buttons=dropdown_buttons,
        direction="down",
        x=0.5,
        y=-0.25,
        showactive=True,
        xanchor="center",
        yanchor="top"
    )],
    legend=dict(x=1.02, y=1, xanchor='left'),
    margin=dict(b=180, r=200)  # Extra space for dropdown and legend
)

# Show the plot
fig.show()
