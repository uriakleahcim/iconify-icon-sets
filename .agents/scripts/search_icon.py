#!/usr/bin/env python3
"""
Fast offline search across Iconify icon sets.
Usage:
    python3 search_icon.py <query> [--collection <prefix>] [--limit <n>]
"""

import os
import sys
import json
import argparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JSON_DIR = os.path.join(REPO_ROOT, "json")

GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

def search_icons(query, collection=None, limit=50):
    if not os.path.isdir(JSON_DIR):
        print(f"Error: JSON dataset directory not found at {JSON_DIR}", file=sys.stderr)
        sys.exit(1)

    query_lower = query.lower()
    matches = []

    if collection:
        files = [f"{collection}.json"] if not collection.endswith(".json") else [collection]
    else:
        files = sorted(os.listdir(JSON_DIR))

    for fname in files:
        if not fname.endswith(".json"):
            continue
        prefix = fname[:-5]
        fpath = os.path.join(JSON_DIR, fname)

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            if query_lower not in content.lower():
                continue

            data = json.loads(content)
            icons = data.get("icons", {})
            aliases = data.get("aliases", {})
            is_palette = data.get("info", {}).get("palette", False)

            for icon in icons:
                if query_lower in icon.lower():
                    matches.append((prefix, icon, "icon", is_palette))
                    if len(matches) >= limit:
                        return matches

            for alias in aliases:
                if query_lower in alias.lower():
                    matches.append((prefix, alias, "alias", is_palette))
                    if len(matches) >= limit:
                        return matches
        except Exception:
            continue

    return matches

def main():
    parser = argparse.ArgumentParser(description="Search icons in local Iconify datasets")
    parser.add_argument("query", help="Keyword to search for (e.g. 'terminal', 'cloud', 'github')")
    parser.add_argument("-c", "--collection", help="Limit search to a specific collection prefix (e.g. 'lucide', 'mdi')")
    parser.add_argument("-l", "--limit", type=int, default=30, help="Maximum number of results to display (default: 30)")
    args = parser.parse_args()

    print(f"\n🔍 Searching for '{BOLD}{args.query}{RESET}' in local icon sets...")
    results = search_icons(args.query, args.collection, args.limit)

    if not results:
        print(f"{YELLOW}No matching icons found.{RESET}\n")
        return

    print(f"\nFound {GREEN}{len(results)}{RESET} match(es) (capped at {args.limit}):\n")
    print(f"{'ICON IDENTIFIER':<40} {'TYPE':<10} {'PALETTE':<10}")
    print("-" * 62)

    for prefix, name, itype, is_palette in results:
        full_id = f"{prefix}:{name}"
        pal_str = f"{YELLOW}multi-color{RESET}" if is_palette else f"{CYAN}monotone{RESET}"
        print(f"{BOLD}{full_id:<40}{RESET} {DIM}{itype:<10}{RESET} {pal_str:<10}")

    print(f"\n{DIM}Tip: Extract to SVG using: python3 .agents/scripts/extract_svg.py <prefix:name>{RESET}\n")

if __name__ == "__main__":
    main()
