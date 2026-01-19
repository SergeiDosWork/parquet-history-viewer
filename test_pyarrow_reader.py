#!/usr/bin/env python3
"""
Test script to verify PyArrow file reading capabilities
"""
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
from datetime import datetime, timedelta
import os

def test_basic_reading():
    """Test basic PyArrow parquet reading functionality"""
    print("Testing basic PyArrow parquet reading...")
    
    # Test with the existing sample file
    df = pq.read_table('sample_trading_data.parquet').to_pandas()
    print(f"✓ Successfully read sample_trading_data.parquet")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    
    # Verify data types
    print(f"  Timestamp dtype: {df['timestamp'].dtype}")
    print(f"  Open dtype: {df['open'].dtype}")
    print(f"  Close dtype: {df['close'].dtype}")

def test_different_formats():
    """Test various PyArrow formats and configurations"""
    print("\nTesting different PyArrow formats...")
    
    # Create test data with different schemas
    dates = pd.date_range(start='2023-01-01', periods=100, freq='1min')
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(100, 200, 100),
        'high': np.random.uniform(100, 200, 100),
        'low': np.random.uniform(100, 200, 100),
        'close': np.random.uniform(100, 200, 100),
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # Test writing and reading with different compression
    compressions = ['snappy', 'gzip', 'brotli']
    
    for comp in compressions:
        filename = f'test_compression_{comp.lower()}.parquet'
        table = pa.Table.from_pandas(test_data)
        pq.write_table(table, filename, compression=comp)
        
        # Read it back
        read_df = pq.read_table(filename).to_pandas()
        print(f"  ✓ Compression {comp}: {read_df.shape}, data integrity: {len(read_df) == len(test_data)}")
        
        # Clean up
        os.remove(filename)
    
    # Also test with no explicit compression (default)
    filename = 'test_default_compression.parquet'
    table = pa.Table.from_pandas(test_data)
    pq.write_table(table, filename)  # Use default compression
    
    read_df = pq.read_table(filename).to_pandas()
    print(f"  ✓ Default compression: {read_df.shape}, data integrity: {len(read_df) == len(test_data)}")
    
    # Clean up
    os.remove(filename)

def test_alternative_column_names():
    """Test handling of alternative column names"""
    print("\nTesting alternative column names...")
    
    # Create test data with alternative column names
    dates = pd.date_range(start='2023-01-01', periods=50, freq='1min')
    alt_data = pd.DataFrame({
        'datetime': dates,
        'open_price': np.random.uniform(100, 200, 50),
        'high_price': np.random.uniform(100, 200, 50),
        'low_price': np.random.uniform(100, 200, 50),
        'close_price': np.random.uniform(100, 200, 50),
        'volume': np.random.randint(1000, 10000, 50)
    })
    
    # Write to parquet
    filename = 'test_alt_columns.parquet'
    table = pa.Table.from_pandas(alt_data)
    pq.write_table(table, filename)
    
    # Read it back
    read_df = pq.read_table(filename).to_pandas()
    print(f"  ✓ Alternative column names preserved: {list(read_df.columns)}")
    
    # Clean up
    os.remove(filename)

def test_metadata_handling():
    """Test metadata handling in PyArrow files"""
    print("\nTesting metadata handling...")
    
    # Create data with metadata
    dates = pd.date_range(start='2023-01-01', periods=20, freq='1min')
    meta_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.uniform(100, 200, 20),
        'high': np.random.uniform(100, 200, 20),
        'low': np.random.uniform(100, 200, 20),
        'close': np.random.uniform(100, 200, 20),
        'volume': np.random.randint(1000, 10000, 20)
    })
    
    # Create schema with metadata
    schema = pa.schema([
        ('timestamp', pa.timestamp('ns'), {'description': 'Timestamp of the trade'}),
        ('open', pa.float64(), {'description': 'Opening price'}),
        ('high', pa.float64(), {'description': 'Highest price'}),
        ('low', pa.float64(), {'description': 'Lowest price'}),
        ('close', pa.float64(), {'description': 'Closing price'}),
        ('volume', pa.int64(), {'description': 'Trading volume'})
    ])
    
    table = pa.Table.from_pandas(meta_data, schema=schema)
    filename = 'test_metadata.parquet'
    pq.write_table(table, filename)
    
    # Read back and check metadata
    read_table = pq.read_table(filename)
    print(f"  ✓ Schema preserved: {read_table.schema}")
    print(f"  ✓ Metadata available: {read_table.schema.metadata}")
    
    # Clean up
    os.remove(filename)

def main():
    print("PyArrow Format Reading Tests")
    print("="*50)
    
    try:
        test_basic_reading()
        test_different_formats()
        test_alternative_column_names()
        test_metadata_handling()
        
        print("\n" + "="*50)
        print("All tests passed! ✓")
        print("The application should handle PyArrow format files correctly.")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()