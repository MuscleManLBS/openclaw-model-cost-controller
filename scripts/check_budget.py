#!/usr/bin/env python3
"""
Check budget status and enforce access policies.
Usage: python check_budget.py --model gpt-4 --estimated-cost 0.50
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def get_log_path():
    """Get the path for usage log file."""
    workspace = Path.home() / ".openclaw" / "workspace"
    logs_dir = workspace / "logs"
    return logs_dir / "model_usage.jsonl"

def get_config_path():
    """Get the path for budget config file."""
    workspace = Path.home() / ".openclaw" / "workspace"
    config_dir = workspace / "config"
    return config_dir / "model_budget.json"

def load_pricing():
    """Load pricing data from reference file."""
    skill_dir = Path(__file__).parent.parent
    pricing_file = skill_dir / "references" / "pricing_reference.json"
    
    if pricing_file.exists():
        with open(pricing_file, 'r') as f:
            return json.load(f)
    return {"models": {}, "alternatives": {"expensive": {}}}

def load_budget_config():
    """Load budget configuration."""
    config_path = get_config_path()
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        "daily_limit": None,
        "monthly_limit": None,
        "alert_threshold": 80
    }

def calculate_current_usage():
    """Calculate current daily and monthly usage."""
    log_path = get_log_path()
    
    if not log_path.exists():
        return {"daily": 0, "monthly": 0}
    
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    daily_cost = 0
    monthly_cost = 0
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry['timestamp']).date()
                    cost = entry['cost']['total_cost']
                    
                    if entry_date == today:
                        daily_cost += cost
                    
                    if entry_date >= month_start:
                        monthly_cost += cost
                        
                except (json.JSONDecodeError, KeyError):
                    continue
    
    return {
        "daily": round(daily_cost, 4),
        "monthly": round(monthly_cost, 4)
    }

def get_budget_status(estimated_cost=0):
    """
    Check budget status and return policy decision.
    Returns: dict with status, message, and action
    """
    config = load_budget_config()
    usage = calculate_current_usage()
    
    daily_limit = config.get("daily_limit")
    monthly_limit = config.get("monthly_limit")
    threshold = config.get("alert_threshold", 80)
    
    projected_daily = usage["daily"] + estimated_cost
    projected_monthly = usage["monthly"] + estimated_cost
    
    status = {
        "daily_usage": usage["daily"],
        "monthly_usage": usage["monthly"],
        "daily_limit": daily_limit,
        "monthly_limit": monthly_limit,
        "projected_daily": round(projected_daily, 4),
        "projected_monthly": round(projected_monthly, 4),
        "level": "normal",
        "action": "allow",
        "message": "[OK] Within budget",
        "alternatives": []
    }
    
    # Check limits
    if daily_limit:
        daily_pct = (projected_daily / daily_limit) * 100
        
        if daily_pct > 100:
            status["level"] = "exceeded"
            status["action"] = "block"
            status["message"] = f"[BLOCKED] DAILY BUDGET EXCEEDED: ${projected_daily:.2f} / ${daily_limit:.2f}"
        elif daily_pct > 95:
            status["level"] = "critical"
            status["action"] = "warn"
            status["message"] = f"[CRITICAL] {daily_pct:.1f}% of daily budget used"
        elif daily_pct > threshold:
            status["level"] = "warning"
            status["action"] = "warn"
            status["message"] = f"[WARNING] {daily_pct:.1f}% of daily budget used"
    
    if monthly_limit and status["action"] != "block":
        monthly_pct = (projected_monthly / monthly_limit) * 100
        
        if monthly_pct > 100:
            status["level"] = "exceeded"
            status["action"] = "block"
            status["message"] = f"[BLOCKED] MONTHLY BUDGET EXCEEDED: ${projected_monthly:.2f} / ${monthly_limit:.2f}"
        elif monthly_pct > 95 and status["level"] == "normal":
            status["level"] = "critical"
            status["action"] = "warn"
            status["message"] = f"[CRITICAL] {monthly_pct:.1f}% of monthly budget used"
        elif monthly_pct > threshold and status["level"] == "normal":
            status["level"] = "warning"
            status["action"] = "warn"
            status["message"] = f"[WARNING] {monthly_pct:.1f}% of monthly budget used"
    
    return status

def suggest_alternatives(model):
    """Suggest cheaper alternatives for a model."""
    pricing = load_pricing()
    alternatives = pricing.get("alternatives", {}).get("expensive", {})
    
    model_key = model.lower().replace("-", "-")
    
    # Find alternatives for this model or similar
    for key, alts in alternatives.items():
        if key in model_key or model_key in key:
            return alts
    
    # Default alternatives for expensive models
    expensive_keywords = ["gpt-4", "claude-opus", "gemini-pro"]
    for keyword in expensive_keywords:
        if keyword in model_key:
            return ["deepseek-v3", "qwen-2-5-turbo", "gemini-2-5-flash"]
    
    return []

def main():
    parser = argparse.ArgumentParser(description='Check budget and enforce policies')
    parser.add_argument('--model', help='Model being requested')
    parser.add_argument('--estimated-cost', type=float, default=0,
                       help='Estimated cost of request')
    parser.add_argument('--estimated-input', type=int, default=0,
                       help='Estimated input tokens')
    parser.add_argument('--estimated-output', type=int, default=0,
                       help='Estimated output tokens')
    parser.add_argument('--action', choices=['check', 'enforce'], default='check',
                       help='Just check or enforce policy')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Calculate estimated cost if tokens provided
    estimated_cost = args.estimated_cost
    if args.estimated_input > 0 or args.estimated_output > 0:
        # Load pricing and calculate
        pricing = load_pricing()
        for provider, models in pricing.get("models", {}).items():
            for model_name, rates in models.items():
                if args.model and args.model.lower() in model_name.lower():
                    input_cost = (args.estimated_input / 1_000_000) * rates["input"]
                    output_cost = (args.estimated_output / 1_000_000) * rates["output"]
                    estimated_cost = input_cost + output_cost
                    break
    
    # Get budget status
    status = get_budget_status(estimated_cost)
    
    # Add alternatives if warning or critical
    if args.model and status["level"] in ["warning", "critical"]:
        status["alternatives"] = suggest_alternatives(args.model)
    
    # Output
    if args.format == 'json':
        print(json.dumps(status, indent=2))
    else:
        print("=" * 50)
        print("BUDGET STATUS CHECK")
        print("=" * 50)
        print(f"Daily:   ${status['daily_usage']:.4f} / ${status['daily_limit'] or '∞'}")
        print(f"Monthly: ${status['monthly_usage']:.4f} / ${status['monthly_limit'] or '∞'}")
        if estimated_cost > 0:
            print(f"This request: ~${estimated_cost:.4f}")
        print("-" * 50)
        print(status['message'])
        
        if status['alternatives']:
            print("-" * 50)
            print("Cheaper alternatives:")
            for alt in status['alternatives']:
                print(f"   - {alt}")
        print("=" * 50)
    
    # Return exit code for enforce mode
    if args.action == 'enforce' and status['action'] == 'block':
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
