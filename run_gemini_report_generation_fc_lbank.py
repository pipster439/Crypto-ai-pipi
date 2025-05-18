import google.generativeai as genai
import json
import argparse
import os
import sys

# Ensure the directory containing lbank_functions_for_gemini can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Attempt to import the functions and their declarations
try:
    from lbank_functions_for_gemini import (
        GET_LBANK_OHLCV_DATA_DECLARATION,
        GET_LBANK_DEPTH_DATA_DECLARATION,
        GET_LBANK_TICKER_DATA_DECLARATION,
        GET_LBANK_LATEST_PRICE_DECLARATION,
        GET_LBANK_RECENT_TRADES_DECLARATION,
        get_lbank_ohlcv_data,
        get_lbank_depth_data,
        get_lbank_ticker_data,
        get_lbank_latest_price,
        get_lbank_recent_trades
    )
    AVAILABLE_FUNCTIONS = {
        "get_lbank_ohlcv_data": get_lbank_ohlcv_data,
        "get_lbank_depth_data": get_lbank_depth_data,
        "get_lbank_ticker_data": get_lbank_ticker_data,
        "get_lbank_latest_price": get_lbank_latest_price,
        "get_lbank_recent_trades": get_lbank_recent_trades
    }
    TOOL_DECLARATIONS = [
        GET_LBANK_OHLCV_DATA_DECLARATION,
        GET_LBANK_DEPTH_DATA_DECLARATION,
        GET_LBANK_TICKER_DATA_DECLARATION,
        GET_LBANK_LATEST_PRICE_DECLARATION,
        GET_LBANK_RECENT_TRADES_DECLARATION
    ]
    print("Successfully imported LBank functions for Gemini.")
except ImportError as e:
    print(f"Error importing LBank functions: {e}. Ensure lbank_functions_for_gemini.py is in the same directory or PYTHONPATH.")
    AVAILABLE_FUNCTIONS = {}
    TOOL_DECLARATIONS = []

def read_file_content(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def generate_report_with_gemini_and_fc(
    api_key,
    prompt_file_path, # This will now be the path to the fully formed prompt
    output_file_path,
    model_name="gemini-1.5-flash-latest",
    max_function_calls=5 # Limit the number of function call rounds
):
    """Generates a report using Google Gemini API, supporting function calling."""
    genai.configure(api_key=api_key)

    # Load the fully formed prompt
    initial_prompt_content = read_file_content(prompt_file_path)
    if not initial_prompt_content:
        print(f"Failed to read initial prompt from {prompt_file_path}")
        return

    # Create the model with tools (function declarations)
    # Only pass tools if they were successfully imported
    model_tools = genai.protos.Tool(function_declarations=TOOL_DECLARATIONS) if TOOL_DECLARATIONS else None
    
    model = genai.GenerativeModel(
        model_name=model_name, 
        tools=model_tools if model_tools else None
    )
    
    chat = model.start_chat(enable_automatic_function_calling=False) # Manual control for clarity
    print(f"Sending initial prompt to Gemini API with model: {model_name}...")
    
    current_prompt = initial_prompt_content
    function_call_count = 0

    while function_call_count < max_function_calls:
        try:
            print(f"\n--- Sending to Gemini (Turn {function_call_count + 1}) ---")
            # print(f"Prompt content: {current_prompt[:300]}...") # Snippet for brevity
            response = chat.send_message(current_prompt)
            function_called = False

            for part in response.parts:
                if part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    args = dict(function_call.args)
                    print(f"Gemini requested function call: {function_name} with args: {args}")
                    function_called = True
                    function_call_count += 1

                    if function_name in AVAILABLE_FUNCTIONS:
                        api_function = AVAILABLE_FUNCTIONS[function_name]
                        try:
                            # Call the actual API function
                            api_response_data = api_function(**args)
                            print(f"Function {function_name} executed. Response: {json.dumps(api_response_data, indent=2)[:300]}...")
                            
                            # Send the function response back to Gemini
                            current_prompt = genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response=api_response_data
                            ))
                        except Exception as e:
                            print(f"Error executing function {function_name}: {e}")
                            current_prompt = genai.protos.Part(function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"error": str(e)}
                            ))
                    else:
                        print(f"Error: Unknown function requested by Gemini: {function_name}")
                        current_prompt = genai.protos.Part(function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response={"error": f"Function {function_name} is not available."}
                        ))
                    break # Process one function call per turn
            
            if not function_called:
                # No function call, this should be the final text response
                if response.parts:
                    generated_text = response.text
                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(generated_text)
                    print(f"\nReport successfully generated and saved to {output_file_path}")
                    return # End of conversation
                else:
                    print("Error: Gemini API returned an empty response or no valid parts after no function call.")
                    if hasattr(response, 'prompt_feedback'): print(f"Prompt Feedback: {response.prompt_feedback}")
                    return

        except Exception as e:
            print(f"An error occurred while interacting with the Gemini API: {e}")
            # print(f"Full API Response (if available): {response}") # For debugging
            return
        
    if function_call_count >= max_function_calls:
        print(f"Reached maximum number of function calls ({max_function_calls}). Stopping.")
        # Try to get the last text response if any
        try:
            final_text = chat.history[-1].parts[0].text if chat.history and chat.history[-1].parts else "No final text response after max function calls."
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(final_text)
            print(f"Partial report (or last available text) saved to {output_file_path}")
        except Exception as ex_save:
            print(f"Could not save final output: {ex_save}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a report using Google Gemini API with function calling.")
    parser.add_argument("--api_key", type=str, help="Your Google Gemini API Key.", required=False)
    # The prompt_file now points to the fully constructed prompt from generate_final_llm_prompt.py
    parser.add_argument("--prompt_file", type=str, default="/home/ubuntu/final_llm_prompt_for_gemini.md", help="Path to the final LLM prompt file.")
    parser.add_argument("--output_file", type=str, default="/home/ubuntu/gemini_fc_generated_report.md", help="Path to save the generated report.")
    parser.add_argument("--model", type=str, default="gemini-1.5-flash-latest", help="Gemini model to use.")
    parser.add_argument("--max_calls", type=int, default=5, help="Maximum number of function call rounds.")

    args = parser.parse_args()

    api_key = args.api_key if args.api_key else os.environ.get('GEMINI_API_KEY')

    if not api_key:
        print("Error: API Key not provided. Please use --api_key argument or set GEMINI_API_KEY environment variable.")
    elif not TOOL_DECLARATIONS or not AVAILABLE_FUNCTIONS:
        print("Error: Tool declarations or available functions for Gemini are missing. Check lbank_functions_for_gemini.py import.")
    else:
        # Before running, ensure the prompt file is generated by the previous step
        print("Ensuring the final prompt file exists...")
        # In a real pipeline, you would run: python3.11 /home/ubuntu/generate_final_llm_prompt.py
        # For now, we just check if it exists.
        if not os.path.exists(args.prompt_file):
            print(f"Error: The prompt file {args.prompt_file} does not exist. Please run generate_final_llm_prompt.py first.")
            print("You might need to run: python3.11 /home/ubuntu/calculate_technical_indicators.py first to generate its input.")
            # Attempt to run the prompt generation script if its inputs exist
            indicators_file = "/home/ubuntu/ohlcv_with_all_indicators.json"
            fetched_data_file = "/home/ubuntu/fetched_market_data.json"
            template_file = "/home/ubuntu/user_llm_prompt_template_v2.md"
            if os.path.exists(indicators_file) and os.path.exists(fetched_data_file) and os.path.exists(template_file):
                print("Attempting to generate the final prompt file now...")
                try:
                    import subprocess
                    subprocess.run(["python3.11", "/home/ubuntu/generate_final_llm_prompt.py"], check=True)
                    if not os.path.exists(args.prompt_file):
                         print(f"Error: {args.prompt_file} still not found after attempting to generate it.")
                         sys.exit(1)
                    print(f"{args.prompt_file} generated.")
                except Exception as e_gen:
                    print(f"Failed to auto-generate prompt file: {e_gen}")
                    sys.exit(1)
            else:
                print(f"Cannot auto-generate prompt file as one of its inputs is missing: {indicators_file}, {fetched_data_file}, or {template_file}")
                sys.exit(1)
        
        generate_report_with_gemini_and_fc(
            api_key,
            args.prompt_file,
            args.output_file,
            args.model,
            args.max_calls
        )
