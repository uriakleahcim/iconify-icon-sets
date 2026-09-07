#!/usr/bin/env python3
"""
Inspect Iconify collection metadata from collections.json.
Usage:
    python3 inspect_collection.py [collection_prefix] [--list] [--category <cat>]
"""

import os
import sys
import json
import argparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COLLECTIONS_FILE = os.path.join(REPO_ROOT, "collections.json")

GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

def load_collections():
    if not os.path.isfile(COLLECTIONS_FILE):
        print(f"Error: {COLLECTIONS_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(COLLECTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def inspect_single(prefix, data):
    if prefix not in data:
        print(f"{YELLOW}Collection '{prefix}' not found in collections.json.{RESET}")
        return
    info = data[prefix]
    print(f"\n{BOLD}📦 Collection: {GREEN}{info.get('name')}{RESET} ({CYAN}{prefix}{RESET})")
    print("-" * 55)
    print(f"  {BOLD}Total Icons:{RESET}    {info.get('total', 'N/A'):,}")
    print(f"  {BOLD}Category:{RESET}       {info.get('category', 'Uncategorized')}")
    print(f"  {BOLD}Palette Type:{RESET}   {'Multi-color' if info.get('palette') else 'Monotone'}")
    
    author = info.get("author", {})
    if isinstance(author, dict):
        auth_name = author.get("name", "Unknown")
        auth_url = author.get("url", "")
        print(f"  {BOLD}Author:{RESET}         {auth_name} ({auth_url})")
        
    license_info = info.get("license", {})
    if isinstance(license_info, dict):
        lic_title = license_info.get("title", "Unknown")
        lic_spdx = license_info.get("spdx", "")
        print(f"  {BOLD}License:{RESET}        {lic_title} [{lic_spdx}]")

    tags = info.get("tags", [])
    if tags:
        print(f"  {BOLD}Tags:{RESET}           {', '.join(tags)}")

    samples = info.get("samples", [])
    if samples:
        print(f"  {BOLD}Sample Icons:{RESET}   {', '.join(samples[:8])}")
    print()

def list_collections(data, category=None):
    items = []
    for prefix, info in data.items():
        cat = info.get("category", "Other")
        if category and category.lower() not in cat.lower():
            continue
        total = info.get("total", 0)
        name = info.get("name", prefix)
        items.append((prefix, name, total, cat))

    items.sort(key=lambda x: x[2], reverse=True)
    print(f"\nFound {GREEN}{len(items)}{RESET} collection(s):\n")
    print(f"{'PREFIX':<24} {'NAME':<32} {'ICONS':<10} {'CATEGORY'}")
    print("-" * 80)
    for prefix, name, total, cat in items[:40]:
        print(f"{CYAN}{prefix:<24}{RESET} {name[:30]:<32} {total:<10} {DIM}{cat}{RESET}")
    if len(items) > 40:
        print(f"\n{DIM}... and {len(items) - 40} more collections.{RESET}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Inspect Iconify collections")
    parser.add_argument("prefix", nargs="?", help="Collection prefix (e.g. 'lucide', 'mdi', 'fa6-solid')")
    parser.add_argument("--list", action="store_true", help="List all available collections sorted by size")
    parser.add_argument("--category", help="Filter listing by category (e.g. 'General', 'Brands')")
    args = parser.parse_args()

    data = load_collections()

    if args.prefix:
        inspect_single(args.prefix, data)
    elif args.list or args.category:
        list_collections(data, args.category)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
