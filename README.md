# Trading History Viewer

A desktop application written in Python that allows viewing trading history stored in Parquet format with interactive features.

## Features

- Load trading history from Parquet files with robust PyArrow support
- Visualize price data as candlestick charts
- Color-coded bars (green for bullish, red for bearish)
- Interactive panning (move the visible window)
- Zoom functionality
- Multiple timeframe selection (1min, 5min, 15min, 30min, 1H, 4H, 1D)
- Flexible column name support (automatically maps common variations)
- Data validation and quality checks

## Requirements

- Python 3.7+
- pandas
- pyarrow
- PyQt5
- numpy

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python trading_history_viewer.py
```

2. Click "Load Parquet File" to select your trading history file
3. The file must contain the following columns (alternative names are supported):
   - `timestamp`: Date/time of the record (also accepts: `time`, `date`, `datetime`, `dt`)
   - `open`: Opening price (also accepts: `open_price`, `openprice`)
   - `high`: Highest price (also accepts: `high_price`, `highprice`)
   - `low`: Lowest price (also accepts: `low_price`, `lowprice`)
   - `close`: Closing price (also accepts: `close_price`, `closeprice`)
   - `volume`: Trading volume (also accepts: `vol`, `amount`, `qty`, `quantity`)

4. Use the controls to:
   - Change timeframe with the dropdown
   - Zoom in/out using the slider
   - Pan left/right using the arrow buttons

## File Format Support

The application provides comprehensive support for various PyArrow formats:
- Different compression methods (Snappy, GZIP, Brotli)
- Flexible column naming conventions
- Automatic data validation and cleaning
- Metadata preservation

For more details on PyArrow format support, see [PYARROW_SUPPORT.md](PYARROW_SUPPORT.md).

## Sample Data

The repository includes a script to generate sample trading data:

```bash
python generate_sample_data.py
```

This creates a file named `sample_trading_data.parquet` with 5000 minutes of simulated trading data that you can use to test the application.

## File Structure

- `trading_history_viewer.py`: Main application code
- `generate_sample_data.py`: Script to create sample data
- `requirements.txt`: Python dependencies
- `sample_trading_data.parquet`: Generated sample data file
- `PYARROW_SUPPORT.md`: Detailed documentation on PyArrow format support
