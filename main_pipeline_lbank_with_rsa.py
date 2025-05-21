import os
import subprocess
import argparse
import sys
import json
import time

# Import necessary functions from lbank_functions_for_gemini_with_rsa
try:
    from lbank_functions_for_gemini_with_rsa import (
        get_lbank_ohlcv_data,
        get_lbank_depth_data,
        get_lbank_latest_price,
        # format_symbol_for_lbank, # Already handled in main
        # format_interval_for_lbank, # Will use a fixed value or simple mapping
        is_rsa_private_key # Keep this for API key detection
    )
except ImportError:
    print("Error: Could not import from lbank_functions_for_gemini_with_rsa.py. Ensure the file is in the same directory or PYTHONPATH.")
    sys.exit(1)


# Determine the base directory of the script, to make paths relative
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration for script names and default file paths (relative to this script)
SCRIPTS = {
    "calculate_indicators": os.path.join(BASE_DIR, "calculate_technical_indicators.py"),
    "generate_prompt": os.path.join(BASE_DIR, "generate_final_llm_prompt.py"),
    "run_gemini": os.path.join(BASE_DIR, "run_gemini_report_generation_fc_lbank.py"),
}

DEFAULT_FILES = {
    "fetched_data": os.path.join(BASE_DIR, "fetched_market_data.json"),
    "indicators_data": os.path.join(BASE_DIR, "ohlcv_with_all_indicators.json"),
    "final_prompt": os.path.join(BASE_DIR, "final_llm_prompt_for_gemini.md"),
    "report_output": os.path.join(BASE_DIR, "gemini_fc_generated_report_lbank.md"),
    "prompt_template": os.path.join(BASE_DIR, "user_llm_prompt_template_lbank.md")
}

PYTHON_EXECUTABLE = sys.executable

def _generate_dummy_data(user_symbol, lbank_symbol, interval_str):
    """Generates dummy market data for fallback."""
    print(f"Generating dummy data for {user_symbol} (LBank: {lbank_symbol}) with interval {interval_str}.")
    return {
        "symbol": user_symbol,
        "lbank_symbol": lbank_symbol,
        "interval": interval_str,
        "ohlcv": [
            [int(time.time() - 3600 * 2 * 1000), 20000, 20100, 19900, 20050, 100], # Dummy data for 2 hours ago
            [int(time.time() - 3600 * 1 * 1000), 20050, 20150, 19950, 20080, 120]  # Dummy data for 1 hour ago
        ],
        "depth": {
            "asks": [[20100.0, 1.5], [20150.0, 2.3]],
            "bids": [[19950.0, 1.8], [19900.0, 2.5]]
        },
        "latest_price": {"price": 20080.0} # Consistent with the last OHLCV close
    }

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
    user_symbol_input = input("请输入您想要分析的交易对 (例如 BTC/USDT 或 btc_usdt): ").strip()
    if not user_symbol_input:
        print("未输入交易对，将使用默认值 BTC/USDT")
        user_symbol_input = "BTC/USDT"

    # Convert symbol format
    if '/' in user_symbol_input:
        base, quote = user_symbol_input.split('/')
        lbank_symbol = f"{base.lower()}_{quote.lower()}"
        user_symbol = user_symbol_input.upper() # Keep standard format for display
    elif '_' in user_symbol_input:
        lbank_symbol = user_symbol_input.lower()
        base, quote = user_symbol_input.split('_')
        user_symbol = f"{base.upper()}/{quote.upper()}" # Create standard format
    else:
        print(f"警告: 交易对格式 '{user_symbol_input}' 不标准，尝试处理为 {user_symbol_input.lower()}_usdt (LBank) 和 {user_symbol_input.upper()}/USDT (Display)")
        lbank_symbol = f"{user_symbol_input.lower()}_usdt" # Assume USDT pair if not specified
        user_symbol = f"{user_symbol_input.upper()}/USDT"

    print(f"使用交易对: {user_symbol} (LBank API格式: {lbank_symbol})")

    # Check if API keys are provided and print info
    if args.lbank_api_key and args.lbank_api_secret:
        print("已检测到LBank API密钥。")
        if is_rsa_private_key(args.lbank_api_secret):
            print("已检测到RSA私钥格式，将使用RSA签名方式。")
        else:
            print("将使用HMAC-SHA256签名方式（默认）。")
    else:
        print("未提供LBank API密钥，将仅使用公共API端点 (可能会有速率限制或功能限制)。")

    # --- Data Fetching Logic ---
    print("\n--- 开始从LBank获取市场数据 ---")
    default_interval_display = "1h"
    default_interval_lbank = "hour1" # LBank specific interval for 1 hour
    ohlcv_size = 200 # Number of data points for OHLCV

    print(f"将使用默认时间间隔: {default_interval_display} (LBank: {default_interval_lbank})，获取 {ohlcv_size} 条OHLCV数据点。")

    fetched_all_data_successfully = False
    market_data_dict = {}

    while not fetched_all_data_successfully:
        # Fetch OHLCV data
        print(f"\n正在获取 {lbank_symbol} 的OHLCV数据...")
        ohlcv_response = get_lbank_ohlcv_data(symbol=lbank_symbol, interval=default_interval_lbank, size=ohlcv_size, api_key=args.lbank_api_key, secret_key=args.lbank_api_secret)
        
        # Fetch Depth data
        print(f"\n正在获取 {lbank_symbol} 的深度数据...")
        depth_response = get_lbank_depth_data(symbol=lbank_symbol, size=50, api_key=args.lbank_api_key, secret_key=args.lbank_api_secret)
        
        # Fetch Latest Price
        print(f"\n正在获取 {lbank_symbol} 的最新价格...")
        latest_price_response = get_lbank_latest_price(symbol=lbank_symbol, api_key=args.lbank_api_key, secret_key=args.lbank_api_secret)

        # Process responses
        ohlcv_data = None
        depth_data = None
        latest_price_data = None
        errors_occurred = False

        if ohlcv_response.get('status') == 'success' and ohlcv_response.get('data'):
            ohlcv_data = ohlcv_response['data']
            print(f"OHLCV数据获取成功 (获取了 {len(ohlcv_data)} 条记录).")
        else:
            print(f"错误: 获取OHLCV数据失败。响应: {ohlcv_response.get('error', ohlcv_response)}")
            errors_occurred = True
        
        if depth_response.get('status') == 'success' and depth_response.get('data'):
            depth_data = depth_response['data']
            print("深度数据获取成功。")
        else:
            print(f"错误: 获取深度数据失败。响应: {depth_response.get('error', depth_response)}")
            errors_occurred = True

        if latest_price_response.get('status') == 'success' and latest_price_response.get('data'):
            latest_price_data = latest_price_response['data']
            print(f"最新价格获取成功: {latest_price_data.get('price')}")
        else:
            print(f"错误: 获取最新价格失败。响应: {latest_price_response.get('error', latest_price_response)}")
            errors_occurred = True
            
        if not errors_occurred:
            fetched_all_data_successfully = True
            market_data_dict = {
                "symbol": user_symbol,
                "lbank_symbol": lbank_symbol,
                "interval": default_interval_display,
                "ohlcv": ohlcv_data,
                "depth": depth_data,
                "latest_price": latest_price_data
            }
        else:
            print("\n--- 数据获取失败 ---")
            user_choice = input("一个或多个数据获取请求失败。您想: \n1. 重试 (retry)\n2. 退出脚本 (exit)\n3. 使用虚拟数据继续 (dummy)\n请输入您的选择 (1, 2, or 3): ").strip().lower()
            if user_choice in ["1", "retry"]:
                print("将重试数据获取...")
                time.sleep(1) # Brief pause before retrying
                continue
            elif user_choice in ["2", "exit"]:
                print("脚本已退出。")
                sys.exit(1)
            elif user_choice in ["3", "dummy"]:
                print("将使用虚拟数据继续。")
                market_data_dict = _generate_dummy_data(user_symbol, lbank_symbol, default_interval_display)
                fetched_all_data_successfully = True # Proceed with dummy data
            else:
                print("无效选择，脚本将退出。")
                sys.exit(1)

    # Write fetched data to file
    print(f"\n--- 正在将获取的市场数据写入文件: {args.fetched_data_file} ---")
    try:
        with open(args.fetched_data_file, "w") as f:
            json.dump(market_data_dict, f, indent=2)
        print(f"市场数据已成功保存到 {args.fetched_data_file}")
    except IOError as e:
        print(f"错误: 无法将市场数据写入文件 {args.fetched_data_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Pass the correct input file to the calculate_indicators script
    indicator_script_args = ["--input_file", args.fetched_data_file, "--output_file", args.indicators_file]
    if not run_script(SCRIPTS["calculate_indicators"], indicator_script_args):
        print("Pipeline failed at technical indicator calculation.", file=sys.stderr)
        sys.exit(1)

    # Update arguments for the generate_prompt script
    # It needs the path to the indicators file and the prompt template
    prompt_gen_args = [
        "--kline_file", args.indicators_file, # This should be the output from calculate_indicators
        "--depth_file", args.fetched_data_file, # Depth data is in the fetched_market_data.json
        "--price_file", args.fetched_data_file, # Latest price is also in fetched_market_data.json
        "--template_file", args.prompt_template_file,
        "--output_file", args.final_prompt_file,
        "--symbol", user_symbol # Pass the user-friendly symbol
    ]
    if not run_script(SCRIPTS["generate_prompt"], prompt_gen_args):
        print("Pipeline failed at LLM prompt generation.", file=sys.stderr)
        sys.exit(1)

    gemini_args = [
        "--prompt_file", args.final_prompt_file,
        "--output_file", args.report_file,
        # Pass API keys if they were provided as args, otherwise Gemini script will use env vars
    ]
    if args.gemini_api_key: # Ensure GEMINI_API_KEY is passed if set by arg
        gemini_args.extend(["--api_key", args.gemini_api_key])
        
    if not run_script(SCRIPTS["run_gemini"], gemini_args):
        print("Pipeline failed at Gemini report generation.", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Full pipeline executed successfully! Report saved to {args.report_file} ---")
    print(f"注意: 此报告使用LBank交易所数据生成 (来自 {lbank_symbol} / {default_interval_display})，包含深度市场数据分析。")
    
    # Provide information about the signature method used
    if args.lbank_api_key and args.lbank_api_secret:
        if is_rsa_private_key(args.lbank_api_secret):
            print("本次分析使用了RSA签名方式访问LBank API。")
        else:
            print("本次分析使用了HMAC-SHA256签名方式访问LBank API。")

if __name__ == "__main__":
    main()
