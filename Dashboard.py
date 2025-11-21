import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

# Load dataset
print("Loading dataset...")
df = pd.read_csv('optimized_merged_data.csv')

# Convert date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Extract date components if not present
if 'Year' not in df.columns:
    df['Year'] = df['Date'].dt.year
if 'Month' not in df.columns:
    df['Month'] = df['Date'].dt.month

print(f"Dataset loaded: {len(df):,} rows × {len(df.columns)} columns")
print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")

# Define color scheme and styling
COLORS = {
    'primary': '#2C7A7B',      # Teal
    'secondary': '#3182CE',     # Blue
    'success': '#38A169',       # Green
    'danger': '#E53E3E',        # Red
    'warning': '#DD6B20',       # Orange
    'info': '#4299E1',          # Light blue
    'background': '#F7FAFC',    # Light gray
    'card_bg': '#FFFFFF',       # White
    'text': '#2D3748',          # Dark gray
    'border': '#E2E8F0'         # Light border
}

CARD_STYLE = {
    'backgroundColor': COLORS['card_bg'],
    'border': f'1px solid {COLORS["border"]}',
    'borderRadius': '8px',
    'padding': '20px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'height': '100%'
}

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.COSMO, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

app.title = "E-Commerce Analytics Dashboard"
server = app.server

# Helper function to create KPI metric cards
def create_kpi_card(title, value, icon, color='primary', subtitle=''):
    """Create a KPI metric card with icon and values"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"fas {icon} fa-2x", 
                          style={'color': COLORS[color]}),
                ], style={'flex': '0 0 auto', 'marginRight': '15px'}),
                html.Div([
                    html.H6(title, className='text-muted mb-1', 
                           style={'fontSize': '0.875rem', 'fontWeight': '500'}),
                    html.H3(value, className='mb-1', 
                           style={'color': COLORS['text'], 'fontWeight': 'bold', 
                                  'fontSize': '1.75rem'}),
                    html.Small(subtitle, className='text-muted',
                              style={'fontSize': '0.75rem'}) if subtitle else None
                ], style={'flex': '1'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'padding': '1.25rem'})
    ], style={**CARD_STYLE, 'marginBottom': '0'})

# Helper function to create global filters row
def create_filter_row():
    """Create the global filters row with 4 dropdowns"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label('Date Range', className='fw-bold mb-2',
                              style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                    dcc.Dropdown(
                        id='date-filter',
                        options=[
                            {'label': 'Latest Month', 'value': 'month'},
                            {'label': 'Latest Quarter', 'value': 'quarter'},
                            {'label': 'Latest Year', 'value': 'year'},
                            {'label': 'All Dates', 'value': 'all'}
                        ],
                        value='all',
                        clearable=False,
                        style={'fontSize': '0.875rem'}
                    )
                ], width=3),
                dbc.Col([
                    html.Label('Product Category', className='fw-bold mb-2',
                              style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                    dcc.Dropdown(
                        id='category-filter',
                        options=[{'label': 'All Categories', 'value': 'all'}] +
                               [{'label': cat, 'value': cat} 
                                for cat in sorted(df['Category'].unique())],
                        value=['all'],
                        multi=True,
                        clearable=False,
                        style={'fontSize': '0.875rem'}
                    )
                ], width=3),
                dbc.Col([
                    html.Label('Customer Location', className='fw-bold mb-2',
                              style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                    dcc.Dropdown(
                        id='location-filter',
                        options=[{'label': 'All Locations', 'value': 'all'}] +
                               [{'label': loc, 'value': loc} 
                                for loc in sorted(df['Customer Location'].unique())],
                        value=['all'],
                        multi=True,
                        clearable=False,
                        style={'fontSize': '0.875rem'}
                    )
                ], width=3),
                dbc.Col([
                    html.Label('Order Value', className='fw-bold mb-2',
                              style={'fontSize': '0.875rem', 'color': COLORS['text']}),
                    dcc.Dropdown(
                        id='order-value-filter',
                        options=[{'label': 'All Values', 'value': 'all'}] +
                               [{'label': val, 'value': val} 
                                for val in sorted(df['Order_Value_Category'].unique())],
                        value=['all'],
                        multi=True,
                        clearable=False,
                        style={'fontSize': '0.875rem'}
                    )
                ], width=3)
            ])
        ], style={'padding': '1.25rem'})
    ], style={
        **CARD_STYLE, 
        'marginBottom': '20px',
        'position': 'sticky',
        'top': '0',
        'zIndex': '1000'
    })

# Define navigation bar
navbar = dbc.Navbar(
    dbc.Container([
        html.Div([
            html.I(className="fas fa-shopping-cart", 
                  style={'fontSize': '28px', 'marginRight': '12px', 'color': 'white'}),
            dbc.NavbarBrand("E-Commerce Analytics", 
                           style={'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': 'white'})
        ], style={'display': 'flex', 'alignItems': 'center'})
    ], fluid=True),
    color=COLORS['primary'],
    dark=True,
    sticky='top',
    style={'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px'}
)

# Define main application layout
app.layout = html.Div([
    navbar,
    
    dbc.Container([
        # Global Filters Row
        create_filter_row(),
        
        # KPI Cards Row
        dbc.Row([
            dbc.Col(html.Div(id='kpi-total-revenue'), width=3),
            dbc.Col(html.Div(id='kpi-total-orders'), width=3),
            dbc.Col(html.Div(id='kpi-avg-order-value'), width=3),
            dbc.Col(html.Div(id='kpi-profit-margin'), width=3),
        ], className='mb-4'),
        
        # Chart Row 1: Revenue Overview
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Revenue Trend (2020-2024)', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='revenue-trend', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Revenue by Category', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='revenue-by-category', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=4)
        ], className='mb-4'),
        
        # Chart Row 2: Product Performance
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Top 20 Products by Revenue', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='top-products', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=12)
        ], className='mb-4'),
        
        # Chart Row 3: Geographic & Customer Analysis
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Geographic Performance', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='revenue-by-location', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Customer Demographics', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='customer-demographics', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=6)
        ], className='mb-4'),
        
        # Chart Row 4: Advanced Analytics
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Unit Price vs Revenue Analysis', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='price-revenue-scatter', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Monthly Revenue Heatmap', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='revenue-heatmap', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=6)
        ], className='mb-4'),
        
        # Chart Row 5: Seasonality & Distribution
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Seasonality Impact', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='seasonality-impact', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Order Value Distribution', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='order-value-dist', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Profit Margin by Category', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='profit-margin-analysis', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=4)
        ], className='mb-4'),
        
        # Chart Row 6: Shipping & Data Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Shipping Fee Impact on Margins', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(dcc.Graph(id='shipping-impact', config={'displayModeBar': False}),
                                style={'padding': '10px'})
                ], style=CARD_STYLE)
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5('Order Details Summary', 
                                          className='mb-0',
                                          style={'fontSize': '1.1rem', 'fontWeight': '600'})),
                    dbc.CardBody(html.Div(id='data-table'),
                                style={'padding': '10px', 'overflowX': 'auto'})
                ], style=CARD_STYLE)
            ], width=6)
        ], className='mb-4'),
        
        # Footer
        html.Hr(style={'margin': '30px 0', 'borderColor': COLORS['border']}),
        html.Div([
            html.P('E-Commerce Analytics Dashboard | 1M Orders • 5 Years • 15 Locations',
                  className='text-center',
                  style={'color': '#718096', 'fontSize': '0.875rem', 'marginBottom': '20px'})
        ])
        
    ], fluid=True, style={'maxWidth': '1400px'})
    
], style={'backgroundColor': COLORS['background'], 'minHeight': '100vh', 'paddingBottom': '20px'})

# Master callback function to update all dashboard components
@callback(
    [Output('kpi-total-revenue', 'children'),
     Output('kpi-total-orders', 'children'),
     Output('kpi-avg-order-value', 'children'),
     Output('kpi-profit-margin', 'children'),
     Output('revenue-trend', 'figure'),
     Output('revenue-by-category', 'figure'),
     Output('top-products', 'figure'),
     Output('revenue-by-location', 'figure'),
     Output('customer-demographics', 'figure'),
     Output('price-revenue-scatter', 'figure'),
     Output('revenue-heatmap', 'figure'),
     Output('seasonality-impact', 'figure'),
     Output('order-value-dist', 'figure'),
     Output('profit-margin-analysis', 'figure'),
     Output('shipping-impact', 'figure'),
     Output('data-table', 'children')],
    [Input('date-filter', 'value'),
     Input('category-filter', 'value'),
     Input('location-filter', 'value'),
     Input('order-value-filter', 'value')]
)
def update_dashboard(date_range, categories, locations, order_values):
    # Start with full dataset
    filtered_df = df.copy()
    
    # Apply filters
    if date_range != 'all':
        max_date = filtered_df['Date'].max()
        if date_range == 'month':
            filtered_df = filtered_df[filtered_df['Date'] >= max_date - pd.DateOffset(months=1)]
        elif date_range == 'quarter':
            filtered_df = filtered_df[filtered_df['Date'] >= max_date - pd.DateOffset(months=3)]
        elif date_range == 'year':
            filtered_df = filtered_df[filtered_df['Date'] >= max_date - pd.DateOffset(years=1)]
    
    if 'all' not in categories:
        filtered_df = filtered_df[filtered_df['Category'].isin(categories)]
    
    if 'all' not in locations:
        filtered_df = filtered_df[filtered_df['Customer Location'].isin(locations)]
    
    if 'all' not in order_values:
        filtered_df = filtered_df[filtered_df['Order_Value_Category'].isin(order_values)]
    
    # Calculate KPI metrics
    total_revenue = filtered_df['Total_Revenue'].sum()
    total_orders = len(filtered_df)
    avg_order_value = filtered_df['Total_Revenue'].mean()
    avg_profit_margin = filtered_df['Profit_Margin'].mean()
    unique_products = filtered_df['Product ID'].nunique()
    
    # Create KPI cards
    kpi_revenue = create_kpi_card(
        'Total Revenue',
        f'${total_revenue:,.0f}',
        'fa-dollar-sign',
        'primary',
        f'{total_orders:,} orders'
    )
    
    kpi_orders = create_kpi_card(
        'Total Orders',
        f'{total_orders:,}',
        'fa-shopping-bag',
        'secondary',
        f'{unique_products} products'
    )
    
    kpi_aov = create_kpi_card(
        'Avg Order Value',
        f'${avg_order_value:,.2f}',
        'fa-chart-line',
        'success',
        'per transaction'
    )
    
    kpi_margin = create_kpi_card(
        'Avg Profit Margin',
        f'${avg_profit_margin:,.2f}',
        'fa-percent',
        'warning',
        'per order'
    )
    
    # Chart 1: Revenue Trend Line
    monthly_revenue = filtered_df.groupby(
        filtered_df['Date'].dt.to_period('M')
    )['Total_Revenue'].sum().reset_index()
    monthly_revenue['Date'] = monthly_revenue['Date'].dt.to_timestamp()
    
    fig_trend = px.line(
        monthly_revenue,
        x='Date',
        y='Total_Revenue',
        labels={'Total_Revenue': 'Revenue ($)', 'Date': 'Month'}
    )
    fig_trend.update_traces(line_color=COLORS['primary'], line_width=3)
    fig_trend.update_layout(
        template='plotly_white',
        hovermode='x unified',
        height=350,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 2: Revenue by Category Pie
    category_revenue = filtered_df.groupby('Category')['Total_Revenue'].sum().reset_index()
    
    fig_category = px.pie(
        category_revenue,
        values='Total_Revenue',
        names='Category',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_category.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont_size=12
    )
    fig_category.update_layout(
        template='plotly_white',
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 3: Top 20 Products Horizontal Bar
    top_products = filtered_df.groupby('Product Name').agg({
        'Total_Revenue': 'sum',
        'Category': 'first'
    }).reset_index().sort_values('Total_Revenue', ascending=False).head(20)
    
    fig_products = px.bar(
        top_products,
        y='Product Name',
        x='Total_Revenue',
        color='Category',
        orientation='h',
        labels={'Total_Revenue': 'Revenue ($)', 'Product Name': ''},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_products.update_layout(
        template='plotly_white',
        height=500,
        margin=dict(l=150, r=40, t=20, b=40),
        yaxis={'categoryorder': 'total ascending'},
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 4: Revenue by Location Horizontal Bar
    location_revenue = filtered_df.groupby('Customer Location')['Total_Revenue'].sum().reset_index()
    
    fig_location = px.bar(
        location_revenue,
        y='Customer Location',
        x='Total_Revenue',
        orientation='h',
        labels={'Total_Revenue': 'Revenue ($)', 'Customer Location': ''}
    )
    fig_location.update_traces(marker_color=COLORS['secondary'])
    fig_location.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=150, r=40, t=20, b=40),
        yaxis={'categoryorder': 'total ascending'},
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 5: Customer Demographics Grouped Bar
    age_gender = filtered_df.groupby(
        ['Customer Age Group', 'Customer Gender']
    )['Total_Revenue'].sum().reset_index()
    
    fig_demographics = px.bar(
        age_gender,
        x='Customer Age Group',
        y='Total_Revenue',
        color='Customer Gender',
        barmode='group',
        labels={'Total_Revenue': 'Revenue ($)', 'Customer Age Group': 'Age Group'},
        color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['success']]
    )
    fig_demographics.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 6: Unit Price vs Revenue Scatter (Sampled)
    sample_size = min(5000, len(filtered_df))
    sample_df = filtered_df.sample(n=sample_size, random_state=42)
    
    fig_scatter = px.scatter(
        sample_df,
        x='Unit Price ($)',
        y='Total_Revenue',
        color='Category',
        size='Quantity (Units)',
        labels={'Unit Price ($)': 'Unit Price ($)', 'Total_Revenue': 'Total Revenue ($)'},
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_scatter.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 7: Monthly Revenue Heatmap
    heatmap_data = filtered_df.groupby(['Year', 'Month'])['Total_Revenue'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='Year', columns='Month', values='Total_Revenue')
    
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=month_labels[:len(heatmap_pivot.columns)],
        y=heatmap_pivot.index,
        colorscale='Teal',
        hoverongaps=False,
        hovertemplate='Year: %{y}<br>Month: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>'
    ))
    fig_heatmap.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=60, r=40, t=20, b=60),
        xaxis_title='Month',
        yaxis_title='Year',
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 8: Seasonality Impact Grouped Bar
    seasonality_data = filtered_df.groupby('Seasonality').agg({
        'Total_Revenue': 'sum',
        'Product ID': 'count'
    }).reset_index()
    seasonality_data.columns = ['Seasonality', 'Revenue', 'Orders']
    
    fig_seasonality = go.Figure(data=[
        go.Bar(
            name='Revenue', 
            x=seasonality_data['Seasonality'], 
            y=seasonality_data['Revenue'], 
            marker_color=COLORS['primary'],
            yaxis='y'
        ),
        go.Bar(
            name='Orders', 
            x=seasonality_data['Seasonality'], 
            y=seasonality_data['Orders'], 
            marker_color=COLORS['secondary'],
            yaxis='y2'
        )
    ])
    fig_seasonality.update_layout(
        template='plotly_white',
        height=350,
        margin=dict(l=40, r=40, t=20, b=40),
        yaxis=dict(title='Revenue ($)'),
        yaxis2=dict(title='Orders', overlaying='y', side='right'),
        barmode='group',
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 9: Order Value Distribution Bar
    value_dist = filtered_df.groupby('Order_Value_Category')['Total_Revenue'].sum().reset_index()
    
    # Define proper order for categories
    category_order = ['Small', 'Medium', 'Large', 'Enterprise']
    value_dist['Order_Value_Category'] = pd.Categorical(
        value_dist['Order_Value_Category'], 
        categories=category_order, 
        ordered=True
    )
    value_dist = value_dist.sort_values('Order_Value_Category')
    
    fig_value_dist = px.bar(
        value_dist,
        x='Order_Value_Category',
        y='Total_Revenue',
        labels={'Order_Value_Category': 'Order Size', 'Total_Revenue': 'Revenue ($)'}
    )
    fig_value_dist.update_traces(marker_color=COLORS['success'])
    fig_value_dist.update_layout(
        template='plotly_white',
        height=350,
        margin=dict(l=40, r=40, t=20, b=40),
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 10: Profit Margin by Category Horizontal Bar
    margin_data = filtered_df.groupby('Category')['Profit_Margin'].mean().reset_index()
    margin_data = margin_data.sort_values('Profit_Margin', ascending=True)
    
    fig_margin = px.bar(
        margin_data,
        y='Category',
        x='Profit_Margin',
        orientation='h',
        labels={'Profit_Margin': 'Avg Profit Margin ($)', 'Category': ''}
    )
    fig_margin.update_traces(marker_color=COLORS['warning'])
    fig_margin.update_layout(
        template='plotly_white',
        height=350,
        margin=dict(l=120, r=40, t=20, b=40),
        font=dict(family='Arial, sans-serif', size=12)
    )
    
    # Chart 11: Shipping Fee Impact Line
    # Bin shipping fees into 10 ranges
    filtered_df['Shipping_Bin'] = pd.cut(filtered_df['Shipping Fee ($)'], bins=10)
    shipping_impact = filtered_df.groupby('Shipping_Bin')['Profit_Margin'].mean().reset_index()
    shipping_impact['Shipping_Bin_Label'] = shipping_impact['Shipping_Bin'].astype(str)
    
    fig_shipping = px.line(
        shipping_impact,
        x='Shipping_Bin_Label',
        y='Profit_Margin',
        labels={'Shipping_Bin_Label': 'Shipping Fee Range', 'Profit_Margin': 'Avg Profit Margin ($)'}
    )
    fig_shipping.update_traces(line_color=COLORS['danger'], line_width=3)
    fig_shipping.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=40, r=40, t=20, b=100),
        xaxis_tickangle=-45,
        font=dict(family='Arial, sans-serif', size=11)
    )
    
    # Chart 12: Order Details Summary Table
    summary_table = filtered_df.groupby('Category').agg({
        'Total_Revenue': 'sum',
        'Product ID': 'count',
        'Profit_Margin': 'mean',
        'Quantity (Units)': 'sum'
    }).reset_index()
    
    summary_table.columns = ['Category', 'Revenue', 'Orders', 'Avg Margin', 'Units Sold']
    
    # Format numbers
    summary_table['Revenue'] = summary_table['Revenue'].apply(lambda x: f'${x:,.0f}')
    summary_table['Orders'] = summary_table['Orders'].apply(lambda x: f'{x:,}')
    summary_table['Avg Margin'] = summary_table['Avg Margin'].apply(lambda x: f'${x:,.2f}')
    summary_table['Units Sold'] = summary_table['Units Sold'].apply(lambda x: f'{x:,}')
    
    table_component = dbc.Table.from_dataframe(
        summary_table,
        striped=True,
        bordered=True,
        hover=True,
        size='sm',
        className='mb-0',
        style={'fontSize': '0.875rem'}
    )
    
    # Return all outputs
    return (
        kpi_revenue, 
        kpi_orders, 
        kpi_aov, 
        kpi_margin,
        fig_trend, 
        fig_category, 
        fig_products, 
        fig_location, 
        fig_demographics,
        fig_scatter, 
        fig_heatmap, 
        fig_seasonality, 
        fig_value_dist, 
        fig_margin,
        fig_shipping, 
        table_component
    )

# Run application
if __name__ == '__main__':
    print("\n" + "="*80)
    print("E-COMMERCE ANALYTICS DASHBOARD".center(80))
    print("="*80)
    print(f"\nDataset loaded: {len(df):,} orders")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"Categories: {df['Category'].nunique()}")
    print(f"Locations: {df['Customer Location'].nunique()}")
    print(f"Products: {df['Product ID'].nunique()}")
    print("\n" + "="*80)
    print("Starting dashboard server...".center(80))
    print("="*80)
    print("\n🚀 Dashboard running at: http://127.0.0.1:8050")
    print("\nPress CTRL+C to stop the server\n")
    
if __name__ == '__main__':
    app.run(debug=True, port=8050)
