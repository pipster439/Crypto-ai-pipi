import pandas as pd
import pandas_ta as ta
import json
import os
import argparse
import sys

def calculate_all_indicators(ohlcv_data, ohlcv_columns=None):
    """
    Calculates a comprehensive set of technical indicators using pandas_ta.

    Args:
        ohlcv_data (list or pd.DataFrame): 
            If list: A list of lists, where each inner list is [timestamp, open, high, low, close, volume].
            If pd.DataFrame: A DataFrame with columns for open, high, low, close, volume (and optionally timestamp as index).
        ohlcv_columns (dict, optional):
            A dictionary mapping standard column names to actual column names in the input DataFrame if not standard.
            Example: {"open": "OpenPrice", "high": "HighPrice", "low": "LowPrice", "close": "ClosePrice", "volume": "Volume"}
            If ohlcv_data is a list, this is ignored and standard names ('open', 'high', 'low', 'close', 'volume') are assumed for the created DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the original OHLCV data and all calculated indicators.
                      Returns None if input data is insufficient or an error occurs.
    """
    if not ohlcv_data:
        print("Error: OHLCV data is empty.")
        return None

    if isinstance(ohlcv_data, list):
        if not all(isinstance(row, list) and len(row) == 6 for row in ohlcv_data):
            print("Error: If ohlcv_data is a list, each inner list must have 6 elements: [timestamp, open, high, low, close, volume]")
            return None
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        # Ensure numeric types for OHLCV columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    elif isinstance(ohlcv_data, pd.DataFrame):
        df = ohlcv_data.copy()
        if ohlcv_columns:
            df.rename(columns=ohlcv_columns, inplace=True)
        # Ensure standard column names exist
        required_cols = {'open', 'high', 'low', 'close', 'volume'}
        if not required_cols.issubset(df.columns):
            print(f"Error: DataFrame must contain columns: {required_cols}. Found: {df.columns}")
            return None
        # Ensure numeric types for OHLCV columns
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        print("Error: ohlcv_data must be a list of lists or a pandas DataFrame.")
        return None

    if df.isnull().any().any():
        print("Warning: NaN values found in OHLCV data after conversion. Attempting to proceed.")
        # df.dropna(inplace=True) # Optionally drop rows with NaNs, or let pandas_ta handle it

    if len(df) < 20: # Many indicators require a minimum number of periods
        print(f"Warning: DataFrame has only {len(df)} rows. Some indicators might not be calculated or be inaccurate.")

    # Create a custom strategy for pandas_ta
    # This allows calculating multiple indicators at once
    custom_strategy = ta.Strategy(
        name="Comprehensive Analysis",
        description="Calculates RSI, MACD, BBands, MAs, KDJ, OBV, MFI, AD, and more.",
        ta=[
            # Standard Indicators from user prompt
            {"kind": "rsi"}, # Relative Strength Index
            {"kind": "macd"}, # Moving Average Convergence Divergence
            {"kind": "bbands", "length": 20, "std": 2}, # Bollinger Bands
            {"kind": "sma", "length": 10, "col_names": ("SMA_10")}, # Simple Moving Average 10
            {"kind": "sma", "length": 20, "col_names": ("SMA_20")}, # Simple Moving Average 20
            {"kind": "sma", "length": 50, "col_names": ("SMA_50")}, # Simple Moving Average 50
            {"kind": "ema", "length": 10, "col_names": ("EMA_10")}, # Exponential Moving Average 10
            {"kind": "ema", "length": 20, "col_names": ("EMA_20")}, # Exponential Moving Average 20
            {"kind": "ema", "length": 50, "col_names": ("EMA_50")}, # Exponential Moving Average 50
            {"kind": "kdj"}, # KDJ Indicator
            {"kind": "obv"}, # On-Balance Volume
            {"kind": "mfi"}, # Money Flow Index
            {"kind": "ad"},  # Accumulation/Distribution Index (A/D Line)
            
            # Additional potentially useful indicators (can be expanded)
            {"kind": "atr"}, # Average True Range
            {"kind": "stoch"}, # Stochastic Oscillator
            {"kind": "mom"}, # Momentum
            {"kind": "roc"}, # Rate of Change
            {"kind": "ppo"}, # Percentage Price Oscillator
            {"kind": "cci"}, # Commodity Channel Index
            {"kind": "vwap"}, # Volume Weighted Average Price (requires typical price, pandas-ta handles it)
            {"kind": "cmf"}, # Chaikin Money Flow
            {"kind": "chop"}, # Chop Index
            {"kind": "psar"}, # Parabolic SAR
        ]
    )

    try:
        print("Calculating indicators...")
        df.ta.strategy(custom_strategy)
        print("Indicators calculated successfully.")
    except Exception as e:
        print(f"Error calculating indicators with pandas_ta: {e}")
        # Return the original DataFrame if strategy fails, or handle more gracefully
        return df # Or None, depending on desired error handling

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate technical indicators from OHLCV data.")
    parser.add_argument("--input_file", type=str, 
                        default=os.path.join(os.path.dirname(__file__), "fetched_market_data.json"),
                        help="Path to the input JSON file containing OHLCV data.")
    parser.add_argument("--output_file", type=str, 
                        default=os.path.join(os.path.dirname(__file__), "ohlcv_with_all_indicators.json"),
                        help="Path to save the JSON file with calculated indicators.")
    
    args = parser.parse_args()

    input_file_path = args.input_file
    output_file_path = args.output_file
    raw_ohlcv_data = []
    
    try:
        print(f"Loading data from: {input_file_path}")
        with open(input_file_path, 'r') as f:
            loaded_json = json.load(f)
            
            # Updated data extraction logic
            if isinstance(loaded_json, dict) and "ohlcv" in loaded_json and isinstance(loaded_json["ohlcv"], list):
                raw_ohlcv_data = loaded_json["ohlcv"]
                print(f"Successfully extracted 'ohlcv' data (found {len(raw_ohlcv_data)} records).")
                # Optional: print symbol and interval for context
                symbol = loaded_json.get("symbol", "N/A")
                interval = loaded_json.get("interval", "N/A")
                print(f"Data for symbol: {symbol}, interval: {interval}")
            elif isinstance(loaded_json, list): # Fallback for direct list of OHLCV data (old format or direct use)
                raw_ohlcv_data = loaded_json
                print("Loaded data as a direct list of OHLCV records.")
            else:
                print(f"Error: Could not find 'ohlcv' list in {input_file_path}, or format is unexpected.")
                # Fallback to a very basic mock data if file loading fails or is empty
                raw_ohlcv_data = [] # Will be handled by the mock data generation below
                
    except FileNotFoundError:
        print(f"Warning: Input data file {input_file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file_path}.")
    
    if not raw_ohlcv_data:
        print("Using mock data as input file was not found, empty, or malformed.")
        raw_ohlcv_data = [
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
            [1672599600000, 17090.0, 17150.0, 17080.0, 17130.0, 1700.0] # Min 20 data points
        ]

    if not raw_ohlcv_data:
        print("Error: No valid OHLCV data available (either from file or mock). Exiting.")
        sys.exit(1) # Exit if no data at all
    
    df_with_indicators = calculate_all_indicators(raw_ohlcv_data)

    if df_with_indicators is not None and not df_with_indicators.empty:
        print("\nDataFrame with Indicators:")
        print(df_with_indicators.head())
        print("...")
        print(df_with_indicators.tail())
        
        # Save to the specified output file
        # Convert timestamp index back to string or epoch for JSON compatibility if needed
        df_for_json = df_with_indicators.copy()
        # Ensure index is of a type that can be easily serialized, like string.
        if isinstance(df_for_json.index, pd.DatetimeIndex):
            df_for_json.index = df_for_json.index.strftime('%Y-%m-%d %H:%M:%S') # Example format
        else:
            df_for_json.index = df_for_json.index.astype(str)

        try:
            df_for_json.to_json(output_file_path, orient="table", indent=4, default_handler=str)
            print(f"\nDataFrame with indicators saved to {output_file_path}")
        except Exception as e:
            print(f"Error saving DataFrame to JSON: {e}", file=sys.stderr)


        # Example: How to get just the latest row of indicators as a dictionary
        latest_indicators = df_with_indicators.iloc[-1].to_dict()
        print("\nLatest indicators as dict:")
        print(json.dumps(latest_indicators, indent=4, default=str)) # Use default for NaNs etc.
    else:
        print("Could not calculate indicators or resulting DataFrame was empty.")
