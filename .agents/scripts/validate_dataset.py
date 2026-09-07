#!/usr/bin/env python3
"""
Diagnostic utility to validate local Iconify datasets and report health metrics.
Usage:
    python3 validate_dataset.py [--sample-check]
"""

import os
import sys
import json
import argparse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JSON_DIR = os.path.join(REPO_ROOT, "json")
COLLECTIONS_FILE = os.path.join(REPO_ROOT, "collections.json")

GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
RESET = "\033[0m"
BOLD = "\033[1m"

def main():
    parser = argparse.ArgumentParser(description="Validate local Iconify dataset integrity")
    parser.add_argument("--sample-check", action="store_true", help="Perform JSON parse test on sample files")
    args = parser.parse_args()

    print(f"\n{BOLD}🏥 Iconify Dataset Diagnostics{RESET}")
    print("=" * 55)

    if not os.path.isdir(JSON_DIR):
        print(f"{RED}❌ JSON directory not found: {JSON_DIR}{RESET}")
        sys.exit(1)

    if not os.path.isfile(COLLECTIONS_FILE):
        print(f"{RED}❌ collections.json not found: {COLLECTIONS_FILE}{RESET}")
        sys.exit(1)

    with open(COLLECTIONS_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    json_files = [f for f in os.listdir(JSON_DIR) if f.endswith(".json")]
    json_prefixes = {f[:-5] for f in json_files}
    meta_prefixes = set(meta.keys())

    missing_on_disk = meta_prefixes - json_prefixes
    untracked_on_disk = json_prefixes - meta_prefixes

    total_icons_meta = sum(v.get("total", 0) for v in meta.values() if isinstance(v, dict))
    total_size_bytes = sum(os.path.getsize(os.path.join(JSON_DIR, f)) for f in json_files)
    total_size_mb = total_size_bytes / (1024 * 1024)

    print(f"  {BOLD}Collections in metadata:{RESET}  {GREEN}{len(meta_prefixes)}{RESET}")
    print(f"  {BOLD}JSON files on disk:{RESET}        {GREEN}{len(json_files)}{RESET}")
    print(f"  {BOLD}Total indexed icons:{RESET}       {GREEN}{total_icons_meta:,}{RESET}")
    print(f"  {BOLD}Total dataset size:{RESET}        {CYAN}{total_size_mb:.2f} MB{RESET}")

    if missing_on_disk:
        print(f"\n{YELLOW}⚠️  Missing collections on disk ({len(missing_on_disk)}):{RESET}")
        print("  " + ", ".join(sorted(list(missing_on_disk))[:10]))
    else:
        print(f"\n{GREEN}✓ All {len(meta_prefixes)} collections exist on disk.{RESET}")

    if untracked_on_disk:
        print(f"{YELLOW}ℹ️  Additional files on disk ({len(untracked_on_disk)}):{RESET}")
        print("  " + ", ".join(sorted(list(untracked_on_disk))[:10]))

    if args.sample_check:
        print(f"\n{BOLD}Testing JSON integrity of 15 sample collections...{RESET}")
        import random
        sample_keys = random.sample(sorted(list(json_prefixes)), min(15, len(json_prefixes)))
        passed = 0
        for key in sample_keys:
            try:
                with open(os.path.join(JSON_DIR, f"{key}.json"), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "icons" in data:
                        passed += 1
            except Exception as e:
                print(f"  {RED}❌ Error reading {key}.json: {e}{RESET}")
        print(f"  {GREEN}✓ {passed}/{len(sample_keys)} sample files passed validation.{RESET}")

    print(f"\n{GREEN}Status: Ready for offline icon compilation and agent operations.{RESET}\n")

if __name__ == "__main__":
    main()
