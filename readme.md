# LBank加密货币量化分析报告自动化流程

本项目是一个基于Python的自动化工具，用于生成加密货币的量化分析报告。它使用LBank交易所API获取市场数据（包括深度数据），计算技术指标，并利用Google Gemini AI生成专业的分析报告。

## 功能特点

- 从LBank交易所获取加密货币的OHLCV数据、深度数据和最新价格
- 支持HMAC-SHA256和RSA两种签名方式（优先使用SHA256，自动检测RSA私钥）
- 计算多种技术指标（RSI、MACD、布林带等）
- 利用Google Gemini AI生成包含高级技术分析的专业报告
- 支持通过交互式输入选择交易对
- 完全基于Python，跨平台兼容

## 环境设置与依赖安装

### 必要的Python库

```bash
pip install ccxt google-generativeai pandas numpy tabulate matplotlib pycryptodome panda_ta
```

### API密钥设置

1. **Google Gemini API密钥**（必需）：
   - 在[Google AI Studio](https://ai.google.dev/)注册并获取API密钥
   - 设置环境变量：`export GEMINI_API_KEY="your_api_key_here"`

2. **LBank API密钥**（可选，用于访问私有API）：
   - 在[LBank官网](https://www.lbank.com/)注册并创建API密钥
   - 设置环境变量：
     ```bash
     export LBANK_API_KEY="your_api_key_here"
     export LBANK_API_SECRET="your_api_secret_here"
     ```
   - 注意：LBANK_API_SECRET可以是HMAC-SHA256密钥或RSA私钥，系统会自动检测并使用相应的签名方式

## 使用方法

1. 解压下载的`lbank_crypto_analysis_project.zip`文件
2. 进入解压后的目录
3. 运行主脚本：

```bash
python main_pipeline_lbank_with_rsa.py
```

4. 按提示输入要分析的交易对（例如：`btc_usdt`或`BTC/USDT`）
5. 等待脚本完成数据获取、指标计算和报告生成
6. 查看生成的报告文件（默认为`gemini_fc_generated_report_lbank.md`）

## 主要文件说明

- `main_pipeline_lbank_with_rsa.py`：主流程脚本，协调整个分析过程
- `lbank_functions_for_gemini_with_rsa.py`：LBank API数据获取函数，支持两种签名方式
- `calculate_technical_indicators.py`：技术指标计算脚本
- `generate_final_llm_prompt.py`：生成AI提示的脚本
- `run_gemini_report_generation_fc_lbank.py`：调用Gemini API生成报告
- `user_llm_prompt_template_lbank.md`：报告生成的模板，包含深度数据分析部分

## 签名方式说明

本工具支持两种LBank API签名方式：

1. **HMAC-SHA256签名**（默认）：
   - 适用于标准API密钥
   - 格式为普通字符串，如`"your_secret_key"`
   - 系统默认使用此方式

2. **RSA签名**：
   - 适用于RSA验证方式生成的API密钥（无需绑定IP）
   - 格式为RSA私钥，通常以`"-----BEGIN RSA PRIVATE KEY-----"`开头
   - 系统会自动检测RSA私钥格式并切换签名方式

系统会根据提供的`LBANK_API_SECRET`格式自动选择合适的签名方式，无需手动指定。

## 自定义选项

主脚本支持以下命令行参数：

```
--gemini_api_key：指定Gemini API密钥（也可通过环境变量设置）
--lbank_api_key：指定LBank API密钥（也可通过环境变量设置）
--lbank_api_secret：指定LBank API密钥（也可通过环境变量设置）
--report_file：指定输出报告的文件路径
```

例如：

```bash
python main_pipeline_lbank_with_rsa.py --report_file my_custom_report.md
```

## 注意事项

- 本工具使用公共API获取基本市场数据，不需要API密钥
- 如需访问私有API或更高频率的请求，建议配置LBank API密钥
- 生成的报告仅供参考，不构成任何投资建议
- 在使用前请确保您的Gemini API密钥有效
- 使用RSA签名方式时，请确保提供完整的RSA私钥

## 故障排除

- 如遇到API连接问题，请检查网络连接和API密钥
- 如果报告生成失败，请检查Gemini API密钥是否有效
- 对于不常见的交易对，可能需要使用确切的LBank格式（如`btc_usdt`）
- 如果RSA签名失败，请确保您的私钥格式正确，必要时可手动添加PEM头尾

## 跨平台兼容性

本工具在以下环境中测试通过：
- Windows 10/11
- macOS
- Linux (Ubuntu)
- 可通过Termux在Android上运行

该工具旨在实现跨平台兼容性。

注意：如果您直接运行项目中的某些独立脚本（例如 `calculate_technical_indicators.py`），请注意其示例用法部分现在使用相对路径来引用示例数据文件。
