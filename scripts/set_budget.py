#!/usr/bin/env python3
"""
Set and manage budget limits for model usage.
Usage: python set_budget.py --daily 10.00 --monthly 100.00
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

def get_config_path():
    """Get the path for budget config file."""
    workspace = Path.home() / ".openclaw" / "workspace"
    config_dir = workspace / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "model_budget.json"

def load_budget_config():
    """Load budget configuration."""
    config_path = get_config_path()
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Default config
    return {
        "daily_limit": None,
        "monthly_limit": None,
        "alert_threshold": 80,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def save_budget_config(config):
    """Save budget configuration."""
    config_path = get_config_path()
    config["updated_at"] = datetime.now().isoformat()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    return config

def set_budget(daily=None, monthly=None, alert_threshold=None):
    """Set budget limits."""
    config = load_budget_config()
    
    if daily is not None:
        config["daily_limit"] = float(daily)
    
    if monthly is not None:
        config["monthly_limit"] = float(monthly)
    
    if alert_threshold is not None:
        config["alert_threshold"] = float(alert_threshold)
    
    return save_budget_config(config)

def display_budget(config):
    """Display current budget settings."""
    print("=" * 50)
    print("BUDGET CONFIGURATION")
    print("=" * 50)
    print(f"Daily Limit:     ${config.get('daily_limit', 'Not set')}")
    print(f"Monthly Limit:   ${config.get('monthly_limit', 'Not set')}")
    print(f"Alert Threshold: {config.get('alert_threshold', 80)}%")
    print(f"Last Updated:    {config.get('updated_at', 'N/A')}")
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description='Set budget limits for model usage')
    parser.add_argument('--daily', type=float, help='Daily budget limit in USD')
    parser.add_argument('--monthly', type=float, help='Monthly budget limit in USD')
    parser.add_argument('--alert-threshold', type=float, default=80,
                       help='Alert threshold percentage (default: 80)')
    parser.add_argument('--show', action='store_true', 
                       help='Show current budget configuration')
    
    args = parser.parse_args()
    
    if args.show:
        config = load_budget_config()
        display_budget(config)
        return
    
    if args.daily is None and args.monthly is None:
        print("[ERROR] Please specify at least one budget limit (--daily or --monthly)")
        print("   Or use --show to display current configuration")
        return
    
    config = set_budget(
        daily=args.daily,
        monthly=args.monthly,
        alert_threshold=args.alert_threshold
    )
    
    print("[OK] Budget configuration updated!")
    display_budget(config)

if __name__ == "__main__":
    main()
