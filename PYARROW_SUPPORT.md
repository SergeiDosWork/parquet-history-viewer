# PyArrow Format Support in Trading History Viewer

## Overview
The Trading History Viewer application provides robust support for reading Parquet files created with PyArrow. The application handles various PyArrow formats, compression methods, and column naming conventions.

## Supported PyArrow Features

### File Formats
- **Standard Parquet**: Default Apache Parquet format
- **Compression Methods**: 
  - Snappy (default)
  - GZIP
  - Brotli
  - Uncompressed

### Column Name Variations
The application supports flexible column naming to accommodate different data sources:

| Standard Name | Alternative Names |
|---------------|-------------------|
| `timestamp` | `time`, `date`, `datetime`, `dt` |
| `open` | `open_price`, `openprice` |
| `high` | `high_price`, `highprice` |
| `low` | `low_price`, `lowprice` |
| `close` | `close_price`, `closeprice` |
| `volume` | `vol`, `amount`, `qty`, `quantity` |

### Data Validation
- Automatic detection and removal of invalid OHLC data
- NaN value filtering in critical columns
- Data type validation and conversion
- Range validation to ensure logical consistency (e.g., high ≥ low, high ≥ open/close)

## Code Implementation Details

### Enhanced Loading Function
The `load_file()` method now includes:

1. **Robust Column Mapping**: Automatically maps alternative column names
2. **Data Type Validation**: Ensures timestamps are properly formatted
3. **Data Quality Checks**: Validates OHLC relationships
4. **Error Handling**: Provides detailed error messages for debugging

### PyArrow Integration
- Uses `pyarrow.parquet.read_table()` for optimal performance
- Converts to pandas DataFrame while preserving data types
- Handles metadata and schema information correctly

## Usage Examples

### Creating Compatible Files
```python
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

# Create your trading data
data = pd.DataFrame({
    'timestamp': pd.date_range('2023-01-01', periods=100, freq='1min'),
    'open': [100.0] * 100,
    'high': [105.0] * 100,
    'low': [95.0] * 100,
    'close': [102.0] * 100,
    'volume': [1000] * 100
})

# Write to parquet
table = pa.Table.from_pandas(data)
pq.write_table(table, 'trading_data.parquet')

# Or with specific compression
pq.write_table(table, 'trading_data.parquet', compression='snappy')
```

### Alternative Column Names
The application will automatically recognize and map these variations:
```python
# These column names will be mapped correctly:
data_with_alternatives = pd.DataFrame({
    'datetime': [...],      # maps to 'timestamp'
    'open_price': [...],    # maps to 'open'
    'high_price': [...],    # maps to 'high'
    'low_price': [...],     # maps to 'low'
    'close_price': [...],   # maps to 'close'
    'vol': [...]            # maps to 'volume'
})
```

## Performance Considerations

- PyArrow provides faster read/write operations compared to other formats
- Memory-efficient handling of large datasets
- Proper data type preservation reduces memory usage
- Optimized for time-series financial data

## Troubleshooting

### Common Issues
1. **Missing Columns**: Ensure your data contains at least the required columns (or their alternatives)
2. **Data Type Issues**: Timestamps should be datetime objects
3. **Invalid OHLC Data**: The application will warn and remove invalid price relationships

### Error Messages
- "Missing required columns": Check column names against supported variations
- "Invalid OHLC data was removed": Review your data for pricing inconsistencies
- "Error loading file": Check file format and permissions

## Testing
Run the test suite to verify PyArrow functionality:
```bash
python test_pyarrow_reader.py
```