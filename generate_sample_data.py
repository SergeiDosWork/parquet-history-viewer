import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pyarrow as pa
import pyarrow.parquet as pq

def generate_sample_trading_data(start_date='2023-01-01', num_records=1000, symbol='AAPL'):
    """
    Generate sample trading data with OHLCV values
    """
    dates = pd.date_range(start=start_date, periods=num_records, freq='1min')
    
    # Starting price
    base_price = 150.0
    
    # Generate price movements
    np.random.seed(42)  # For reproducible results
    returns = np.random.normal(0.0001, 0.02, num_records)  # Daily return with small drift
    
    # Calculate prices based on returns
    prices = [base_price]
    for r in returns[1:]:
        new_price = prices[-1] * (1 + r)
        prices.append(new_price)
    
    # Add some volatility to make it more realistic
    prices = np.array(prices)
    
    # Generate OHLC data with some variation
    open_prices = prices
    high_prices = open_prices + np.abs(np.random.normal(0, 2, len(prices)))  # Random high values
    low_prices = open_prices - np.abs(np.random.normal(0, 2, len(prices)))   # Random low values
    
    # Ensure close prices are within high/low bounds
    close_prices = np.clip(prices, low_prices, high_prices)
    
    # Update high and low if needed
    high_prices = np.maximum(high_prices, np.maximum(open_prices, close_prices))
    low_prices = np.minimum(low_prices, np.minimum(open_prices, close_prices))
    
    # Generate volume data
    volumes = np.random.randint(1000, 10000, len(dates))
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'symbol': symbol,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    
    return df

def save_to_parquet(df, filename):
    """
    Save DataFrame to Parquet file
    """
    table = pa.Table.from_pandas(df)
    pq.write_table(table, filename)
    print(f"Saved {len(df)} records to {filename}")

if __name__ == "__main__":
    # Generate sample data
    print("Generating sample trading data...")
    sample_data = generate_sample_trading_data(num_records=5000)
    
    # Save to parquet file
    save_to_parquet(sample_data, 'sample_trading_data.parquet')
    
    print("\nSample data preview:")
    print(sample_data.head(10))
    
    print(f"\nData shape: {sample_data.shape}")
    print(f"Date range: {sample_data['timestamp'].min()} to {sample_data['timestamp'].max()}")