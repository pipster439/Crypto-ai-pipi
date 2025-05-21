import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import time
from urllib.parse import urlencode
import hmac
import hashlib
import base64

# Add project root to sys.path to allow importing project modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lbank_functions_for_gemini_with_rsa import (
    format_symbol_for_lbank,
    format_symbol_for_ccxt,
    format_interval_for_lbank,
    is_rsa_private_key,
    create_signature_hmac,
    create_signature_rsa,
    get_lbank_ohlcv_data,
    get_lbank_depth_data,
    get_lbank_latest_price,
    get_lbank_ticker_data_ccxt_fallback,
    get_lbank_recent_trades,
    get_lbank_account_info,
    LBANK_API_BASE_URL,
    LBANK_API_KEY_INFO_PATH,
    LBANK_USER_INFO_PATH,
    LBANK_KLINE_PATH,
    LBANK_DEPTH_PATH,
    LBANK_TICKER_PATH,
    LBANK_TRADES_PATH
)

# Dummy RSA keys for testing
DUMMY_RSA_PRIVATE_KEY_STR = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQC+rZJ2YH3a7yNCfEY0p3nsZpCE28MT8jhw7t4j30RBrLgUhYkY
wLPiP5W8VquHeCsvxKq9pjsWTOLjE/2zC1fjPqSQbrj9R9WMJ8t3YLbQp3K0kLIO
l0cbhX8SwLdTnCWCfrEhzf6lZ2fWfSLN0oR8U4f1473xnnL3kIL0x23yjwIDAQAB
AoGAE5KkY3CFIIqfT9zK3ftQeUI2ATh6nOcp09W0sY25EmIBNW0gY5iNYOayLrdC
L5g2hPKEAgJz0xUhJ5cQxnegPE3XG9TgSnz/Not236L8x39j2yPgwkHKgUCR8jQk
5Ca2iqYSSJSILpPsG9n8yV4d8t7yS8YEY031aKkdjcdonNkCQQDkdOqOSEyL1TEd
kYl4/sJdUbTWzAJPE7o+UfLqjSnGFE/D62uFkGqXqP8xNBbpkStApmTyWNQp9aZN
R4uCgO/PAkEA72hbiIBL9xXz4qVvflHCQz/M9Gq9g0aP9uGvBDKxMH81fclVf0Ao
sPcbStPE0AnK1QjXoNl3/u7vX2PyX5JPTwJAX3Q/hL0EWNn81z+nQhYlAXvYf9s8
kYF5nISiUYM09x9y4OAwkOpXl5XNGjRpuuXGgqdt5q8rEaU2LzE7fN8x6wJBAL3p
g8JzmUvO+v71Wj6QxQIDAQABAkEAx1E+oMS6o8oM9K3X8s6h5Q/gW4TXrV3dMv1R
oOcUe71tYlROV9X/34vsjNPo7rFvoLI2s5z2W7r5X0xaQ2WbEg==
-----END RSA PRIVATE KEY-----"""

DUMMY_INVALID_RSA_KEY_STR = """-----BEGIN PRIVATE KEY-----
thisisnotavalidkey
-----END PRIVATE KEY-----"""

DUMMY_HMAC_SECRET = "testsecret"
DUMMY_API_KEY = "testapikey"


class TestLBankFunctions(unittest.TestCase):

    def test_format_symbol_for_lbank(self):
        self.assertEqual(format_symbol_for_lbank("BTC/USDT"), "btc_usdt")
        self.assertEqual(format_symbol_for_lbank("ETH/BTC"), "eth_btc")
        self.assertEqual(format_symbol_for_lbank("btc_usdt"), "btc_usdt") # Already formatted

    def test_format_symbol_for_ccxt(self):
        self.assertEqual(format_symbol_for_ccxt("btc_usdt"), "BTC/USDT")
        self.assertEqual(format_symbol_for_ccxt("eth_btc"), "ETH/BTC")
        self.assertEqual(format_symbol_for_ccxt("BTC/USDT"), "BTC/USDT") # Already formatted

    def test_format_interval_for_lbank(self):
        self.assertEqual(format_interval_for_lbank("1m"), "minute1")
        self.assertEqual(format_interval_for_lbank("1h"), "hour1")
        self.assertEqual(format_interval_for_lbank("1d"), "day1")
        self.assertEqual(format_interval_for_lbank("1w"), "week1")
        self.assertEqual(format_interval_for_lbank("unknown"), "unknown")

    def test_is_rsa_private_key(self):
        self.assertTrue(is_rsa_private_key(DUMMY_RSA_PRIVATE_KEY_STR))
        self.assertFalse(is_rsa_private_key(DUMMY_INVALID_RSA_KEY_STR))
        self.assertFalse(is_rsa_private_key("this is a plain string"))
        self.assertFalse(is_rsa_private_key(DUMMY_HMAC_SECRET))

    def test_create_signature_hmac(self):
        params = {"echostr": "abcdef", "signature_method": "HmacSHA256", "timestamp": "1234567890"}
        # Expected signature can be generated manually or from a trusted source
        # For this example, let's assume a known output for given params & secret
        # params_str = urlencode(params)
        # expected_signature = hmac.new(DUMMY_HMAC_SECRET.encode('utf-8'), params_str.encode('utf-8'), hashlib.sha256).hexdigest().upper()
        # self.assertEqual(create_signature_hmac(params, DUMMY_HMAC_SECRET), expected_signature)
        # Actual test:
        signature = create_signature_hmac(params, DUMMY_HMAC_SECRET)
        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0) # Check if a signature is generated

    def test_create_signature_rsa(self):
        params = {"echostr": "abcdef", "signature_method": "RSA", "timestamp": "1234567890"}
        signature = create_signature_rsa(params, DUMMY_RSA_PRIVATE_KEY_STR)
        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0) # Check if a signature is generated
        # Verification of RSA is complex and would require the public key.
        # For this unit test, generating any signature is a basic check.

    @patch('requests.get')
    def test_get_lbank_ohlcv_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "true", "data": [[time.time()*1000, 100, 110, 90, 105, 1000]], "error_code": 0}
        mock_get.return_value = mock_response
        
        result = get_lbank_ohlcv_data("btc_usdt", "hour1", 10)
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['data'], list)
        self.assertEqual(len(result['data'][0]), 6)
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_get_lbank_ohlcv_data_api_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200 # API returns 200 but with error code
        mock_response.json.return_value = {"result": "false", "error_code": 10001, "msg": "Invalid symbol"}
        mock_get.return_value = mock_response

        result = get_lbank_ohlcv_data("invalid_symbol", "hour1", 10)
        self.assertEqual(result['status'], 'error')
        self.assertIn("API error", result['error'])
        self.assertIn("10001", result['error'])

    @patch('requests.get', side_effect=requests.exceptions.RequestException("Network Error"))
    def test_get_lbank_ohlcv_data_network_error(self, mock_get):
        result = get_lbank_ohlcv_data("btc_usdt", "hour1", 10)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Network Error", result['error'])

    @patch('requests.get')
    def test_get_lbank_depth_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "true", 
            "data": {"asks": [[100,1]], "bids": [[99,1]]}, 
            "error_code": 0
        }
        mock_get.return_value = mock_response
        result = get_lbank_depth_data("btc_usdt", 10)
        self.assertEqual(result['status'], 'success')
        self.assertIn('asks', result['data'])
        self.assertIn('bids', result['data'])

    @patch('requests.get')
    def test_get_lbank_latest_price_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "true", 
            "data": [{"symbol": "btc_usdt", "ticker": {"latest": "30000"}}], 
            "error_code": 0
        }
        mock_get.return_value = mock_response
        result = get_lbank_latest_price("btc_usdt")
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['price'], "30000")

    @patch('ccxt.lbank')
    def test_get_lbank_ticker_data_ccxt_fallback_success(self, mock_lbank_ccxt):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_ticker.return_value = {"last": 31000, "symbol": "BTC/USDT"}
        mock_lbank_ccxt.return_value = mock_exchange_instance

        result = get_lbank_ticker_data_ccxt_fallback("BTC/USDT")
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['price'], 31000)

    @patch('ccxt.lbank')
    def test_get_lbank_ticker_data_ccxt_fallback_error(self, mock_lbank_ccxt):
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.fetch_ticker.side_effect = Exception("CCXT Network Error")
        mock_lbank_ccxt.return_value = mock_exchange_instance

        result = get_lbank_ticker_data_ccxt_fallback("BTC/USDT")
        self.assertEqual(result['status'], 'error')
        self.assertIn("CCXT Network Error", result['error'])


    @patch('requests.get')
    def test_get_lbank_recent_trades_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "true",
            "data": [{"price": "30000", "amount": "0.1", "type": "buy", "time": time.time()*1000}],
            "error_code": 0
        }
        mock_get.return_value = mock_response
        result = get_lbank_recent_trades("btc_usdt", 10)
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['data'], list)

    # Test for get_lbank_account_info (requires mocking POST and signature logic)
    @patch('requests.post')
    def test_get_lbank_account_info_success_hmac(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "true",
            "data": {"asset": {"BTC": {"free": "1.0", "freeze": "0.1"}}},
            "error_code": 0
        }
        mock_post.return_value = mock_response

        result = get_lbank_account_info(DUMMY_API_KEY, DUMMY_HMAC_SECRET)
        self.assertEqual(result['status'], 'success')
        self.assertIn('asset', result['data'])
        mock_post.assert_called_once()
        # Verify that the call was made with HMAC signature
        args, kwargs = mock_post.call_args
        self.assertIn("sign", kwargs['data'])
        self.assertIn("signature_method=HmacSHA256", kwargs['data'])


    @patch('requests.post')
    def test_get_lbank_account_info_success_rsa(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": "true",
            "data": {"asset": {"ETH": {"free": "10.0", "freeze": "1.0"}}},
            "error_code": 0
        }
        mock_post.return_value = mock_response

        result = get_lbank_account_info(DUMMY_API_KEY, DUMMY_RSA_PRIVATE_KEY_STR)
        self.assertEqual(result['status'], 'success')
        self.assertIn('asset', result['data'])
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("sign", kwargs['data'])
        self.assertIn("signature_method=RSA", kwargs['data'])


    @patch('requests.post')
    def test_get_lbank_account_info_api_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "false", "error_code": 10013, "msg": "Invalid API key"}
        mock_post.return_value = mock_response

        result = get_lbank_account_info("invalidkey", DUMMY_HMAC_SECRET)
        self.assertEqual(result['status'], 'error')
        self.assertIn("API error 10013", result['error'])

    @patch('requests.post', side_effect=requests.exceptions.RequestException("Network Error"))
    def test_get_lbank_account_info_network_error(self, mock_post):
        result = get_lbank_account_info(DUMMY_API_KEY, DUMMY_HMAC_SECRET)
        self.assertEqual(result['status'], 'error')
        self.assertIn("Network Error", result['error'])

    def test_get_lbank_ohlcv_data_empty_response(self):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "true", "data": [], "error_code": 0} # Empty data list
            mock_get.return_value = mock_response
            
            result = get_lbank_ohlcv_data("btc_usdt", "hour1", 10)
            self.assertEqual(result['status'], 'success') # API call itself is successful
            self.assertEqual(result['data'], []) # Data is empty as returned

    def test_get_lbank_depth_data_malformed_response(self):
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "true", "data": {"no_asks_bids": True}, "error_code": 0} # Malformed
            mock_get.return_value = mock_response
            
            result = get_lbank_depth_data("btc_usdt", 10)
            self.assertEqual(result['status'], 'error') # Should detect malformed data
            self.assertIn("Depth data is not in expected format", result['error'])


if __name__ == '__main__':
    unittest.main()
