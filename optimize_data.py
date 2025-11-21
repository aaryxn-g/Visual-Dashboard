import pandas as pd
from datetime import datetime

def print_memory_usage(df, df_name):
    mem = df.memory_usage(deep=True).sum() / (1024 * 1024)
    print(f"{df_name} memory usage: {mem:.2f} MB")

def optimize_dataframe(df):
    print("\nStarting optimization...")
    
    df_opt = df.copy()
    
    print("\n1. Removing redundant columns...")
    columns_to_drop = [
        'Tax_Amount',
        'Total_Shipping_Revenue',
        'Quarter', 
        'Day_of_Week', 
        'Date_Week', 
        'Year_Month', 
        'Year_Quarter',
        'Price_Segment'
    ]
    
    columns_to_drop = [col for col in columns_to_drop if col in df_opt.columns]
    df_opt = df_opt.drop(columns=columns_to_drop)
    print(f"   Removed {len(columns_to_drop)} columns")
    
    numeric_cols = df_opt.select_dtypes(include=['int', 'float']).columns
    for col in numeric_cols:
        if df_opt[col].dtype == 'float64':
            df_opt[col] = pd.to_numeric(df_opt[col], downcast='float')
            print(f"   Converted {col} from float64 to {df_opt[col].dtype}")
        elif df_opt[col].dtype in ['int32', 'int64']:
            df_opt[col] = pd.to_numeric(df_opt[col], downcast='integer')
            print(f"   Converted {col} from {df[col].dtype} to {df_opt[col].dtype}")
    
    for col in df_opt.select_dtypes(include=['object']).columns:
        num_unique = df_opt[col].nunique()
        if num_unique / len(df_opt) < 0.5:
            df_opt[col] = df_opt[col].astype('category')
            print(f"   Converted {col} to category with {num_unique} unique values")
    
    return df_opt

def main():
    print("="*80)
    print("DATASET OPTIMIZATION TOOL")
    print("="*80)
    
    input_file = 'merged_order_product_details.csv'
    output_file = 'optimized_merged_data.csv'
    
    try:
        print(f"\nLoading data from {input_file}...")
        start_time = datetime.now()
        df = pd.read_csv(input_file)
        load_time = (datetime.now() - start_time).total_seconds()
        print(f"   Loaded {len(df):,} rows and {len(df.columns)} columns in {load_time:.2f} seconds")
        print_memory_usage(df, "Original data")
        
        df_optimized = optimize_dataframe(df)
        
        print(f"\nSaving optimized data to {output_file}...")
        start_time = datetime.now()
        df_optimized.to_csv(output_file, index=False)
        save_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "="*50)
        print("OPTIMIZATION SUMMARY")
        print("="*50)
        print(f"Original dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns")
        print(f"New dimensions:      {df_optimized.shape[0]:,} rows × {df_optimized.shape[1]} columns")
        
        original_size = df.memory_usage(deep=True).sum() / (1024 * 1024)
        optimized_size = df_optimized.memory_usage(deep=True).sum() / (1024 * 1024)
        print(f"\nOriginal size: {original_size:.2f} MB")
        print(f"Optimized size: {optimized_size:.2f} MB")
        print(f"Reduction: {(1 - optimized_size/original_size)*100:.1f}%")
        
        import os
        original_file_size = os.path.getsize(input_file) / (1024 * 1024)
        optimized_file_size = os.path.getsize(output_file) / (1024 * 1024)
        print(f"\nOriginal file size: {original_file_size:.2f} MB")
        print(f"Optimized file size: {optimized_file_size:.2f} MB")
        print(f"File size reduction: {(1 - optimized_file_size/original_file_size)*100:.1f}%")
        
        print(f"\nOptimization completed in {(datetime.now() - start_time).total_seconds():.2f} seconds")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
