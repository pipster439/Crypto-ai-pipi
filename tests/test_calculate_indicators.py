import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add project root to sys.path to allow importing project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculate_technical_indicators import calculate_all_indicators

class TestCalculateIndicators(unittest.TestCase):

    def setUp(self):
        # Sample OHLCV data (list of lists format) - Timestamp, Open, High, Low, Close, Volume
        self.sample_ohlcv_list = [
            [1672531200000, 16500.0, 16550.0, 16480.0, 16520.0, 1000.5],
            [1672534800000, 16520.0, 16560.0, 16510.0, 16540.0, 1200.2],
            [1672538400000, 16540.0, 16600.0, 16530.0, 16580.0, 1100.0],
            [1672542000000, 16580.0, 16620.0, 16570.0, 16590.0, 900.3],
            [1672545600000, 16590.0, 16700.0, 16580.0, 16650.0, 1500.7],
            [1672549200000, 16650.0, 16680.0, 16630.0, 16670.0, 800.1],
            [1672552800000, 16670.0, 16750.0, 16660.0, 16720.0, 1300.9],
            [1672556400000, 16720.0, 16730.0, 16680.0, 16700.0, 700.6],
            [1672560000000, 16700.0, 16780.0, 16690.0, 16770.0, 1400.4],
            [1672563600000, 16770.0, 16800.0, 16750.0, 16790.0, 1000.0],
            [1672567200000, 16790.0, 16850.0, 16780.0, 16830.0, 1600.2],
            [1672570800000, 16830.0, 16880.0, 16820.0, 16860.0, 1150.5],
            [1672574400000, 16860.0, 16900.0, 16850.0, 16890.0, 950.8],
            [1672578000000, 16890.0, 16950.0, 16880.0, 16930.0, 1250.3],
            [1672581600000, 16930.0, 16980.0, 16920.0, 16970.0, 1050.1],
            [1672585200000, 16970.0, 17000.0, 16950.0, 16990.0, 1350.6],
            [1672588800000, 16990.0, 17050.0, 16980.0, 17030.0, 1100.7],
            [1672592400000, 17030.0, 17080.0, 17020.0, 17060.0, 1450.9],
            [1672596000000, 17060.0, 17100.0, 17050.0, 17090.0, 1000.4],
            [1672599600000, 17090.0, 17150.0, 17080.0, 17130.0, 1700.0] # 20 data points
        ]

        # Sample OHLCV data (Pandas DataFrame format)
        self.sample_ohlcv_df = pd.DataFrame(
            self.sample_ohlcv_list,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        self.sample_ohlcv_df['timestamp'] = pd.to_datetime(self.sample_ohlcv_df['timestamp'], unit='ms')
        self.sample_ohlcv_df.set_index('timestamp', inplace=True)

        self.expected_indicator_cols = [
            'RSI_14', 'MACD_12_26_9', 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'SMA_10', 'EMA_10'
        ] # A subset of expected columns

    def test_calculate_with_valid_list_data(self):
        df_indicators = calculate_all_indicators(self.sample_ohlcv_list)
        self.assertIsInstance(df_indicators, pd.DataFrame)
        self.assertFalse(df_indicators.empty)
        for col in self.expected_indicator_cols:
            self.assertIn(col, df_indicators.columns)
        # Check that not all values for a key indicator are NaN (assuming enough data)
        self.assertFalse(df_indicators['RSI_14'].isnull().all(), "RSI_14 should not be all NaN")

    def test_calculate_with_valid_dataframe_data(self):
        df_indicators = calculate_all_indicators(self.sample_ohlcv_df.copy()) # Pass a copy
        self.assertIsInstance(df_indicators, pd.DataFrame)
        self.assertFalse(df_indicators.empty)
        for col in self.expected_indicator_cols:
            self.assertIn(col, df_indicators.columns)
        self.assertFalse(df_indicators['SMA_10'].isnull().all(), "SMA_10 should not be all NaN")

    def test_insufficient_data_list(self):
        # Test with too few rows (e.g., 5 rows, many indicators need more)
        insufficient_data = self.sample_ohlcv_list[:5]
        with self.assertLogs(level='WARNING') as log: # Check for print warning
             df_indicators = calculate_all_indicators(insufficient_data)
             self.assertTrue(any("Warning: DataFrame has only 5 rows." in message for message in log.output))
        self.assertIsInstance(df_indicators, pd.DataFrame)
        # Some indicators might be all NaN, this is expected with too little data
        # For example, SMA_10 will be all NaN if less than 10 data points
        self.assertTrue(df_indicators['SMA_10'].isnull().all(), "SMA_10 should be all NaN with 5 data points")


    def test_insufficient_data_df(self):
        insufficient_df = self.sample_ohlcv_df.iloc[:5].copy()
        with self.assertLogs(level='WARNING') as log:
            df_indicators = calculate_all_indicators(insufficient_df)
            self.assertTrue(any("Warning: DataFrame has only 5 rows." in message for message in log.output))
        self.assertIsInstance(df_indicators, pd.DataFrame)
        self.assertTrue(df_indicators['EMA_10'].isnull().all(), "EMA_10 should be all NaN with 5 data points")


    def test_invalid_input_format_non_list_df(self):
        with self.assertLogs(level='ERROR') as log: # Check for print error
            result = calculate_all_indicators("not a list or df")
            self.assertTrue(any("Error: ohlcv_data must be a list of lists or a pandas DataFrame." in message for message in log.output))
        self.assertIsNone(result)

    def test_invalid_input_format_list_wrong_elements(self):
        invalid_list_data = [[1, 2, 3], [4, 5, 6]] # Incorrect number of elements
        with self.assertLogs(level='ERROR') as log:
            result = calculate_all_indicators(invalid_list_data)
            self.assertTrue(any("Error: If ohlcv_data is a list, each inner list must have 6 elements" in message for message in log.output))
        self.assertIsNone(result)

    def test_empty_input_list(self):
        with self.assertLogs(level='ERROR') as log:
            result = calculate_all_indicators([])
            self.assertTrue(any("Error: OHLCV data is empty." in message for message in log.output))
        self.assertIsNone(result)

    def test_empty_input_df(self):
        empty_df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        empty_df.set_index('timestamp', inplace=True)
        # The function expects data, so an empty df will likely lead to errors within pandas_ta or earlier checks.
        # Current implementation, an empty DF will pass the initial check but fail in pandas_ta or length checks.
        # Let's assume it should return None or an empty DF with warnings.
        with self.assertLogs(level='WARNING') as log: # Expecting a warning about length
            df_indicators = calculate_all_indicators(empty_df)
            self.assertTrue(any("Warning: DataFrame has only 0 rows." in message for message in log.output))
        # The strategy might still be applied to an empty frame, resulting in an empty frame with columns
        self.assertIsInstance(df_indicators, pd.DataFrame)
        self.assertTrue(df_indicators.empty) # Or check if columns are added but all rows are NaN

    def test_ohlcv_columns_mapping(self):
        # Create a DataFrame with custom column names
        custom_df = pd.DataFrame(
            self.sample_ohlcv_list,
            columns=['time', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'VolumeQty']
        )
        custom_df['time'] = pd.to_datetime(custom_df['time'], unit='ms')
        custom_df.set_index('time', inplace=True)
        
        ohlcv_columns_map = {
            "open": "OpenPrice", 
            "high": "HighPrice", 
            "low": "LowPrice", 
            "close": "ClosePrice", 
            "volume": "VolumeQty"
        }
        df_indicators = calculate_all_indicators(custom_df.copy(), ohlcv_columns=ohlcv_columns_map)
        self.assertIsInstance(df_indicators, pd.DataFrame)
        self.assertFalse(df_indicators.empty)
        for col in self.expected_indicator_cols:
            self.assertIn(col, df_indicators.columns)
        self.assertFalse(df_indicators['RSI_14'].isnull().all())

    def test_numeric_conversion_and_nans(self):
        # Data with some non-numeric values that should be coerced to NaN
        mixed_data_list = [
            [1672531200000, "16500.0", 16550.0, 16480.0, 16520.0, 1000.5],
            [1672534800000, 16520.0, "invalid", 16510.0, 16540.0, 1200.2], # 'invalid' high
            [1672538400000, 16540.0, 16600.0, 16530.0, 16580.0, "1100.0"]
        ] * 7 # Make it 21 rows to ensure enough data for most indicators
        
        with self.assertLogs(level='WARNING') as log: # Expect warning about NaNs
            df_indicators = calculate_all_indicators(mixed_data_list)
            self.assertTrue(any("Warning: NaN values found in OHLCV data after conversion." in message for message in log.output))
        
        self.assertIsInstance(df_indicators, pd.DataFrame)
        # Check if 'high' column has NaNs after coercion
        self.assertTrue(df_indicators['high'].isnull().any())
        # Indicators should still be calculated for valid parts, or handle NaNs gracefully
        self.assertIn('RSI_14', df_indicators.columns)


if __name__ == '__main__':
    unittest.main()
