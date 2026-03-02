---
name: model-cost-tracker
description: Track AI model costs with budget limits. Monitor usage across OpenAI, Anthropic, Google, DeepSeek, Qwen, MiniMax and more. Features: real-time cost calculation, daily/monthly budgets with alerts, usage reports, and automatic cheaper model suggestions. Trigger when managing AI spending or setting cost thresholds.
---

# Model Cost Tracker

## Overview

A comprehensive cost tracking and budget management system for AI model usage. Tracks every model call, calculates real-time costs, and enforces budget-based access policies.

## Features

1. **Usage Tracking**: Log every model call with timestamp, model name, tokens used
2. **Cost Calculation**: Real-time cost computation based on current market rates
3. **Budget Management**: Set daily/monthly budgets with threshold alerts
4. **Access Control**: Automatically block or warn when approaching limits
5. **Reporting**: Generate usage reports and cost breakdowns

## Quick Start

### Track a model call
```python
python {baseDir}/scripts/track_usage.py --model gpt-4 --input-tokens 1000 --output-tokens 500
```

### Check current costs
```python
python {baseDir}/scripts/cost_report.py --period today
python {baseDir}/scripts/cost_report.py --period month
```

### Set budget limit
```python
python {baseDir}/scripts/set_budget.py --daily 10.00 --monthly 100.00
```

### Check budget status (enforces policies)
```python
python {baseDir}/scripts/check_budget.py --model gpt-4 --estimated-cost 0.50
```

## Data Storage

- Usage logs: `~/.openclaw/workspace/logs/model_usage.jsonl`
- Budget config: `~/.openclaw/workspace/config/model_budget.json`
- Cost rates: See `references/pricing_reference.md`

## Cost Calculation

Pricing data stored in `references/pricing_reference.json`:
- Input/output token prices per model
- Cached input discounts
- Currency: USD per 1M tokens

## Budget Policies

### Threshold Levels

| Level | Percentage | Action |
|-------|-----------|--------|
| Normal | < 70% | Allow all requests |
| Warning | 70-85% | Warn user, suggest cheaper alternatives |
| Critical | 85-95% | Require confirmation for expensive models |
| Exceeded | > 95% | Block expensive models, allow only cheap/free |

### Alternative Model Suggestions

When budget is tight, suggest cheaper alternatives:
- GPT-4 → GPT-3.5 or DeepSeek V3
- Claude Opus → Claude Sonnet or Qwen Turbo
- Gemini Pro → Gemini Flash

## Integration with OpenClaw

The skill can be integrated into the request pipeline:

```python
# Before making a model call
check = subprocess.run([
    "python", "{baseDir}/scripts/check_budget.py",
    "--model", selected_model,
    "--estimated-input", str(input_tokens),
    "--estimated-output", str(output_tokens)
], capture_output=True, text=True)

if "BLOCKED" in check.stdout:
    # Suggest alternative or ask user
    pass
```

## Commands Reference

### track_usage.py
Log a model usage event.
```
--model MODEL_NAME          Model identifier
--input-tokens N           Input token count
--output-tokens N          Output token count  
--timestamp ISO8601        Optional timestamp (default: now)
--metadata JSON            Optional metadata
```

### cost_report.py
Generate cost reports.
```
--period {today,week,month,custom}  Report period
--start-date YYYY-MM-DD            Custom start date
--end-date YYYY-MM-DD              Custom end date
--format {text,json,csv}           Output format
--group-by {model,day,provider}    Grouping option
```

### set_budget.py
Configure budget limits.
```
--daily AMOUNT             Daily budget in USD
--monthly AMOUNT           Monthly budget in USD
--alert-threshold PERCENT  Alert at % of budget (default: 80)
```

### check_budget.py
Check if a request should be allowed.
```
--model MODEL              Model being requested
--estimated-cost AMOUNT    Estimated cost of request
--action {check,enforce}   Just check or enforce policy
```

## Model Pricing

See `references/pricing_reference.json` for current rates.
Key models tracked:
- OpenAI: GPT-4, GPT-3.5 series
- Anthropic: Claude Opus, Sonnet, Haiku
- Google: Gemini Pro, Flash
- DeepSeek: V3, R1
- Alibaba: Qwen series
- MiniMax: M2.5

## Tips

- Run cost reports weekly to identify expensive patterns
- Set alerts at 70% to avoid surprises
- Use cheaper models for drafts, expensive for final review
- Track metadata to correlate costs with specific projects
