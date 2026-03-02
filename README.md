---
name: model-cost-tracker
description: Track AI model usage costs, calculate real-time expenses, and enforce budget-based access policies. Use when users need to (1) monitor AI model usage and costs across providers, (2) set daily/monthly budget limits with threshold alerts, (3) generate cost reports and analytics, (4) get alerts when approaching budget limits, (5) analyze which models are most expensive, or (6) implement automatic model switching based on cost constraints. Works with all major providers including OpenAI, Anthropic, Google, DeepSeek, Alibaba (Qwen), MiniMax, Moonshot (Kimi), and more. Supports cost calculation, budget enforcement, and cheaper alternative recommendations.
---

# Model Cost Tracker

## Overview

A comprehensive cost tracking and budget management system for AI model usage. Monitor every API call, calculate real-time costs, enforce budget limits, and automatically suggest cheaper alternatives when budgets are tight.

## Features

- **📊 Usage Tracking**: Log every model call with timestamp, provider, token counts, and metadata
- **💰 Cost Calculation**: Real-time cost computation based on up-to-date pricing for 20+ models
- **🎯 Budget Management**: Set daily/monthly budgets with configurable alert thresholds (70%/85%/95%)
- **🚦 Access Control**: Enforce policies - warn at 80%, require confirmation at 95%, block at 100%
- **💡 Smart Alternatives**: Automatically suggest cheaper models when budgets are tight
- **📈 Reporting**: Generate detailed cost reports by model, day, or provider (text/JSON/CSV)

## Quick Start

### Set Budget Limits
```bash
python scripts/set_budget.py --daily 10.00 --monthly 100.00 --alert-threshold 80
```

### Track Model Usage
```bash
python scripts/track_usage.py --model gpt-4o --input-tokens 2000 --output-tokens 500
```

### Generate Cost Reports
```bash
python scripts/cost_report.py --period today    # Today
python scripts/cost_report.py --period week     # Last 7 days
python scripts/cost_report.py --period month    # Last 30 days
python scripts/cost_report.py --format json     # JSON output
python scripts/cost_report.py --format csv      # CSV export
```

### Check Budget Before Calling
```bash
python scripts/check_budget.py --model gpt-4o --estimated-input 10000 --estimated-output 5000
```

## Supported Models

### OpenAI
- GPT-5.2 Pro ($21.00/$168.00 per 1M tokens)
- GPT-5.2 ($1.75/$14.00 per 1M tokens)
- GPT-5 Mini ($0.25/$2.00 per 1M tokens)
- GPT-4.1 ($3.00/$12.00 per 1M tokens)
- GPT-4o ($2.50/$10.00 per 1M tokens)
- GPT-4o Mini ($0.15/$0.60 per 1M tokens)
- GPT-3.5 Turbo ($0.50/$1.50 per 1M tokens)

### Anthropic
- Claude Opus 4.6 ($15.00/$75.00 per 1M tokens)
- Claude Sonnet 4.6 ($3.00/$15.00 per 1M tokens)
- Claude Haiku 4.5 ($0.25/$1.25 per 1M tokens)

### Google
- Gemini 3.1 Pro ($3.50/$10.50 per 1M tokens)
- Gemini 2.5 Flash ($0.15/$0.60 per 1M tokens)

### Chinese Models
- **DeepSeek V3** ($0.14/$0.28 per 1M tokens) ⭐ Best Value
- **DeepSeek R1** ($0.55/$2.19 per 1M tokens)
- **Qwen 2.5 Max** ($0.80/$2.40 per 1M tokens)
- **Qwen 2.5 Turbo** ($0.20/$0.60 per 1M tokens)
- **Qwen 2.5 72B** ($0.15/$0.45 per 1M tokens)
- **MiniMax M2.5** ($0.30/$1.20 per 1M tokens)
- **Kimi K2.5** ($0.50/$2.00 per 1M tokens)
- **GLM-5** ($0.40/$1.30 per 1M tokens)

### Others
- Grok 2 ($5.00/$15.00 per 1M tokens)
- Llama 3 (Open source - self-hosted)

## Budget Policy Levels

| Level | Usage % | Action | Description |
|-------|---------|--------|-------------|
| **Normal** | < 70% | ✅ Allow | All requests permitted |
| **Warning** | 70-85% | ⚠️ Warn | Alert user, suggest alternatives |
| **Critical** | 85-95% | 🔶 Confirm | Expensive models require confirmation |
| **Exceeded** | > 95% | ❌ Block | Block expensive models, allow cheap/free only |

## Smart Alternative Suggestions

When budgets are tight, automatically suggest cheaper alternatives:

| Expensive Model | Suggested Alternatives |
|-----------------|------------------------|
| GPT-5.2 Pro | GPT-5.2, DeepSeek V3, Qwen Turbo |
| Claude Opus 4.6 | Claude Sonnet, DeepSeek V3, Qwen Turbo |
| GPT-5.2 | GPT-5 Mini, DeepSeek V3, Gemini Flash |
| GPT-4o | GPT-4o Mini, DeepSeek V3, Qwen Turbo |

## Data Storage

| File | Path | Description |
|------|------|-------------|
| Usage Logs | `~/.openclaw/workspace/logs/model_usage.jsonl` | JSONL format, one entry per call |
| Budget Config | `~/.openclaw/workspace/config/model_budget.json` | Budget limits and thresholds |
| Pricing Data | `references/pricing_reference.json` | Current pricing for all models |

## Integration Examples

### Python Integration

```python
import subprocess
import json

def track_model_call(model, input_tokens, output_tokens):
    """Track a model usage event."""
    result = subprocess.run([
        "python", "scripts/track_usage.py",
        "--model", model,
        "--input-tokens", str(input_tokens),
        "--output-tokens", str(output_tokens)
    ], capture_output=True, text=True)
    return result.returncode == 0

def check_budget(model, estimated_cost):
    """Check if request is within budget."""
    result = subprocess.run([
        "python", "scripts/check_budget.py",
        "--model", model,
        "--estimated-cost", str(estimated_cost),
        "--format", "json"
    ], capture_output=True, text=True)
    
    status = json.loads(result.stdout)
    return status["action"] == "allow", status

# Example workflow
def call_model_safely(model, prompt, max_input_tokens=10000):
    # Estimate cost
    estimated_output = 2000
    
    # Check budget
    allowed, status = check_budget(model, 0)  # Will calculate actual cost
    
    if not allowed:
        print(f"Budget exceeded: {status['message']}")
        print(f"Alternatives: {status['alternatives']}")
        return None
    
    # Call your actual model here
    # response = your_model_api.call(model, prompt)
    
    # Track usage after call
    # track_model_call(model, input_tokens, output_tokens)
    
    return response
```

### Shell Integration

```bash
#!/bin/bash
# budget-aware-model-call.sh

MODEL="$1"
INPUT_TOKENS="$2"
OUTPUT_TOKENS="$3"

# Check budget before calling
check_result=$(python ~/.openclaw/workspace/skills/model-cost-tracker/scripts/check_budget.py \
    --model "$MODEL" \
    --estimated-input "$INPUT_TOKENS" \
    --estimated-output "$OUTPUT_TOKENS" \
    --action enforce)

if [ $? -ne 0 ]; then
    echo "Request blocked: $check_result"
    exit 1
fi

# Call your model API here
echo "Calling $MODEL with $INPUT_TOKENS input tokens..."

# Track usage after call
python ~/.openclaw/workspace/skills/model-cost-tracker/scripts/track_usage.py \
    --model "$MODEL" \
    --input-tokens "$INPUT_TOKENS" \
    --output-tokens "$OUTPUT_TOKENS"
```

## Command Reference

### track_usage.py
```
--model MODEL_NAME          Model identifier (required)
--input-tokens N           Input token count (required)
--output-tokens N          Output token count (required)
--timestamp ISO8601        Optional timestamp (default: now)
--metadata JSON            Optional metadata as JSON string
```

### cost_report.py
```
--period {today,week,month,custom}  Report period
--start-date YYYY-MM-DD            Custom start date
--end-date YYYY-MM-DD              Custom end date
--format {text,json,csv}           Output format (default: text)
--group-by {model,day,provider}    Grouping option (default: model)
```

### set_budget.py
```
--daily AMOUNT             Daily budget limit in USD
--monthly AMOUNT           Monthly budget limit in USD
--alert-threshold PERCENT  Alert percentage (default: 80)
--show                     Display current configuration
```

### check_budget.py
```
--model MODEL              Model being requested
--estimated-cost AMOUNT    Estimated cost of request (optional)
--estimated-input N        Estimated input tokens (optional)
--estimated-output N       Estimated output tokens (optional)
--action {check,enforce}   Just check or enforce policy (default: check)
--format {text,json}       Output format (default: text)
```

## Best Practices

1. **Set Conservative Budgets**: Start with 50% of your expected usage
2. **Use Alerts**: Set threshold at 70% to get early warnings
3. **Track Metadata**: Add project/context metadata to analyze costs by use case
4. **Review Weekly**: Run reports weekly to identify expensive patterns
5. **Use Alternatives**: Accept suggested cheaper models when budgets are tight
6. **Batch Operations**: Use Batch API discounts where available (50% off)

## Example Workflow

```bash
# 1. Configure budget
python scripts/set_budget.py --daily 5.00 --monthly 50.00

# 2. Track multiple calls
python scripts/track_usage.py --model gpt-4o --input-tokens 50000 --output-tokens 10000
python scripts/track_usage.py --model deepseek-v3 --input-tokens 100000 --output-tokens 25000
python scripts/track_usage.py --model claude-sonnet-4-6 --input-tokens 30000 --output-tokens 8000

# 3. Check today's spending
python scripts/cost_report.py --period today

# 4. Check if expensive request is allowed
python scripts/check_budget.py --model gpt-5.2-pro --estimated-input 20000 --estimated-output 5000

# 5. Export monthly report
python scripts/cost_report.py --period month --format csv > costs_$(date +%Y-%m).csv
```

## Troubleshooting

### Unicode errors on Windows
If you see encoding errors, set console to UTF-8:
```cmd
chcp 65001
```

### Unknown model warnings
Add new models to `references/pricing_reference.json`:
```json
"new-model": {
    "input": 0.50,
    "output": 1.50,
    "currency": "USD",
    "unit": "per_1m_tokens"
}
```

### Missing log file
The skill automatically creates directories. If tracking fails, manually create:
```bash
mkdir -p ~/.openclaw/workspace/logs
mkdir -p ~/.openclaw/workspace/config
```

## Contributing

To add new models or update pricing:
1. Edit `references/pricing_reference.json`
2. Update `alternatives` section for smart suggestions
3. Test with `track_usage.py`
4. Repackage skill with `package_skill.py`

## License

MIT License - Free for personal and commercial use.

## Author

Created for OpenClaw - AI cost management made simple.

---

**Version**: 1.0.0  
**Last Updated**: 2026-03-02  
**Pricing Data Updated**: 2026-03-02
