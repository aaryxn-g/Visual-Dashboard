# E-Commerce Analytics Dashboard

A comprehensive analytics dashboard for e-commerce data analysis, built with Python, Dash, and Plotly.

## Overview

This project processes and visualizes e-commerce order data, providing insights into sales trends, customer behavior, and revenue metrics. The system consists of three main components:

1. **Data Processing Pipeline** (`merge.py`)
   - Merges order and product data
   - Performs data validation and cleaning
   - Generates comprehensive quality reports

2. **Data Optimization** (`optimize_data.py`)
   - Optimizes data types for memory efficiency
   - Removes redundant columns
   - Prepares data for visualization

3. **Interactive Dashboard** (`dashboard.py`)
   - Visualizes key metrics and trends
   - Provides interactive filtering and exploration
   - Built with Dash and Plotly

## Features

- **Sales Analytics**: Track revenue, orders, and profit margins
- **Customer Insights**: Analyze customer demographics and behavior
- **Product Performance**: Identify top-selling products and categories
- **Geographic Analysis**: Visualize sales by location
- **Temporal Analysis**: Explore trends over time

## Requirements

- Python 3.7+
- pandas
- plotly
- dash
- dash-bootstrap-components
- numpy

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aaryxn-g/Visual-Dashboard.git
   cd Visual-Dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare your data**:
   - Place your order data in `Order_Details.csv`
   - Place your product data in `Product_Details.csv`

2. **Run the data pipeline**:
   ```bash
   python merge.py
   python optimize_data.py
   ```

3. **Start the dashboard**:
   ```bash
   python dashboard.py
   ```
   Open your browser and navigate to `http://127.0.0.1:8050`

## File Structure

```
.
├── README.md               # This file
├── dashboard.py            # Main dashboard application
├── merge.py                # Data merging and processing
├── optimize_data.py        # Data optimization
├── requirements.txt        # Python dependencies
├── merged_order_product_details.csv  # Intermediate merged data
└── optimized_merged_data.csv         # Final optimized dataset
```

## Data Requirements

### Order Details (Order_Details.csv)
- Product ID
- Shipping Fee ($)
- Quantity (Units)
- Net Price ($)
- Customer Age Group
- Customer Location
- Customer Gender
- Seasonality
- Date

### Product Details (Product_Details.csv)
- Product ID
- Product Name
- Category
- Sub_Collection
- Unit Price ($)
- Tax Rate (%)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ for the LUG Datathon
- Special thanks to all contributors
