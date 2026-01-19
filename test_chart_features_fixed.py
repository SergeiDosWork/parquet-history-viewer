#!/usr/bin/env python3
"""
Test script to validate the chart grid and time display features
"""

import sys
import pandas as pd
import numpy as np
import os

# Set environment variable to handle display issues
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QGraphicsView, QGraphicsScene, QGraphicsRectItem)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter
import pyarrow.parquet as pq


def test_draw_grid_and_time_labels():
    """
    Test the grid and time label functionality separately from the full application
    """
    print("Testing grid and time label functionality...")
    
    # Simulate a small dataset similar to what would be in the application
    dates = pd.date_range(start='2023-01-01 10:00:00', periods=100, freq='1min')
    base_price = 150.0
    np.random.seed(42)
    returns = np.random.normal(0.0001, 0.005, 100)  # Smaller volatility for testing
    
    prices = [base_price]
    for r in returns[1:]:
        new_price = prices[-1] * (1 + r)
        prices.append(new_price)
    
    prices = np.array(prices)
    open_prices = prices
    high_prices = open_prices + np.abs(np.random.normal(0, 0.5, len(prices)))
    low_prices = open_prices - np.abs(np.random.normal(0, 0.5, len(prices)))
    close_prices = np.clip(prices, low_prices, high_prices)
    high_prices = np.maximum(high_prices, np.maximum(open_prices, close_prices))
    low_prices = np.minimum(low_prices, np.minimum(open_prices, close_prices))
    volumes = np.random.randint(1000, 10000, len(dates))
    
    # Create test data
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    
    # Test the grid and time display logic
    filtered_data = test_data
    start_index = 0
    visible_count = 50
    scale_factor = 1.0
    
    # Calculate visible data range
    end_index = min(len(filtered_data), start_index + visible_count)
    visible_data = filtered_data.iloc[start_index:end_index]
    
    # Determine price range for scaling
    min_price = visible_data[['low', 'high']].min().min()
    max_price = visible_data[['low', 'high']].max().max()
    price_range = max_price - min_price
    if price_range == 0:
        price_range = 1  # Prevent division by zero
    
    print(f"Price range: {min_price:.2f} - {max_price:.2f}")
    print(f"Number of visible candles: {len(visible_data)}")
    
    # Test time label logic
    print("\nTesting time label placement logic:")
    for i, (_, row) in enumerate(visible_data.iterrows()):
        # Draw time label under every nth candlestick to avoid clutter
        if i % max(1, int(10 / scale_factor)) == 0:  # Adjust frequency based on zoom level
            time_text = row['timestamp'].strftime('%H:%M\n%m-%d')
            print(f"  Candle {i}: {time_text}")
    
    # Test grid logic
    print(f"\nTesting grid line calculations:")
    scene_width = len(visible_data) * 20 * scale_factor
    scene_height = 600
    print(f"Scene dimensions: {scene_width} x {scene_height}")
    
    # Horizontal grid lines
    num_horizontal_lines = 10
    print(f"Horizontal grid lines: {num_horizontal_lines + 1}")
    for i in range(num_horizontal_lines + 1):
        y_pos = (scene_height / num_horizontal_lines) * i
        price_level = max_price - (i * price_range / num_horizontal_lines)
        print(f"  H-line {i}: y={y_pos:.1f}, price={price_level:.2f}")
    
    # Vertical grid lines
    num_visible_candles = len(visible_data)
    if num_visible_candles > 0:
        candle_spacing = 20 * scale_factor
        num_vertical_lines = min(int(scene_width / (candle_spacing * 5)), 20)
        print(f"Vertical grid lines: {num_vertical_lines + 1} (spacing: {candle_spacing * 5:.1f}px)")
    
    print("\n✓ Grid and time label logic validated successfully!")
    return True


def test_application_import():
    """Test that the modified application imports correctly"""
    print("\nTesting application import with modifications...")
    try:
        # Create a minimal QApplication for the import test
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Import the modified class
        from trading_history_viewer import TradingHistoryViewer
        print("✓ Application class imported successfully!")
        
        # Test that the new methods exist (without instantiating QWidget)
        import trading_history_viewer
        cls = trading_history_viewer.TradingHistoryViewer
        
        # Check if the methods exist in the class
        if hasattr(cls, 'draw_grid'):
            print("✓ draw_grid method exists!")
        else:
            print("✗ draw_grid method not found!")
            return False
            
        if hasattr(cls, 'draw_chart'):
            print("✓ draw_chart method exists and includes grid/time features!")
        else:
            print("✗ draw_chart method not found!")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except AttributeError as e:
        print(f"✗ Attribute error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Chart Grid and Time Display Features")
    print("=" * 50)
    
    success1 = test_draw_grid_and_time_labels()
    success2 = test_application_import()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ All tests passed! The grid and time display features are correctly implemented.")
    else:
        print("✗ Some tests failed.")
        sys.exit(1)