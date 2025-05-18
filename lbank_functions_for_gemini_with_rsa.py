"""
This file defines functions that can be called by Google Gemini 
to fetch data from the LBank exchange API, with CCXT as a fallback.
Supports both HMAC-SHA256 and RSA signature methods.
"""
import os
import requests
import json
import time
import hashlib
import hmac
import base64
import ccxt
from urllib.parse import urlencode
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# --- LBank API Configuration ---
LBANK_API_KEY = os.environ.get("LBANK_API_KEY", "")  # Will be set by user in their environment
LBANK_API_SECRET = os.environ.get("LBANK_API_SECRET", "")  # Will be set by user in their environment
LBANK_BASE_URL = "https://api.lbkex.com"  # Official API base URL

# --- Function Declarations for Gemini ---
GET_LBANK_OHLCV_DATA_DECLARATION = {
    "name": "get_lbank_ohlcv_data",
    "description": "Fetches historical Open, High, Low, Close, and Volume (OHLCV) k-line data for a given cryptocurrency symbol and interval from LBank exchange.",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "symbol": {
                "type_": "STRING",
                "description": "The trading symbol in format like 'eth_btc'. For USDT pairs, use format like 'btc_usdt'."
            },
            "interval": {
                "type_": "STRING",
                "description": "The k-line interval. Supported values: 'minute1', 'minute5', 'minute15', 'minute30', 'hour1', 'hour4', 'hour8', 'hour12', 'day1', 'week1', 'month1'."
            },
            "size": {
                "type_": "INTEGER",
                "description": "Number of data points to retrieve. Default is 100, max is 2000."
            }
        },
        "required": ["symbol", "interval"]
    }
}

GET_LBANK_DEPTH_DATA_DECLARATION = {
    "name": "get_lbank_depth_data",
    "description": "Fetches order book depth data (bids and asks) for a given cryptocurrency symbol from LBank exchange.",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "symbol": {
                "type_": "STRING",
                "description": "The trading symbol in format like 'eth_btc'. For USDT pairs, use format like 'btc_usdt'."
            },
            "size": {
                "type_": "INTEGER",
                "description": "Number of price levels to retrieve. Default is 60, range is 1-200."
            }
        },
        "required": ["symbol"]
    }
}

GET_LBANK_TICKER_DATA_DECLARATION = {
    "name": "get_lbank_ticker_data",
    "description": "Fetches 24-hour ticker data for a given cryptocurrency symbol from LBank exchange.",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "symbol": {
                "type_": "STRING",
                "description": "The trading symbol in format like 'eth_btc'. For USDT pairs, use format like 'btc_usdt'."
            }
        },
        "required": ["symbol"]
    }
}

GET_LBANK_LATEST_PRICE_DECLARATION = {
    "name": "get_lbank_latest_price",
    "description": "Fetches the latest price for a given cryptocurrency symbol from LBank exchange.",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "symbol": {
                "type_": "STRING",
                "description": "The trading symbol in format like 'eth_btc'. For USDT pairs, use format like 'btc_usdt'."
            }
        },
        "required": ["symbol"]
    }
}

GET_LBANK_RECENT_TRADES_DECLARATION = {
    "name": "get_lbank_recent_trades",
    "description": "Fetches recent trade data for a given cryptocurrency symbol from LBank exchange.",
    "parameters": {
        "type_": "OBJECT",
        "properties": {
            "symbol": {
                "type_": "STRING",
                "description": "The trading symbol in format like 'eth_btc'. For USDT pairs, use format like 'btc_usdt'."
            },
            "size": {
                "type_": "INTEGER",
                "description": "Number of trades to retrieve. Default is 50, max is 600."
            }
        },
        "required": ["symbol"]
    }
}

# --- Helper Functions ---
def format_symbol_for_lbank(symbol):
    """Convert standard symbol format (BTC/USDT) to LBank format (btc_usdt)"""
    if '/' in symbol:
        base, quote = symbol.split('/')
        return f"{base.lower()}_{quote.lower()}"
    return symbol.lower()  # If already in correct format or unknown format

def format_symbol_for_ccxt(symbol):
    """Convert LBank symbol format (btc_usdt) to CCXT format (BTC/USDT)"""
    if '_' in symbol:
        base, quote = symbol.split('_')
        return f"{base.upper()}/{quote.upper()}"
    return symbol.upper()  # If already in correct format or unknown format

def format_interval_for_lbank(interval):
    """Convert common interval format to LBank format"""
    # Map common interval formats to LBank format
    interval_map = {
        '1m': 'minute1',
        '5m': 'minute5',
        '15m': 'minute15',
        '30m': 'minute30',
        '1h': 'hour1',
        '4h': 'hour4',
        '8h': 'hour8',
        '12h': 'hour12',
        '1d': 'day1',
        '1w': 'week1',
        '1M': 'month1'
    }
    return interval_map.get(interval, interval)  # Return mapped value or original if not found

def is_rsa_private_key(key_str):
    """Check if the provided key is an RSA private key"""
    try:
        if "-----BEGIN" in key_str and "PRIVATE KEY-----" in key_str:
            return True
        # Try to parse as PEM format
        RSA.import_key(key_str)
        return True
    except Exception:
        return False

def create_signature_hmac(api_secret, params_str):
    """Create HMAC-SHA256 signature for LBank API"""
    try:
        signature = hmac.new(
            api_secret.encode('utf-8'),
            params_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    except Exception as e:
        print(f"Error creating HMAC signature: {e}")
        return None

def create_signature_rsa(private_key_str, params_str):
    """Create RSA signature for LBank API"""
    try:
        # If the key doesn't have the proper PEM format, add it
        if "-----BEGIN" not in private_key_str:
            private_key_str = f"-----BEGIN RSA PRIVATE KEY-----\n{private_key_str}\n-----END RSA PRIVATE KEY-----"
        
        # Import the private key
        private_key = RSA.import_key(private_key_str)
        
        # Create the signature
        h = SHA256.new(params_str.encode('utf-8'))
        signature = pkcs1_15.new(private_key).sign(h)
        
        # Encode the signature in base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        return signature_b64
    except Exception as e:
        print(f"Error creating RSA signature: {e}")
        return None

def make_lbank_public_request(endpoint, params=None):
    """Make a public API request to LBank"""
    url = f"{LBANK_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON response"}

def make_lbank_private_request(endpoint, params=None):
    """Make a private API request to LBank with automatic signature method selection"""
    if not LBANK_API_KEY:
        return {"error": "API key is required for private API calls"}
    
    if not LBANK_API_SECRET:
        return {"error": "API secret is required for private API calls"}
    
    # Prepare parameters
    if params is None:
        params = {}
    
    params['api_key'] = LBANK_API_KEY
    params['timestamp'] = str(int(time.time() * 1000))
    
    # Sort parameters alphabetically
    sorted_params = dict(sorted(params.items()))
    params_str = urlencode(sorted_params)
    
    # Determine signature method and create signature
    signature = None
    signature_method = "hmac"  # Default method
    
    if is_rsa_private_key(LBANK_API_SECRET):
        signature = create_signature_rsa(LBANK_API_SECRET, params_str)
        signature_method = "rsa"
    else:
        signature = create_signature_hmac(LBANK_API_SECRET, params_str)
    
    if not signature:
        return {"error": f"Failed to create {signature_method.upper()} signature"}
    
    # Add signature to parameters
    params['sign'] = signature
    
    # Make the request
    url = f"{LBANK_BASE_URL}{endpoint}"
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON response"}

# --- Python Functions to be Called (Implementations) ---
def get_lbank_ohlcv_data(symbol, interval, size=100):
    """Fetches OHLCV data from LBank."""
    print(f"Attempting to fetch OHLCV data for {symbol}, interval {interval}, size {size} from LBank.")
    
    # Try direct API first
    try:
        # Format parameters
        lbank_symbol = format_symbol_for_lbank(symbol)
        lbank_interval = format_interval_for_lbank(interval)
        
        # Make request to LBank API
        endpoint = "/v2/kline.do"
        params = {
            "symbol": lbank_symbol,
            "type": lbank_interval,
            "size": size
        }
        
        response = make_lbank_public_request(endpoint, params)
        
        if "error" in response:
            print(f"Direct API error: {response['error']}, trying CCXT fallback...")
        else:
            return {"status": "success", "data": response, "source": "direct_api"}
    
    except Exception as e:
        print(f"Error with direct API: {str(e)}, trying CCXT fallback...")
    
    # Fallback to CCXT
    try:
        exchange = ccxt.lbank()
        ccxt_symbol = format_symbol_for_ccxt(symbol)
        ccxt_timeframe = interval if interval in ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M'] else '1h'  # Default to 1h if not standard
        
        ohlcv = exchange.fetch_ohlcv(ccxt_symbol, timeframe=ccxt_timeframe, limit=size)
        if ohlcv:
            return {"status": "success", "data": ohlcv, "source": "ccxt"}
        else:
            return {"error": f"No OHLCV data returned by CCXT for {symbol} on LBank.", "source": "ccxt"}
    
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching OHLCV for {symbol} on LBank: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching OHLCV for {symbol} on LBank: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching OHLCV for {symbol} on LBank: {e}", "source": "ccxt"}

def get_lbank_depth_data(symbol, size=60):
    """Fetches order book depth data from LBank."""
    print(f"Attempting to fetch depth data for {symbol}, size {size} from LBank.")
    
    # Try direct API first
    try:
        # Format parameters
        lbank_symbol = format_symbol_for_lbank(symbol)
        
        # Make request to LBank API
        endpoint = "/v2/depth.do"
        params = {
            "symbol": lbank_symbol,
            "size": size
        }
        
        response = make_lbank_public_request(endpoint, params)
        
        if "error" in response:
            print(f"Direct API error: {response['error']}, trying CCXT fallback...")
        else:
            return {"status": "success", "data": response, "source": "direct_api"}
    
    except Exception as e:
        print(f"Error with direct API: {str(e)}, trying CCXT fallback...")
    
    # Fallback to CCXT
    try:
        exchange = ccxt.lbank()
        ccxt_symbol = format_symbol_for_ccxt(symbol)
        
        order_book = exchange.fetch_order_book(ccxt_symbol, limit=size)
        if order_book:
            return {"status": "success", "data": order_book, "source": "ccxt"}
        else:
            return {"error": f"No depth data returned by CCXT for {symbol} on LBank.", "source": "ccxt"}
    
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching depth for {symbol} on LBank: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching depth for {symbol} on LBank: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching depth for {symbol} on LBank: {e}", "source": "ccxt"}

def get_lbank_ticker_data(symbol):
    """Fetches 24-hour ticker data from LBank."""
    print(f"Attempting to fetch ticker data for {symbol} from LBank.")
    
    # Try direct API first
    try:
        # Format parameters
        lbank_symbol = format_symbol_for_lbank(symbol)
        
        # Make request to LBank API
        endpoint = "/v2/ticker/24hr.do"
        params = {
            "symbol": lbank_symbol
        }
        
        response = make_lbank_public_request(endpoint, params)
        
        if "error" in response:
            print(f"Direct API error: {response['error']}, trying CCXT fallback...")
        else:
            return {"status": "success", "data": response, "source": "direct_api"}
    
    except Exception as e:
        print(f"Error with direct API: {str(e)}, trying CCXT fallback...")
    
    # Fallback to CCXT
    try:
        exchange = ccxt.lbank()
        ccxt_symbol = format_symbol_for_ccxt(symbol)
        
        ticker = exchange.fetch_ticker(ccxt_symbol)
        if ticker:
            return {"status": "success", "data": ticker, "source": "ccxt"}
        else:
            return {"error": f"No ticker data returned by CCXT for {symbol} on LBank.", "source": "ccxt"}
    
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching ticker for {symbol} on LBank: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching ticker for {symbol} on LBank: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching ticker for {symbol} on LBank: {e}", "source": "ccxt"}

def get_lbank_latest_price(symbol):
    """Fetches the latest price from LBank."""
    print(f"Attempting to fetch latest price for {symbol} from LBank.")
    
    # Try direct API first
    try:
        # Format parameters
        lbank_symbol = format_symbol_for_lbank(symbol)
        
        # Make request to LBank API
        endpoint = "/v2/supplement/ticker/price.do"
        params = {
            "symbol": lbank_symbol
        }
        
        response = make_lbank_public_request(endpoint, params)
        
        if "error" in response:
            print(f"Direct API error: {response['error']}, trying CCXT fallback...")
        else:
            return {"status": "success", "data": response, "source": "direct_api"}
    
    except Exception as e:
        print(f"Error with direct API: {str(e)}, trying CCXT fallback...")
    
    # Fallback to CCXT
    try:
        exchange = ccxt.lbank()
        ccxt_symbol = format_symbol_for_ccxt(symbol)
        
        ticker = exchange.fetch_ticker(ccxt_symbol)
        if ticker and 'last' in ticker:
            return {"status": "success", "data": {"symbol": symbol, "price": str(ticker['last'])}, "source": "ccxt"}
        else:
            return {"error": f"No price data returned by CCXT for {symbol} on LBank.", "source": "ccxt"}
    
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching price for {symbol} on LBank: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching price for {symbol} on LBank: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching price for {symbol} on LBank: {e}", "source": "ccxt"}

def get_lbank_recent_trades(symbol, size=50):
    """Fetches recent trade data from LBank."""
    print(f"Attempting to fetch recent trades for {symbol}, size {size} from LBank.")
    
    # Try direct API first
    try:
        # Format parameters
        lbank_symbol = format_symbol_for_lbank(symbol)
        
        # Make request to LBank API
        endpoint = "/v2/supplement/trades.do"
        params = {
            "symbol": lbank_symbol,
            "size": size
        }
        
        response = make_lbank_public_request(endpoint, params)
        
        if "error" in response:
            print(f"Direct API error: {response['error']}, trying CCXT fallback...")
        else:
            return {"status": "success", "data": response, "source": "direct_api"}
    
    except Exception as e:
        print(f"Error with direct API: {str(e)}, trying CCXT fallback...")
    
    # Fallback to CCXT
    try:
        exchange = ccxt.lbank()
        ccxt_symbol = format_symbol_for_ccxt(symbol)
        
        trades = exchange.fetch_trades(ccxt_symbol, limit=size)
        if trades:
            return {"status": "success", "data": trades, "source": "ccxt"}
        else:
            return {"error": f"No trades data returned by CCXT for {symbol} on LBank.", "source": "ccxt"}
    
    except ccxt.NetworkError as e:
        return {"error": f"CCXT NetworkError fetching trades for {symbol} on LBank: {e}", "source": "ccxt"}
    except ccxt.ExchangeError as e:
        return {"error": f"CCXT ExchangeError fetching trades for {symbol} on LBank: {e}", "source": "ccxt"}
    except Exception as e:
        return {"error": f"An unexpected error occurred with CCXT fetching trades for {symbol} on LBank: {e}", "source": "ccxt"}

# --- Example of a private API call using automatic signature selection ---
def get_lbank_account_info():
    """Fetches account information from LBank (requires API key and secret)."""
    print("Attempting to fetch account information from LBank.")
    
    # This is a private API call that requires authentication
    endpoint = "/v2/user/info.do"
    
    # No additional parameters needed for this endpoint
    response = make_lbank_private_request(endpoint)
    
    if "error" in response:
        print(f"Error fetching account info: {response['error']}")
        return {"error": response['error']}
    
    return {"status": "success", "data": response}

# --- Main Function for Testing ---
if __name__ == "__main__":
    print("This script defines functions and declarations for Gemini function calling using LBank API and CCXT.")
    print("Supports both HMAC-SHA256 and RSA signature methods.")
    
    # Detect signature method
    if LBANK_API_SECRET:
        if is_rsa_private_key(LBANK_API_SECRET):
            print("Detected RSA private key format for API secret.")
        else:
            print("Using HMAC-SHA256 signature method (default).")
    
    print("Note: For testing, uncomment the test calls below and ensure correct symbol formats.")
    
    # Uncomment to test
    # print("\nTesting OHLCV for BTC/USDT...")
    # ohlcv_data = get_lbank_ohlcv_data(symbol="btc_usdt", interval="hour1", size=5)
    # print(json.dumps(ohlcv_data, indent=2))
    
    # print("\nTesting Depth for BTC/USDT...")
    # depth_data = get_lbank_depth_data(symbol="btc_usdt", size=10)
    # print(json.dumps(depth_data, indent=2))
    
    # print("\nTesting Ticker for BTC/USDT...")
    # ticker_data = get_lbank_ticker_data(symbol="btc_usdt")
    # print(json.dumps(ticker_data, indent=2))
    
    # print("\nTesting Latest Price for BTC/USDT...")
    # price_data = get_lbank_latest_price(symbol="btc_usdt")
    # print(json.dumps(price_data, indent=2))
    
    # print("\nTesting Recent Trades for BTC/USDT...")
    # trades_data = get_lbank_recent_trades(symbol="btc_usdt", size=5)
    # print(json.dumps(trades_data, indent=2))
    
    # If you have API key and secret, you can test private API calls
    # print("\nTesting Account Info (requires API key and secret)...")
    # account_info = get_lbank_account_info()
    # print(json.dumps(account_info, indent=2))
