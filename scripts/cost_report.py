#!/usr/bin/env python3
"""
Generate cost reports for model usage.
Usage: python cost_report.py --period today|week|month
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def get_log_path():
    """Get the path for usage log file."""
    workspace = Path.home() / ".openclaw" / "workspace"
    logs_dir = workspace / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / "model_usage.jsonl"

def get_config_path():
    """Get the path for budget config file."""
    workspace = Path.home() / ".openclaw" / "workspace"
    config_dir = workspace / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "model_budget.json"

def load_usage_data(start_date=None, end_date=None):
    """Load usage data from log file."""
    log_path = get_log_path()
    
    if not log_path.exists():
        return []
    
    entries = []
    with open(log_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry['timestamp']).date()
                    
                    if start_date and entry_date < start_date:
                        continue
                    if end_date and entry_date > end_date:
                        continue
                    
                    entries.append(entry)
                except (json.JSONDecodeError, KeyError):
                    continue
    
    return entries

def generate_report(entries, group_by="model"):
    """Generate cost report from entries."""
    if not entries:
        return {"total_cost": 0, "total_tokens": 0, "entries": []}
    
    # Group data
    grouped = defaultdict(lambda: {"cost": 0, "input_tokens": 0, "output_tokens": 0, "calls": 0})
    
    total_cost = 0
    for entry in entries:
        key = entry.get(group_by, entry['model'])
        if group_by == "day":
            key = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d')
        elif group_by == "provider":
            # Extract provider from model name or metadata
            key = entry.get('metadata', {}).get('provider', 'unknown')
        
        cost = entry['cost']['total_cost']
        grouped[key]['cost'] += cost
        grouped[key]['input_tokens'] += entry['input_tokens']
        grouped[key]['output_tokens'] += entry['output_tokens']
        grouped[key]['calls'] += 1
        total_cost += cost
    
    # Build report
    report = {
        "period": {
            "start": min(e['timestamp'] for e in entries)[:10] if entries else None,
            "end": max(e['timestamp'] for e in entries)[:10] if entries else None,
        },
        "summary": {
            "total_cost": round(total_cost, 4),
            "total_calls": len(entries),
            "total_tokens": sum(e['total_tokens'] for e in entries),
            "avg_cost_per_call": round(total_cost / len(entries), 6) if entries else 0
        },
        "breakdown": []
    }
    
    for key, data in sorted(grouped.items(), key=lambda x: x[1]['cost'], reverse=True):
        report["breakdown"].append({
            "key": key,
            "cost": round(data['cost'], 4),
            "calls": data['calls'],
            "input_tokens": data['input_tokens'],
            "output_tokens": data['output_tokens'],
            "avg_cost_per_call": round(data['cost'] / data['calls'], 6) if data['calls'] else 0
        })
    
    return report

def format_report_text(report):
    """Format report as text."""
    lines = []
    lines.append("=" * 60)
    lines.append("MODEL USAGE COST REPORT")
    lines.append("=" * 60)
    lines.append(f"Period: {report['period']['start']} to {report['period']['end']}")
    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Total Cost:     ${report['summary']['total_cost']:.4f}")
    lines.append(f"Total Calls:    {report['summary']['total_calls']:,}")
    lines.append(f"Total Tokens:   {report['summary']['total_tokens']:,}")
    lines.append(f"Avg Cost/Call:  ${report['summary']['avg_cost_per_call']:.6f}")
    lines.append("")
    lines.append("BREAKDOWN BY MODEL")
    lines.append("-" * 60)
    lines.append(f"{'Model':<25} {'Calls':>8} {'Cost ($)':>12} {'%':>8}")
    lines.append("-" * 60)
    
    total = report['summary']['total_cost']
    for item in report['breakdown']:
        pct = (item['cost'] / total * 100) if total > 0 else 0
        lines.append(f"{item['key']:<25} {item['calls']:>8} {item['cost']:>12.4f} {pct:>7.1f}%")
    
    lines.append("=" * 60)
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Generate cost reports')
    parser.add_argument('--period', choices=['today', 'week', 'month', 'custom'], 
                       default='today', help='Report period')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD) for custom period')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD) for custom period')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], 
                       default='text', help='Output format')
    parser.add_argument('--group-by', choices=['model', 'day', 'provider'], 
                       default='model', help='Group data by')
    
    args = parser.parse_args()
    
    # Calculate date range
    today = datetime.now().date()
    start_date = today
    end_date = today
    
    if args.period == 'today':
        start_date = today
        end_date = today
    elif args.period == 'week':
        start_date = today - timedelta(days=7)
        end_date = today
    elif args.period == 'month':
        start_date = today - timedelta(days=30)
        end_date = today
    elif args.period == 'custom':
        if args.start_date:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        if args.end_date:
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    
    # Load data and generate report
    entries = load_usage_data(start_date, end_date)
    report = generate_report(entries, group_by=args.group_by)
    
    # Output
    if args.format == 'text':
        print(format_report_text(report))
    elif args.format == 'json':
        print(json.dumps(report, indent=2))
    elif args.format == 'csv':
        print("model,calls,cost,input_tokens,output_tokens")
        for item in report['breakdown']:
            print(f"{item['key']},{item['calls']},{item['cost']},{item['input_tokens']},{item['output_tokens']}")

if __name__ == "__main__":
    main()
