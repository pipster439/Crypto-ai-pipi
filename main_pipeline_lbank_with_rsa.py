import os
import subprocess
import argparse
import sys
import json

# Determine the base directory of the script, to make paths relative
# This makes the script runnable from any directory as long as the sub-scripts are in the same location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration for script names and default file paths (relative to this script)
SCRIPTS = {
    "calculate_indicators": os.path.join(BASE_DIR, "calculate_technical_indicators.py"),
    "generate_prompt": os.path.join(BASE_DIR, "generate_final_llm_prompt.py"),
    "run_gemini": os.path.join(BASE_DIR, "run_gemini_report_generation_fc_lbank.py"),  # Updated to use LBank version
}

DEFAULT_FILES = {
    "fetched_data": os.path.join(BASE_DIR, "fetched_market_data.json"),
    "indicators_data": os.path.join(BASE_DIR, "ohlcv_with_all_indicators.json"),
    "final_prompt": os.path.join(BASE_DIR, "final_llm_prompt_for_gemini.md"),
    "report_output": os.path.join(BASE_DIR, "gemini_fc_generated_report_lbank.md"),  # Updated output filename
    "prompt_template": os.path.join(BASE_DIR, "user_llm_prompt_template_lbank.md") # Updated to use LBank template
}

PYTHON_EXECUTABLE = sys.executable # Use the same python interpreter that runs this script

def run_script(script_path, script_args=None):
    """Helper function to run a Python script using subprocess."""
    command = [PYTHON_EXECUTABLE, script_path]
    if script_args:
        command.extend(script_args)
    
    print("\n--- Running script: " + " ".join(command) + " ---") 
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True, cwd=BASE_DIR)
        print(process.stdout)
        if process.stderr:
            print("Stderr:", process.stderr, file=sys.stderr)
        print(f"--- Script {os.path.basename(script_path)} completed successfully. ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {os.path.basename(script_path)}:", file=sys.stderr)
        print("Return code:", e.returncode, file=sys.stderr)
        print("Stdout:", e.stdout, file=sys.stderr)
        print("Stderr:", e.stderr, file=sys.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: Script not found at {script_path}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Main pipeline script for crypto analysis report generation using LBank data.")
    parser.add_argument("--gemini_api_key", type=str, default=os.environ.get("GEMINI_API_KEY"),
                        help="Google Gemini API Key. Defaults to GEMINI_API_KEY environment variable.")
    parser.add_argument("--lbank_api_key", type=str, default=os.environ.get("LBANK_API_KEY"),
                        help="LBank API Key. Defaults to LBANK_API_KEY environment variable.")
    parser.add_argument("--lbank_api_secret", type=str, default=os.environ.get("LBANK_API_SECRET"),
                        help="LBank API Secret. Defaults to LBANK_API_SECRET environment variable. Can be HMAC-SHA256 key or RSA private key.")
    
    parser.add_argument("--fetched_data_file", type=str, default=DEFAULT_FILES["fetched_data"],
                        help="Path to the fetched market data JSON file. Default: " + DEFAULT_FILES["fetched_data"])
    parser.add_argument("--indicators_file", type=str, default=DEFAULT_FILES["indicators_data"],
                        help="Path for the output indicators JSON file. Default: " + DEFAULT_FILES["indicators_data"])
    parser.add_argument("--final_prompt_file", type=str, default=DEFAULT_FILES["final_prompt"],
                        help="Path for the final LLM prompt Markdown file. Default: " + DEFAULT_FILES["final_prompt"])
    parser.add_argument("--report_file", type=str, default=DEFAULT_FILES["report_output"],
                        help="Path for the final generated report Markdown file. Default: " + DEFAULT_FILES["report_output"])
    parser.add_argument("--prompt_template_file", type=str, default=DEFAULT_FILES["prompt_template"],
                        help="Path to the LLM prompt template. Default: " + DEFAULT_FILES["prompt_template"])

    args = parser.parse_args()

    if not args.gemini_api_key:
        print("Error: Gemini API Key not provided. Set GEMINI_API_KEY environment variable or use --gemini_api_key argument.", file=sys.stderr)
        sys.exit(1)

    # Set environment variables for API keys
    os.environ["GEMINI_API_KEY"] = args.gemini_api_key
    if args.lbank_api_key:
        os.environ["LBANK_API_KEY"] = args.lbank_api_key
    if args.lbank_api_secret:
        os.environ["LBANK_API_SECRET"] = args.lbank_api_secret

    # Get symbol from user input
    user_symbol = input("请输入您想要分析的交易对 (例如 BTC/USDT 或 btc_usdt): ").strip()
    if not user_symbol:
        print("未输入交易对，将使用默认值 BTC/USDT")
        user_symbol = "BTC/USDT"
    
    # Convert symbol format if needed
    if '/' in user_symbol:
        # Convert from CCXT format (BTC/USDT) to LBank format (btc_usdt)
        base, quote = user_symbol.split('/')
        lbank_symbol = f"{base.lower()}_{quote.lower()}"
    elif '_' in user_symbol:
        # Already in LBank format
        lbank_symbol = user_symbol.lower()
        # Also create CCXT format for compatibility
        base, quote = user_symbol.split('_')
        user_symbol = f"{base.upper()}/{quote.upper()}"
    else:
        # Unknown format, try to handle gracefully
        print(f"警告: 交易对格式 '{user_symbol}' 不标准，尝试处理...")
        lbank_symbol = user_symbol.lower()
        user_symbol = user_symbol.upper()

    print(f"使用交易对: {user_symbol} (LBank格式: {lbank_symbol})")

    # Check if API keys are provided
    if args.lbank_api_key:
        print("已检测到LBank API密钥")
        if args.lbank_api_secret:
            # Try to detect if it's an RSA key
            try:
                from lbank_functions_for_gemini_with_rsa import is_rsa_private_key
                if is_rsa_private_key(args.lbank_api_secret):
                    print("已检测到RSA私钥格式，将使用RSA签名方式")
                else:
                    print("将使用HMAC-SHA256签名方式（默认）")
            except ImportError:
                print("无法检测签名方式，将使用默认签名方法")
    else:
        print("未提供LBank API密钥，将仅使用公共API")

    print(f"\n--- Ensuring input data file: {args.fetched_data_file} ---")
    if not os.path.exists(args.fetched_data_file):
        print(f"Warning: Fetched data file {args.fetched_data_file} not found.")
        print(f"Creating a dummy version with symbol {user_symbol} for the pipeline to proceed.")
        print("This dummy file will likely be overwritten by actual data if Gemini function calling is triggered for this symbol.")
        dummy_data = {
            "symbol": user_symbol,
            "lbank_symbol": lbank_symbol,  # Add LBank format symbol
            "interval": "1h", 
            "ohlcv": [
                [1672531200000, 20000, 20100, 19900, 20050, 100],
                [1672534800000, 20050, 20150, 19950, 20080, 120]
            ],
            "depth": {  # Add dummy depth data structure
                "asks": [[20100, 1.5], [20150, 2.3]],
                "bids": [[19950, 1.8], [19900, 2.5]]
            }
        }
        try:
            with open(args.fetched_data_file, "w") as f:
                json.dump(dummy_data, f, indent=2)
            print(f"Dummy file {args.fetched_data_file} created for symbol {user_symbol}.")
        except IOError as e:
            print(f"Error creating dummy file {args.fetched_data_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Using existing fetched data file: {args.fetched_data_file}")
        # Update the symbol in the existing file to match user input
        try:
            with open(args.fetched_data_file, 'r') as f:
                data = json.load(f)
            data['symbol'] = user_symbol
            data['lbank_symbol'] = lbank_symbol
            with open(args.fetched_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Updated symbol in existing data file to {user_symbol}.")
        except Exception as e:
            print(f"Warning: Could not update symbol in existing data file: {e}")

    if not run_script(SCRIPTS["calculate_indicators"]):
        print("Pipeline failed at technical indicator calculation.", file=sys.stderr)
        sys.exit(1)

    if not run_script(SCRIPTS["generate_prompt"]):
        print("Pipeline failed at LLM prompt generation.", file=sys.stderr)
        sys.exit(1)

    gemini_args = [
        "--prompt_file", args.final_prompt_file,
        "--output_file", args.report_file,
    ]
    if not run_script(SCRIPTS["run_gemini"], gemini_args):
        print("Pipeline failed at Gemini report generation.", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Full pipeline executed successfully! Report saved to {args.report_file} ---")
    print(f"注意: 此报告使用LBank交易所数据生成，包含深度市场数据分析。")
    
    # Provide information about the signature method used
    if args.lbank_api_key and args.lbank_api_secret:
        try:
            from lbank_functions_for_gemini_with_rsa import is_rsa_private_key
            if is_rsa_private_key(args.lbank_api_secret):
                print("本次分析使用了RSA签名方式访问LBank API。")
            else:
                print("本次分析使用了HMAC-SHA256签名方式访问LBank API。")
        except ImportError:
            pass

if __name__ == "__main__":
    main()
