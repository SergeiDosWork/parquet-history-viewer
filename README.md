# Trading History Viewer

A desktop application written in Python that allows viewing trading history stored in Parquet format with interactive features.

## Features

- Load trading history from Parquet files
- Visualize price data as candlestick charts
- Color-coded bars (green for bullish, red for bearish)
- Interactive panning (move the visible window)
- Zoom functionality
- Multiple timeframe selection (1min, 5min, 15min, 30min, 1H, 4H, 1D)

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
3. The file must contain the following columns:
   - `timestamp`: Date/time of the record
   - `open`: Opening price
   - `high`: Highest price
   - `low`: Lowest price
   - `close`: Closing price
   - `volume`: Trading volume

4. Use the controls to:
   - Change timeframe with the dropdown
   - Zoom in/out using the slider
   - Pan left/right using the arrow buttons

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
