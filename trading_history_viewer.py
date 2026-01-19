import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QComboBox, QSlider, 
                             QGraphicsView, QGraphicsScene, QGraphicsRectItem)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QColor, QPainter
import pyarrow.parquet as pq


class TradingHistoryViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize data and settings
        self.data = None
        self.filtered_data = None
        self.current_timeframe = '1min'
        self.start_index = 0
        self.visible_count = 100
        self.scale_factor = 1.0
        
        # Set up the main window
        self.setWindowTitle("Trading History Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar_layout = QHBoxLayout()
        
        # File selection
        self.file_label = QLabel("No file selected")
        toolbar_layout.addWidget(self.file_label)
        
        self.load_button = QPushButton("Load Parquet File")
        self.load_button.clicked.connect(self.load_file)
        toolbar_layout.addWidget(self.load_button)
        
        # Timeframe selector
        toolbar_layout.addWidget(QLabel("Timeframe:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1min', '3min', '5min', '15min', '30min', '1H', '4H', '1D'])
        self.timeframe_combo.currentTextChanged.connect(self.change_timeframe)
        toolbar_layout.addWidget(self.timeframe_combo)
        
        main_layout.addLayout(toolbar_layout)
        
        # Create graphics view for visualization
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        main_layout.addWidget(self.view)
        
        # Add controls
        controls_layout = QHBoxLayout()
        
        # Zoom controls
        controls_layout.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)  # 10%
        self.zoom_slider.setMaximum(500)  # 500%
        self.zoom_slider.setValue(100)  # 100% (normal size)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        controls_layout.addWidget(self.zoom_slider)
        
        # Panning controls
        self.pan_left_btn = QPushButton("<<")
        self.pan_left_btn.clicked.connect(self.pan_left)
        controls_layout.addWidget(self.pan_left_btn)
        
        self.pan_right_btn = QPushButton(">>")
        self.pan_right_btn.clicked.connect(self.pan_right)
        controls_layout.addWidget(self.pan_right_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def load_file(self):
        """Load a parquet file containing trading history"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Trading History File", "", "Parquet Files (*.parquet);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load the parquet file using PyArrow
                table = pq.read_table(file_path)
                self.data = table.to_pandas()
                
                # Ensure required columns exist
                required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                missing_cols = [col for col in required_cols if col not in self.data.columns]
                
                # Check for alternative column names that might be used
                if missing_cols:
                    # Try to map common alternative names
                    column_mapping = {}
                    
                    # Look for possible timestamp alternatives
                    timestamp_alts = ['time', 'date', 'datetime', 'dt']
                    for alt in timestamp_alts:
                        if alt in self.data.columns:
                            column_mapping[alt] = 'timestamp'
                            missing_cols.remove('timestamp')
                            break
                    
                    # Look for price alternatives
                    price_mappings = {
                        'open': ['open_price', 'openprice'],
                        'high': ['high_price', 'highprice'],
                        'low': ['low_price', 'lowprice'],
                        'close': ['close_price', 'closeprice'],
                        'volume': ['vol', 'amount', 'qty', 'quantity', 'tick_volume']
                    }
                    
                    for req_col, alts in price_mappings.items():
                        if req_col in missing_cols:
                            for alt in alts:
                                if alt in self.data.columns:
                                    column_mapping[alt] = req_col
                                    missing_cols.remove(req_col)
                                    break
                
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}. "
                                   f"Available columns: {list(self.data.columns)}")
                
                # Rename columns if needed
                if column_mapping:
                    self.data = self.data.rename(columns=column_mapping)
                
                # Ensure timestamp is datetime type
                if not pd.api.types.is_datetime64_any_dtype(self.data['timestamp']):
                    self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
                
                # Sort by timestamp
                self.data = self.data.sort_values('timestamp').reset_index(drop=True)
                
                # Remove any rows with NaN values in critical columns
                self.data = self.data.dropna(subset=['open', 'high', 'low', 'close', 'volume'])
                
                # Validate data ranges
                invalid_data = (
                    (self.data['high'] < self.data['low']) |
                    (self.data['high'] < self.data['open']) |
                    (self.data['high'] < self.data['close']) |
                    (self.data['low'] > self.data['open']) |
                    (self.data['low'] > self.data['close'])
                )
                if invalid_data.any():
                    self.data = self.data[~invalid_data]
                    self.status_bar.showMessage("Warning: Invalid OHLC data was removed")
                
                # Update UI
                self.file_label.setText(f"File: {file_path.split('/')[-1]} ({len(self.data)} records)")
                self.status_bar.showMessage(f"Loaded {len(self.data)} records from {file_path} successfully")
                
                # Apply initial timeframe filter
                self.apply_timeframe_filter()
                self.draw_chart()
                
            except Exception as e:
                self.status_bar.showMessage(f"Error loading file: {str(e)}")
                print(f"Detailed error: {e}")  # For debugging

    def apply_timeframe_filter(self):
        """Apply the selected timeframe to the data"""
        if self.data is None:
            return
            
        # Resample data based on selected timeframe
        resampled_data = self.data.set_index('timestamp').resample(self.get_pandas_freq()).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna().reset_index()
        
        self.filtered_data = resampled_data
        self.start_index = max(0, len(self.filtered_data) - self.visible_count)
        self.draw_chart()

    def get_pandas_freq(self):
        """Convert our timeframe to pandas frequency string"""
        freq_map = {
            '1min': '1T',
            '3min': '3T',
            '5min': '5T',
            '15min': '15T',
            '30min': '30T',
            '1H': '1H',
            '4H': '4H',
            '1D': '1D'
        }
        return freq_map.get(self.current_timeframe, '1T')

    def change_timeframe(self, timeframe):
        """Handle timeframe change"""
        self.current_timeframe = timeframe
        self.apply_timeframe_filter()

    def zoom_changed(self, value):
        """Handle zoom level changes"""
        self.scale_factor = value / 100.0  # Convert slider value to scale factor
        self.draw_chart()

    def pan_left(self):
        """Pan view left"""
        if self.filtered_data is not None:
            self.start_index = max(0, self.start_index - int(self.visible_count * 0.1))
            self.draw_chart()

    def pan_right(self):
        """Pan view right"""
        if self.filtered_data is not None:
            max_start = max(0, len(self.filtered_data) - self.visible_count)
            self.start_index = min(max_start, self.start_index + int(self.visible_count * 0.1))
            self.draw_chart()

    def draw_chart(self):
        """Draw the trading chart with bars"""
        self.scene.clear()
        
        if self.filtered_data is None or len(self.filtered_data) == 0:
            return

        # Calculate visible data range
        end_index = min(len(self.filtered_data), self.start_index + self.visible_count)
        visible_data = self.filtered_data.iloc[self.start_index:end_index]

        if len(visible_data) == 0:
            return

        # Determine price range for scaling
        min_price = visible_data[['low', 'high']].min().min()
        max_price = visible_data[['low', 'high']].max().max()
        price_range = max_price - min_price
        if price_range == 0:
            price_range = 1  # Prevent division by zero

        # Calculate dimensions
        scene_width = len(visible_data) * 20 * self.scale_factor
        scene_height = 600
        self.scene.setSceneRect(0, 0, scene_width, scene_height)

        # Draw each candlestick
        bar_width = 15 * self.scale_factor
        for i, (_, row) in enumerate(visible_data.iterrows()):
            x_pos = i * 20 * self.scale_factor
            
            # Calculate positions based on prices
            open_y = scene_height - ((row['open'] - min_price) / price_range) * scene_height
            close_y = scene_height - ((row['close'] - min_price) / price_range) * scene_height
            high_y = scene_height - ((row['high'] - min_price) / price_range) * scene_height
            low_y = scene_height - ((row['low'] - min_price) / price_range) * scene_height
            
            # Determine color (green for up, red for down)
            is_up = row['close'] >= row['open']
            color = QColor(0, 200, 0) if is_up else QColor(200, 0, 0)  # Green/red
            
            # Draw high-low line (wick)
            wick_pen = QColor(100, 100, 100)
            self.scene.addLine(x_pos + bar_width/2, high_y, x_pos + bar_width/2, low_y, wick_pen)
            
            # Draw open-close rectangle (body)
            body_top = min(open_y, close_y)
            body_height = abs(close_y - open_y)
            if body_height < 1:  # Minimum height for visibility
                body_height = 1
                
            rect = QRectF(x_pos, body_top, bar_width, body_height)
            brush = QBrush(color)
            self.scene.addRect(rect, color, brush)


def main():
    app = QApplication(sys.argv)
    viewer = TradingHistoryViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()