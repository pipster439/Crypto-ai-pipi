# 全面加密货币量化分析报告自动化流程 (Python 跨平台版)

## 概述

本项目旨在通过结合 CoinW API (通过 CCXT 库)、技术指标计算库 (pandas-ta) 和 Google Gemini 大语言模型 (通过其函数调用功能)，实现一个自动化的、可跨平台运行的加密货币量化分析报告生成流程。用户提供 API 密钥和分析模板，系统将自动获取市场数据、计算技术指标、构建提示，并调用 Gemini 生成详细的分析报告。

核心流程由 `main_pipeline.py` 脚本统一调度，该脚本确保了在不同操作系统（如 Windows, macOS, Linux, Android (Termux/Pydroid)）上具有良好兼容性。

## 文件结构与说明

-   `main_pipeline.py`: **核心执行脚本**。负责按顺序调用其他子脚本，处理参数，并管理整个报告生成流程。支持通过命令行参数配置交易对、API密钥和文件路径。
-   `coinw_functions_for_gemini.py`: 定义了从 CoinW 获取市场数据 (OHLCV、资金费率、多空比) 的 Python 函数，这些函数通过 CCXT 库实现，并包含了相应的 Google Gemini 函数调用声明。API 密钥在此文件中配置（建议通过环境变量）。
-   `calculate_technical_indicators.py`: 接收原始 OHLCV 数据，使用 `pandas-ta` 库计算各种标准技术指标 (如 RSI, MACD, BBands, MAs, KDJ, OBV, MFI, A/D Line 等)，并将结果（包含原始数据和所有指标）保存为 JSON 文件 (`ohlcv_with_all_indicators.json`)。
-   `user_llm_prompt_template_v2.md`: 用户提供的详细 LLM 提示模板，其中包含用于注入市场数据和分析结果的占位符 `[---INSERT FETCHED MARKET DATA HERE---]`。此版本优化了AI角色，使其专注于解读本地计算的指标并进行高级分析。
-   `generate_final_llm_prompt.py`: 读取 `user_llm_prompt_template_v2.md`、`fetched_market_data.json` 和 `ohlcv_with_all_indicators.json`，将市场数据和指标摘要动态填充到提示模板中，生成最终的、可供 Gemini 使用的完整提示文件 (`final_llm_prompt_for_gemini.md`)。
-   `run_gemini_report_generation_fc.py`: 调用 Google Gemini API (支持函数调用) 生成最终的分析报告。它读取最终的提示文件，与 Gemini 模型交互，并最终生成分析报告。
-   `fetched_market_data.json`: (示例/运行时生成) 从 `coinw_functions_for_gemini.py` 中函数获取的原始市场数据（OHLCV、资金费率等）的 JSON 格式。如果此文件不存在，`main_pipeline.py` 会根据 `--symbol` 参数创建一个包含该交易对的虚拟版本，该版本可能在 Gemini 函数调用时被实际数据覆盖。
-   `ohlcv_with_all_indicators.json`: (示例/运行时生成) `calculate_technical_indicators.py` 处理原始数据后生成的、包含所有计算指标的 JSON 数据。
-   `final_llm_prompt_for_gemini.md`: (示例/运行时生成) 经过 `generate_final_llm_prompt.py` 处理后，准备发送给 Gemini API 的完整提示内容。
-   `gemini_fc_generated_report_main_pipeline.md`: (示例/运行时生成) 由 `main_pipeline.py` 流程通过 Gemini API 生成的最终分析报告。
-   `README.md`: 本说明文件。
-   `cross_platform_python_workflow_todo.md`: (开发记录) 任务执行过程中的详细待办事项列表。

## 环境设置与依赖安装 (跨平台通用)

1.  **Python 版本**: 强烈建议使用 Python 3.9 或更高版本 (脚本测试基于 Python 3.11)。确保 Python 已添加到您的系统 PATH。
    *   **Windows**: 从 [python.org](https://www.python.org/downloads/windows/) 下载并安装，勾选 "Add Python to PATH"。
    *   **macOS**: 通常预装 Python。可通过 Homebrew (`brew install python3`) 或从 [python.org](https://www.python.org/downloads/macos/) 安装最新版。
    *   **Linux**: 大多数发行版预装 Python。可通过包管理器安装 (如 `sudo apt update && sudo apt install python3 python3-pip` for Debian/Ubuntu)。
    *   **Android (Termux)**: 打开 Termux, 运行 `pkg install python python-pip`。
2.  **安装依赖库**: 打开您的终端或命令行工具，导航到项目根目录 (包含 `main_pipeline.py` 的目录)，然后运行以下命令安装必要的 Python 库：
    ```bash
    pip install google-generativeai pandas pandas-ta ccxt requests tabulate
    ```
    或者 (如果 `pip3` 是您的 Python 3 pip 命令):
    ```bash
    pip3 install google-generativeai pandas pandas-ta ccxt requests tabulate
    ```
3.  **API 密钥配置**:
    *   **Google Gemini API Key**: **必须配置**。将您的 Gemini API 密钥设置为环境变量 `GEMINI_API_KEY`，或者在运行 `main_pipeline.py` 时通过 `--gemini_api_key` 参数提供。
        *   **Windows (PowerShell)**: `$env:GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"` (临时, 当前会话)
        *   **Windows (CMD)**: `set GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY` (临时, 当前会话)
        *   **macOS/Linux/Termux (Bash/Zsh)**: `export GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"` (临时, 当前会话)
        *   为永久设置，请将上述命令添加到您的 shell 配置文件中 (如 `.bashrc`, `.zshrc`, 或通过系统环境变量设置)。
    *   **CoinW API Keys**: (可选, 如果需要 Gemini 函数调用实时获取最新数据，并且 `fetched_market_data.json` 不存在或不包含目标交易对的最新数据)。在 `coinw_functions_for_gemini.py` 文件顶部，或通过环境变量 `COINW_API_KEY` 和 `COINW_API_SECRET` 配置您的 CoinW API 公钥和私钥。脚本中已包含用户提供的测试密钥作为默认值，但强烈建议替换为您自己的密钥以进行实际操作。

## 运行流程 (使用 `main_pipeline.py`)

**核心命令 (在项目根目录下运行):**

```bash
python main_pipeline.py --symbol "BTC/USDT" --gemini_api_key "YOUR_GEMINI_API_KEY_IF_NOT_SET_AS_ENV_VAR"
```
或者，如果 `python3` 是您的 Python 3 命令:
```bash
python3 main_pipeline.py --symbol "BTC/USDT"
```
(此命令假设 `GEMINI_API_KEY` 已设置为环境变量)

**`main_pipeline.py` 脚本参数说明:**

*   `--gemini_api_key`: (可选) 您的 Google Gemini API 密钥。如果已设置为环境变量 `GEMINI_API_KEY`，则无需提供。
*   `--symbol`: (可选) 您希望分析的交易对，格式通常为 `BASE/QUOTE`，例如 `BTC/USDT`, `ETH/BTC`。默认为 `BTC/USDT`。此参数主要用于在 `fetched_market_data.json` 文件不存在时，创建一个包含此交易对的初始虚拟数据文件。实际数据获取将由 Gemini 的函数调用机制（调用 `coinw_functions_for_gemini.py`）根据 LLM 的理解和函数声明来执行，理论上会优先使用 LLM 理解到的交易对。
*   `--fetched_data_file`: (可选) 原始市场数据 JSON 文件的路径。默认为 `./fetched_market_data.json` (相对于脚本位置)。
*   `--indicators_file`: (可选) 技术指标输出 JSON 文件的路径。默认为 `./ohlcv_with_all_indicators.json`。
*   `--final_prompt_file`: (可选) 最终 LLM 提示 Markdown 文件的路径。默认为 `./final_llm_prompt_for_gemini.md`。
*   `--report_file`: (可选) 最终生成的分析报告 Markdown 文件的路径。默认为 `./gemini_fc_generated_report_main_pipeline.md`。
*   `--prompt_template_file`: (可选) LLM 提示模板文件的路径。默认为 `./user_llm_prompt_template_v2.md`。

**执行流程概述:**

1.  `main_pipeline.py` 检查 `fetched_market_data.json` 是否存在。如果不存在，会根据 `--symbol` 参数创建一个包含虚拟 OHLCV 数据的版本，以便后续脚本可以运行。这个虚拟数据旨在让流程能够启动，实际数据通常会在 Gemini 函数调用阶段被获取和更新。
2.  调用 `calculate_technical_indicators.py`，它读取 `fetched_market_data.json` 并计算技术指标，保存到 `ohlcv_with_all_indicators.json`。
3.  调用 `generate_final_llm_prompt.py`，它结合 `user_llm_prompt_template_v2.md`、`fetched_market_data.json` 和 `ohlcv_with_all_indicators.json` 生成最终的提示 `final_llm_prompt_for_gemini.md`。
4.  调用 `run_gemini_report_generation_fc.py`，它使用 `final_llm_prompt_for_gemini.md` 和配置的 Gemini API 密钥与 Gemini 模型交互。此步骤可能涉及函数调用（执行 `coinw_functions_for_gemini.py` 中的函数）来获取最新的市场数据。最终生成的报告保存到 `--report_file` 指定的路径。

## 注意事项与跨平台兼容性

*   **相对路径**: 所有脚本均设计为使用相对路径（相对于脚本自身的位置），这使得将整个项目文件夹移动到不同位置或不同系统上时，脚本依然能够正确找到依赖文件和子脚本。
*   **Python 环境**: 确保在所有目标平台上都安装了兼容的 Python 版本和所有必要的库（见“依赖安装”部分）。
*   **文件编码**: 所有文本文件（如 `.md`, `.py`, `.json`）建议使用 UTF-8 编码以避免跨平台问题。
*   **CCXT 数据获取**: `coinw_functions_for_gemini.py` 中的数据获取依赖 CCXT 库。请确保 CCXT 支持您希望查询的 CoinW 交易对和数据类型。资金费率、多空比等数据并非所有交易所都通过 CCXT 标准化支持。
*   **LLM 提示质量**: `user_llm_prompt_template_v2.md` 的质量直接影响最终报告的质量。您可以根据需要调整此模板。
*   **错误处理**: 脚本中包含基本的错误处理。在实际生产使用中，可能需要根据具体情况进行增强。

## 未来可扩展方向

*   更复杂的错误处理和重试机制。
*   支持更多交易所和数据源，通过参数配置。
*   在本地实现更多高级技术分析的初步识别，减轻 LLM 的计算负担。
*   提供一个简单的图形用户界面 (GUI) 或 Web 界面进行参数配置和流程触发。
*   报告结果的自动可视化（如图表嵌入）。

