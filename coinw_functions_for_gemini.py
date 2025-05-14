"""
This file defines functions that can be called by Google Gemini 
to fetch data from the CoinW exchange API, with CCXT as a fallback.
"""
import os
import requests # Placeholder for direct API calls if ever implemented
import json
import time
import hashlib # For CoinW API signature if needed
import ccxt

# --- CoinW API Configuration ---
COINW_API_KEY = os.environ.get("COINW_API_KEY", "ed2eb965-7841-4235-9278-7cec85d0e657") # Using provided key as default for testing
COINW_API_SECRET = os.environ.get("COINW_API_SECRET", "DZXHVSLXWGNKEY88V7LTEHDKBN7DIXNFBRZL") # Using provided secret as default for testing
COINW_BASE_URL = "https://api.coinw.com" # Official API base URL, may vary for specific endpoints

# --- Function Declarations for Gemini ---
# Corrected schema according to Gemini's expected format (using type_ and uppercase types)

GET_COINW_OHLCV_DATA_DECLARATION = {
    "name": "get_coinw_ohlcv_data",
    "description": "Fetches historical Open, High, Low, Close, and Volume (OHLCV) k-line data for a given cryptocurrency symbol and interval from CoinW exchange. Uses CCXT as a primary method.",
    "parameters": {
        "type_": "OBJECT", # Changed 'type' to 'type_'
        "properties": {
            "symbol": {
                "type_": "STRING", # Changed 'type' to 'type_'
                "description": "The trading symbol in CCXT format, e.g., 'BTC/USDT'."
            },
            "interval": {
                "type_": "STRING", # Changed 'type' to 'type_'
                "description": "The k-line interval in CCXT format. Common values: '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'."
            },
            "limit": {
                "type_": "INTEGER", # Changed 'type' to 'type_'
                "description": "Number of data points to retrieve. Default is 100."
            }
        },
        "required": ["symbol", "interval"]
    }
}

GET_COINW_FUNDING_RATE_DECLARATION = {
    "name": "get_coinw_funding_rate_data",
    "description": "Fetches funding rate data for a given perpetual contract symbol from CoinW exchange using CCXT.",
    "parameters": {
        "type_": "OBJECT", # Changed 'type' to 'type_'
        "properties": {
            "symbol": {
                "type_": "STRING", # Changed 'type' to 'type_'
                "description": "The perpetual contract symbol in CCXT format, e.g., 'BTC/USDT:USDT'. Ensure it's a perpetual swap symbol."
            }
        },
        "required": ["symbol"]
    }
}

GET_COINW_LONG_SHORT_RATIO_DECLARATION = {
    "name": "get_coinw_long_short_ratio_data",
    "description": "Attempts to fetch the long/short ratio for a given symbol from CoinW exchange using CCXT. Note: This is often exchange-specific and might not be available or standardized via CCXT for CoinW.",
    "parameters": {
        "type_": "OBJECT", # Changed 'type' to 'type_'
        "properties": {
            "symbol": {
                "type_": "STRING", # Changed 'type' to 'type_'
                "description": "The symbol in CCXT format, e.g., 'BTC/USDT'."
            }
        },
        "required": ["symbol"]
    }
}

# --- Python Functions to be Called (Implementations) ---

def get_coinw_ohlcv_data(symbol: str, interval: str, limit: int = 100):
    """Fetches OHLCV data from CoinW using CCXT."""
    print(f"Attempting to fetch OHLCV data for {symbol}, interval {interval}, limit {limit} from CoinW via CCXT.")
    if not COINW_API_KEY or not COINW_API_SECRET:
        return {"error": "CoinW API key/secret not configured in environment variables."}

    try:
        exchange = ccxt.coinw({
            'apiKey': COINW_API_KEY,
            'secret': COINW_API_SECRET,
            'options': {
                'defaultType': 'spot',
            }
        })
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=interval, limit=limit)
        if ohlcv:
            return {"status": "success", "data": ohlcv, "source": "ccxt"}
        else:
            return {"error": f"No OHLCV data returned by CCXT for {symbol} on CoinW.", "source": "ccxt"}
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching OHLCV for {symbol} on CoinW: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching OHLCV for {symbol} on CoinW: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching OHLCV for {symbol} on CoinW: {e}", "source": "ccxt"}

def get_coinw_funding_rate_data(symbol: str):
    """Fetches funding rate data from CoinW using CCXT."""
    print(f"Attempting to fetch funding rate data for {symbol} from CoinW via CCXT.")
    if not COINW_API_KEY or not COINW_API_SECRET:
        return {"error": "CoinW API key/secret not configured in environment variables."}

    try:
        exchange = ccxt.coinw({
            'apiKey': COINW_API_KEY,
            'secret': COINW_API_SECRET,
            'options': {
                'defaultType': 'swap',
            }
        })
        if not exchange.has['fetchFundingRate'] and not exchange.has['fetchFundingRates']:
             return {"error": f"CoinW (via CCXT) does not support fetchFundingRate or fetchFundingRates.", "source": "ccxt"}
        
        funding_rate_data = None
        if exchange.has['fetchFundingRate']:
            funding_rate_data = exchange.fetch_funding_rate(symbol)
        elif exchange.has['fetchFundingRates']:
            all_funding_rates = exchange.fetch_funding_rates()
            if symbol in all_funding_rates:
                funding_rate_data = all_funding_rates[symbol]
            else:
                for key, value in all_funding_rates.items():
                    if symbol.split(':')[0] == key.split(':')[0]:
                        funding_rate_data = value
                        print(f"Matched funding rate for {symbol} with key {key}")
                        break
                if not funding_rate_data:
                    return {"error": f"Funding rate for {symbol} not found in fetchFundingRates output.", "data_available": list(all_funding_rates.keys()), "source": "ccxt"}

        if funding_rate_data:
            # CCXT often returns a structure, we want to pass a JSON-serializable dict
            return {"status": "success", "data": funding_rate_data, "source": "ccxt"}
        else:
            return {"error": f"No funding rate data returned by CCXT for {symbol} on CoinW.", "source": "ccxt"}

    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching funding rate for {symbol} on CoinW: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching funding rate for {symbol} on CoinW: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching funding rate for {symbol} on CoinW: {e}", "source": "ccxt"}

def get_coinw_long_short_ratio_data(symbol: str):
    """Attempts to fetch long/short ratio data from CoinW using CCXT."""
    print(f"Attempting to fetch long/short ratio data for {symbol} from CoinW via CCXT.")
    if not COINW_API_KEY or not COINW_API_SECRET:
        return {"error": "CoinW API key/secret not configured in environment variables."}

    try:
        exchange = ccxt.coinw({
            'apiKey': COINW_API_KEY,
            'secret': COINW_API_SECRET,
        })
        if exchange.has.get('fetchLongShortRatio'):
            ls_ratio = exchange.fetchLongShortRatio(symbol)
            return {"status": "success", "data": ls_ratio, "source": "ccxt_unified_hypothetical"}
        
        return {"error": "Fetching long/short ratio via CCXT for CoinW is not directly supported or requires specific implicit API call knowledge not yet implemented.", "source": "ccxt"}
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError attempting to fetch long/short ratio for {symbol} on CoinW: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError attempting to fetch long/short ratio for {symbol} on CoinW: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT attempting to fetch long/short ratio for {symbol} on CoinW: {e}", "source": "ccxt"}

if __name__ == "__main__":
    print("This script defines functions and declarations for Gemini function calling using CCXT for CoinW.")
    print(f"Using COINW_API_KEY: {COINW_API_KEY[:5]}... and COINW_API_SECRET: {COINW_API_SECRET[:5]}...")
    # print("\nTesting OHLCV for BTC/USDT...")
    # ohlcv_data = get_coinw_ohlcv_data(symbol="BTC/USDT", interval="1h", limit=5)
    # print(json.dumps(ohlcv_data, indent=2))
    # print("\nTesting Funding Rate for BTC/USDT:USDT...")
    # funding_data = get_coinw_funding_rate_data(symbol="BTC/USDT:USDT")
    # print(json.dumps(funding_data, indent=2))
    # print("\nTesting Long/Short Ratio for BTC/USDT...")
    # ls_ratio_data = get_coinw_long_short_ratio_data(symbol="BTC/USDT")
    # print(json.dumps(ls_ratio_data, indent=2))
    print("\nNote: Uncomment test calls and ensure correct symbol formats for CoinW via CCXT.")

