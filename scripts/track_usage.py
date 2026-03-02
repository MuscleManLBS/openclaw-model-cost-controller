#!/usr/bin/env python3
"""
Track AI model usage and log to JSONL file.
Usage: python track_usage.py --model gpt-4 --input-tokens 1000 --output-tokens 500
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

def get_log_path():
    """Get the path for usage log file."""
    workspace = Path.home() / ".openclaw" / "workspace"
    logs_dir = workspace / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / "model_usage.jsonl"

def load_pricing():
    """Load pricing data from reference file."""
    skill_dir = Path(__file__).parent.parent
    pricing_file = skill_dir / "references" / "pricing_reference.json"
    
    if pricing_file.exists():
        with open(pricing_file, 'r') as f:
            return json.load(f)
    return {"models": {}}

def calculate_cost(model, input_tokens, output_tokens, pricing_data):
    """Calculate cost for a model usage."""
    model_lower = model.lower()
    
    # Search for model in pricing data
    for provider, models in pricing_data.get("models", {}).items():
        for model_name, rates in models.items():
            if model_lower in model_name.lower() or model_name.lower() in model_lower:
                input_cost = (input_tokens / 1_000_000) * rates["input"]
                output_cost = (output_tokens / 1_000_000) * rates["output"]
                return {
                    "input_cost": round(input_cost, 6),
                    "output_cost": round(output_cost, 6),
                    "total_cost": round(input_cost + output_cost, 6),
                    "currency": rates.get("currency", "USD")
                }
    
    # Unknown model
    return {
        "input_cost": 0,
        "output_cost": 0,
        "total_cost": 0,
        "currency": "USD",
        "warning": f"Unknown model: {model}"
    }

def track_usage(model, input_tokens, output_tokens, timestamp=None, metadata=None):
    """Track a model usage event."""
    pricing_data = load_pricing()
    cost_info = calculate_cost(model, input_tokens, output_tokens, pricing_data)
    
    entry = {
        "timestamp": timestamp or datetime.now().isoformat(),
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost_info,
        "metadata": metadata or {}
    }
    
    log_path = get_log_path()
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return entry

def main():
    parser = argparse.ArgumentParser(description='Track AI model usage')
    parser.add_argument('--model', required=True, help='Model name (e.g., gpt-4)')
    parser.add_argument('--input-tokens', type=int, required=True, help='Input token count')
    parser.add_argument('--output-tokens', type=int, required=True, help='Output token count')
    parser.add_argument('--timestamp', help='ISO timestamp (default: now)')
    parser.add_argument('--metadata', help='JSON metadata string')
    
    args = parser.parse_args()
    
    metadata = None
    if args.metadata:
        metadata = json.loads(args.metadata)
    
    entry = track_usage(
        model=args.model,
        input_tokens=args.input_tokens,
        output_tokens=args.output_tokens,
        timestamp=args.timestamp,
        metadata=metadata
    )
    
    print(f"[OK] Tracked usage for {args.model}")
    print(f"   Input: {args.input_tokens:,} tokens")
    print(f"   Output: {args.output_tokens:,} tokens")
    print(f"   Cost: ${entry['cost']['total_cost']:.6f} {entry['cost']['currency']}")
    
    if 'warning' in entry['cost']:
        print(f"   [WARN] {entry['cost']['warning']}")

if __name__ == "__main__":
    main()
