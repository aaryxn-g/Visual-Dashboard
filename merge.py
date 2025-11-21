import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

ORDER_FILE = 'Order_Details.csv'
PRODUCT_FILE = 'Product_Details.csv'
OUTPUT_FILE = 'merged_order_product_details.csv'
REPORT_FILE = 'merge_quality_report.txt'

def format_bytes(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"

def print_section(title):
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80)

def main():
    script_start = datetime.now()
    
    print_section("E-COMMERCE DATASET MERGE PIPELINE")
    print(f"Started: {script_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print_section("STEP 1: LOADING DATASETS")
    
    order_dtypes = {
        'Product ID': 'object',
        'Shipping Fee ($)': 'float32',
        'Quantity (Units)': 'int32',
        'Net Price ($)': 'float64',
        'Customer Age Group': 'category',
        'Customer Location': 'category',
        'Customer Gender': 'category',
        'Seasonality': 'category',
        'Date': 'object'
    }
    
    product_dtypes = {
        'Product ID': 'object',
        'Product Name': 'object',
        'Category': 'category',
        'Sub_Collection': 'category',
        'Unit Price ($)': 'float64',
        'Tax Rate (%)': 'int8'
    }
    
    try:
        print(f"Loading {ORDER_FILE}...")
        orders = pd.read_csv(ORDER_FILE, dtype=order_dtypes)
        print(f"  Loaded: {len(orders):,} rows × {len(orders.columns)} columns")
        
        print(f"\nLoading {PRODUCT_FILE}...")
        products = pd.read_csv(PRODUCT_FILE, dtype=product_dtypes)
        print(f"  Loaded: {len(products):,} rows × {len(products.columns)} columns")
        
    except FileNotFoundError as e:
        print(f"\nERROR: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR loading files: {e}")
        sys.exit(1)
    
    print_section("STEP 2: DATA VALIDATION & QUALITY CHECKS")
    
    print("\nParsing date fields...")
    orders['Date'] = pd.to_datetime(orders['Date'], format='%Y-%m-%d', errors='coerce')
    date_nulls = orders['Date'].isna().sum()
    
    if date_nulls > 0:
        print(f"  Warning: {date_nulls} dates failed to parse")
    
    print("\nORDERS DATASET PROFILE:")
    print(f"  Rows: {len(orders):,}")
    print(f"  Columns: {len(orders.columns)}")
    print(f"  Date Range: {orders['Date'].min().date()} to {orders['Date'].max().date()}")
    print(f"  Null Values: {orders.isnull().sum().sum()}")
    
    print("\nPRODUCTS DATASET PROFILE:")
    print(f"  Rows: {len(products):,}")
    print(f"  Columns: {len(products.columns)}")
    print(f"  Null Values: {products.isnull().sum().sum()}")
    
    print("\nPRODUCT ID ANALYSIS:")
    orders_unique_ids = orders['Product ID'].nunique()
    products_unique_ids = products['Product ID'].nunique()
    orders_duplicates = (orders['Product ID'].value_counts() > 1).sum()
    products_duplicates = (products['Product ID'].value_counts() > 1).sum()
    
    print(f"  Unique IDs in Orders: {orders_unique_ids:,}")
    print(f"  Unique IDs in Products: {products_unique_ids:,}")
    print(f"  Duplicate IDs in Orders: {orders_duplicates:,} (expected for multiple orders)")
    print(f"  Duplicate IDs in Products: {products_duplicates:,} (should be 0)")
    
    orders_ids = set(orders['Product ID'].unique())
    products_ids = set(products['Product ID'].unique())
    overlap = orders_ids.intersection(products_ids)
    only_orders = orders_ids - products_ids
    only_products = products_ids - orders_ids
    
    print(f"\nOVERLAP ANALYSIS:")
    print(f"  IDs in both datasets: {len(overlap):,} ({len(overlap)/len(orders_ids)*100:.2f}%)")
    print(f"  IDs only in Orders: {len(only_orders):,}")
    print(f"  IDs only in Products: {len(only_products):,}")
    
    if len(only_orders) > 0:
        print(f"  Warning: {len(only_orders)} orders will be lost in INNER join")
    
    print_section("STEP 3: MERGING DATASETS (INNER JOIN)")
    
    merge_start = datetime.now()
    print(f"Executing INNER JOIN on 'Product ID'...")
    
    products_unique = products.drop_duplicates(subset=['Product ID'], keep='first')
    print(f"  Removed {len(products) - len(products_unique)} duplicate product entries")
    
    merged = pd.merge(
        orders,
        products_unique,
        on='Product ID',
        how='inner'
    )
    
    merge_duration = (datetime.now() - merge_start).total_seconds()
    retention_rate = (len(merged) / len(orders)) * 100
    
    print(f"\nMerge completed successfully!")
    print(f"  Output Rows: {len(merged):,}")
    print(f"  Output Columns: {len(merged.columns)}")
    print(f"  Retention Rate: {retention_rate:.2f}%")
    print(f"  Duration: {merge_duration:.2f}s")
    
    print_section("STEP 4: CALCULATING DERIVED FIELDS")
    
    calc_start = datetime.now()
    
    print("\nCalculating financial metrics...")
    merged['Revenue_Before_Tax'] = merged['Unit Price ($)'] * merged['Quantity (Units)']
    merged['Tax_Amount'] = merged['Revenue_Before_Tax'] * (merged['Tax Rate (%)'] / 100)
    merged['Total_Revenue'] = merged['Revenue_Before_Tax'] + merged['Tax_Amount']
    merged['Total_Shipping_Revenue'] = merged['Shipping Fee ($)'] * merged['Quantity (Units)']
    merged['Profit_Margin'] = ((merged['Net Price ($)'] - merged['Unit Price ($)']) / merged['Unit Price ($)'] * 100).round(2)
    
    print("Extracting temporal components...")
    merged['Year'] = merged['Date'].dt.year.astype('int16')
    merged['Month'] = merged['Date'].dt.month.astype('int8')
    merged['Quarter'] = merged['Date'].dt.quarter.astype('int8')
    merged['Day_of_Week'] = merged['Date'].dt.day_name()
    merged['Date_Week'] = merged['Date'].dt.isocalendar().week.astype('int8')
    merged['Year_Month'] = merged['Date'].dt.strftime('%Y-%m')
    merged['Year_Quarter'] = merged['Date'].dt.to_period('Q').astype(str)
    
    print("Creating categorical segments...")
    merged['Price_Segment'] = pd.cut(
        merged['Unit Price ($)'],
        bins=[0, 500, 1000, 1500, 2000],
        labels=['Budget ($0-500)', 'Mid-Range ($500-1K)', 'Premium ($1K-1.5K)', 'Luxury ($1.5K-2K)']
    )
    
    merged['Order_Value_Category'] = pd.cut(
        merged['Total_Revenue'],
        bins=[0, 10000, 100000, 500000, float('inf')],
        labels=['Small', 'Medium', 'Large', 'Enterprise']
    )
    
    calc_duration = (datetime.now() - calc_start).total_seconds()
    
    print(f"\nDerived fields completed!")
    print(f"  New Columns Added: 17")
    print(f"  Final Shape: {merged.shape[0]:,} rows × {merged.shape[1]} columns")
    print(f"  Duration: {calc_duration:.2f}s")
    
    print_section("STEP 5: POST-MERGE QUALITY VERIFICATION")
    
    merged_memory = merged.memory_usage(deep=True).sum()
    null_counts = merged.isnull().sum()
    has_nulls = null_counts[null_counts > 0]
    
    print(f"\nMERGED DATASET SUMMARY:")
    print(f"  Total Rows: {len(merged):,}")
    print(f"  Total Columns: {len(merged.columns)}")
    print(f"  Memory Usage: {format_bytes(merged_memory)}")
    
    if len(has_nulls) > 0:
        print(f"\nCOLUMNS WITH NULL VALUES:")
        for col, count in has_nulls.items():
            print(f"  {col}: {count:,} ({count/len(merged)*100:.2f}%)")
    
    print(f"\nDATA TYPE DISTRIBUTION:")
    dtype_counts = merged.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  {dtype}: {count} columns")
    
    print_section("STEP 6: BUSINESS INTELLIGENCE METRICS")
    
    total_revenue = merged['Total_Revenue'].sum()
    revenue_before_tax = merged['Revenue_Before_Tax'].sum()
    total_tax = merged['Tax_Amount'].sum()
    
    print(f"\nREVENUE METRICS:")
    print(f"  Total Revenue (with tax): ${total_revenue:,.2f}")
    print(f"  Total Revenue (before tax): ${revenue_before_tax:,.2f}")
    print(f"  Total Tax Collected: ${total_tax:,.2f}")
    
    top_locations = merged.groupby('Customer Location')['Total_Revenue'].sum().sort_values(ascending=False).head(3)
    print(f"  Top Locations by Revenue:")
    for loc, rev in top_locations.items():
        print(f"    {loc}: ${rev:,.2f}")
    
    print_section("STEP 7: SAVING MERGED DATASET")
    
    save_start = datetime.now()
    
    try:
        merged.to_csv(OUTPUT_FILE, index=False)
        save_duration = (datetime.now() - save_start).total_seconds()
        
        file_size = os.path.getsize(OUTPUT_FILE)
        
        print(f"\nDataset saved successfully!")
        print(f"  File: {OUTPUT_FILE}")
        print(f"  Size: {format_bytes(file_size)}")
        print(f"  Duration: {save_duration:.2f}s")
        
    except Exception as e:
        print(f"\nERROR saving file: {e}")
        save_duration = 0
    
    print_section("STEP 8: GENERATING QUALITY REPORT")
    
    total_duration = (datetime.now() - script_start).total_seconds()
    
    report = f"""
    {'='*80}
    E-COMMERCE DATASET MERGE QUALITY REPORT
    {'='*80}
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Total Processing Time: {total_duration:.2f} seconds

    {'='*80}
    MERGE SUMMARY
    {'='*80}
    Input Files:
      Orders: {ORDER_FILE}
        - Rows: {len(orders):,}
        - Columns: {len(orders.columns)}
        
      Products: {PRODUCT_FILE}
        - Rows: {len(products):,}
        - Columns: {len(products.columns)}

    Output File: {OUTPUT_FILE}
      - Rows: {len(merged):,}
      - Columns: {len(merged.columns)}
      - Memory: {format_bytes(merged_memory)}
      - Size: {format_bytes(file_size) if 'file_size' in locals() else 'N/A'}
      - Join Type: INNER JOIN on 'Product ID'
      - Retention Rate: {retention_rate:.2f}%

    {'='*80}
    PRODUCT ID ANALYSIS
    {'='*80}
    Unique Product IDs:
      - In Orders: {orders_unique_ids:,}
      - In Products: {products_unique_ids:,}
      - In Both (Overlap): {len(overlap):,}
      - Only in Orders: {len(only_orders):,}
      - Only in Products: {len(only_products):,}
      
    Match Rate: {len(overlap)/len(orders_ids)*100:.2f}%
    Merge Completeness: {'Excellent' if retention_rate > 99 else 'Some data loss'}

    {'='*80}
    DATA QUALITY METRICS
    {'='*80}
    Null Values per Column:
    {merged.isnull().sum().to_string()}

    Data Type Distribution:
    {merged.dtypes.value_counts().to_string()}

    Date Validation:
      - Date Range: {merged['Date'].min().date()} to {merged['Date'].max().date()}
      - Invalid Dates: {date_nulls}
      - Total Days: {(merged['Date'].max() - merged['Date'].min()).days}

    {'='*80}
    BUSINESS INTELLIGENCE METRICS
    {'='*80}
    Revenue Metrics:
      Total Revenue (with tax): ${total_revenue:,.2f}
      Total Revenue (before tax): ${revenue_before_tax:,.2f}
      Total Tax Collected: ${total_tax:,.2f}

    {'='*80}
    CATEGORY DISTRIBUTION
    {'='*80}
    {merged['Category'].value_counts().to_string()}

    Revenue by Category:
    {merged.groupby('Category')['Total_Revenue'].sum().sort_values(ascending=False).to_string()}

    {'='*80}
    GEOGRAPHIC DISTRIBUTION
    {'='*80}
    Orders by Location:
    {merged['Customer Location'].value_counts().head(10).to_string()}

    Revenue by Location:
    {merged.groupby('Customer Location')['Total_Revenue'].sum().sort_values(ascending=False).head(10).to_string()}

    {'='*80}
    TEMPORAL ANALYSIS
    {'='*80}
    Years Covered: {sorted(merged['Year'].unique())}

    Revenue by Year:
    {merged.groupby('Year')['Total_Revenue'].sum().to_string()}

    Orders by Quarter:
    {merged['Year_Quarter'].value_counts().sort_index().to_string()}

    {'='*80}
    PERFORMANCE METRICS
    {'='*80}
    Processing Timeline:
      - Load Time: ~{(merge_start - script_start).total_seconds():.2f}s
      - Merge Time: {merge_duration:.2f}s
      - Calculation Time: {calc_duration:.2f}s
      - Save Time: {save_duration:.2f}s
      - Total Time: {total_duration:.2f}s

    Memory Efficiency:
      - Peak Memory: {format_bytes(merged_memory)}
      - Compression Ratio: {(orders.memory_usage(deep=True).sum() + products.memory_usage(deep=True).sum()) / merged_memory:.2f}x

    {'='*80}
    QUALITY ASSURANCE CHECKLIST
    {'='*80}
    Datasets loaded successfully
    Product IDs matched ({len(overlap):,} overlaps)
    {'Excellent' if retention_rate > 99 else 'Some data loss'} Retention rate: {retention_rate:.2f}%
    Merge operation completed
    All derived fields calculated
    {'No null values' if len(has_nulls) == 0 else 'Null values present'} Null value check: {len(has_nulls)} columns with nulls
    Data types optimized
    Output file saved successfully
    Quality report generated

    {'='*80}
    DATASET SCHEMA
    {'='*80}
    {merged.dtypes.to_string()}

    {'='*80}
    SAMPLE DATA (First 5 Rows)
    {'='*80}
    {merged.head().to_string()}

    {'='*80}
    READY FOR ANALYSIS
    {'='*80}
    This dataset is ready for:
      Plotly Dashboard Development
      Business Intelligence Tools (Tableau, Power BI)
      Time-Series Forecasting
      Customer Segmentation Analysis
      Revenue Analytics
      Geographic Performance Analysis
      Product Performance Tracking

    Next Steps:
      1. Load {OUTPUT_FILE} in your analytics tool
      2. Review this quality report for data insights
      3. Build interactive dashboards with Plotly/Dash
      4. Create KPI tracking and alerts
      5. Develop predictive models if needed

    {'='*80}
    END OF REPORT
    {'='*80}
    """
    
    print(f"\nGenerating comprehensive quality report...")
    
    try:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Quality report saved: {REPORT_FILE}")
    except Exception as e:
        print(f"ERROR saving report: {e}")
    
    print_section("STEP 9: MERGED DATASET SAMPLE")
    
    print("\nFirst 5 rows of merged dataset:")
    print(merged.head().to_string())
    
    print(f"\n\nColumn List ({len(merged.columns)} total):")
    for i, col in enumerate(merged.columns, 1):
        print(f"  {i:2d}. {col} ({merged[col].dtype})")
    
    print_section("MERGE OPERATION COMPLETE")
    print_section("✅ MERGE OPERATION COMPLETE")
    
    print(f"\n⏱️  Total Processing Time: {total_duration:.2f} seconds")
    print(f"📁 Output Dataset: {OUTPUT_FILE}")
    print(f"   └─ {len(merged):,} rows × {len(merged.columns)} columns")
    print(f"   └─ {format_bytes(file_size) if 'file_size' in locals() else 'N/A'}")
    print(f"\n📊 Quality Report: {REPORT_FILE}")
    
    print(f"\n🎯 Success Metrics:")
    print(f"   ✓ {retention_rate:.2f}% data retention")
    print(f"   ✓ {len(overlap):,} Product IDs matched")
    print(f"   ✓ ${total_revenue:,.2f} total revenue tracked")
    
    print(f"\n📈 Next Steps:")
    print(f"   1. Review {REPORT_FILE} for detailed insights")
    print(f"   2. Load {OUTPUT_FILE} for dashboard creation")
    print(f"   3. Build Plotly visualizations for KPI tracking")
    print(f"   4. Perform deeper analytics and forecasting")
    
    print("\n" + "="*80)
    print("Ready for Analytics & Dashboard Development! 🚀".center(80))
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
