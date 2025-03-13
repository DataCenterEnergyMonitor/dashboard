import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from io import BytesIO
import base64

# Define color palette for reporting scopes (using RGB tuples instead of rgba strings)
REPORTING_SCOPE_COLORS = {
    'Company Wide Electricity Use': (23/255, 79/255, 138/255, 0.8),
    'Data Center Electricity Use': '#C16597',
    'Data Center Fuel Use': '#AACE63',
    'Data Center Water Use': '#23CDC6',
    'Comprehensive': '#4CAF50'
}

def create_timeline_chart(filtered_df):
    """
    Create a stacked timeline chart showing companies' reporting patterns over time.
    Returns the chart as a base64 encoded string for display in Dash.
    """
    if filtered_df.empty:
        return None

    # Get unique companies and years
    companies = sorted(filtered_df['company_name'].unique())
    years = sorted(filtered_df['reported_data_year'].unique())
    
    # Calculate scope data for each company-year combination
    scope_data = {}
    for company in companies:
        for year in years:
            mask = (filtered_df['company_name'] == company) & (filtered_df['reported_data_year'] == year)
            reported_scopes = filtered_df[mask]['reporting_scope'].unique()
            scope_data[(company, year)] = list(reported_scopes)

    # Create the figure
    fig_width = max(12, len(years) * 0.8)
    fig_height = max(8, len(companies) * 0.4)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    # Set background
    ax.set_facecolor('#f0f0f0')
    
    # Draw cells
    for i, company in enumerate(companies):
        for j, year in enumerate(years):
            x0, y0 = j, i
            width, height = 1, 1
            
            reported_scopes = scope_data[(company, year)]
            num_scopes = len(reported_scopes)
            
            # Draw base cell
            rect = patches.Rectangle(
                (x0, y0), width, height,
                facecolor='white' if num_scopes > 0 else '#f0f0f0',
                edgecolor='white',
                linewidth=1
            )
            ax.add_patch(rect)
            
            if num_scopes > 0:
                if num_scopes >= 3:
                    # Comprehensive reporting - solid green
                    rect = patches.Rectangle(
                        (x0, y0), width, height,
                        facecolor=REPORTING_SCOPE_COLORS['Comprehensive'],
                        edgecolor='white',
                        linewidth=1
                    )
                    ax.add_patch(rect)
                else:
                    # Draw sections for each scope
                    section_width = width / num_scopes
                    for k, scope in enumerate(reported_scopes):
                        rect = patches.Rectangle(
                            (x0 + k * section_width, y0),
                            section_width, height,
                            facecolor=REPORTING_SCOPE_COLORS[scope],
                            edgecolor='white',
                            linewidth=1
                        )
                        ax.add_patch(rect)
    
    # Set chart limits and labels
    ax.set_xlim(0, len(years))
    ax.set_ylim(0, len(companies))
    
    # Configure ticks and labels
    ax.set_xticks(np.arange(0.5, len(years) + 0.5))
    ax.set_yticks(np.arange(0.5, len(companies) + 0.5))
    ax.set_xticklabels(years, rotation=45)
    ax.set_yticklabels(companies)
    
    # Add gridlines
    ax.set_xticks(np.arange(0, len(years) + 1, 1), minor=True)
    ax.set_yticks(np.arange(0, len(companies) + 1, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle='-', linewidth=2)
    
    # Create legend
    legend_elements = [
        patches.Patch(facecolor=color, edgecolor='white', label=scope)
        for scope, color in REPORTING_SCOPE_COLORS.items()
    ]
    ax.legend(
        handles=legend_elements,
        title="Reporting Scopes",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )
    
    # Set labels and title
    plt.title('Data Center Reporting Timeline', pad=20)
    plt.xlabel('Reporting Year')
    plt.ylabel('Company')
    
    # Adjust layout
    plt.tight_layout()
    
    # Convert plot to base64 string
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8') 