#!/usr/bin/env python3
"""
Offline SVG extractor from Iconify JSON sets.
Extracts SVG markup directly from local JSON files with color, size, and transform support.

Usage:
    python3 extract_svg.py <prefix:name> [--color <hex/name>] [--size <pixels>] [--output <file.svg>]
"""

import os
import sys
import json
import argparse
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JSON_DIR = os.path.join(REPO_ROOT, "json")

def parse_icon_id(identifier):
    if ":" not in identifier:
        raise ValueError(f"Invalid icon identifier '{identifier}'. Format must be 'prefix:icon-name' (e.g. 'lucide:rocket').")
    prefix, name = identifier.split(":", 1)
    return prefix.strip(), name.strip()

def build_svg(prefix, name, color=None, size=None):
    json_path = os.path.join(JSON_DIR, f"{prefix}.json")
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"Icon collection '{prefix}' not found at {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    icons = data.get("icons", {})
    aliases = data.get("aliases", {})
    root_width = data.get("width", 16)
    root_height = data.get("height", 16)
    root_left = data.get("left", 0)
    root_top = data.get("top", 0)
    is_palette = data.get("info", {}).get("palette", False)

    icon_props = {}
    if name in icons:
        icon_props = dict(icons[name])
    elif name in aliases:
        alias_data = aliases[name]
        parent_name = alias_data.get("parent")
        if parent_name and parent_name in icons:
            icon_props = dict(icons[parent_name])
            for k, v in alias_data.items():
                if k != "parent":
                    icon_props[k] = v
        else:
            raise KeyError(f"Alias '{name}' references unknown parent '{parent_name}'")
    else:
        raise KeyError(f"Icon '{name}' not found in collection '{prefix}'")

    body = icon_props.get("body", "")
    width = icon_props.get("width", root_width)
    height = icon_props.get("height", root_height)
    left = icon_props.get("left", root_left)
    top = icon_props.get("top", root_top)
    rotate = icon_props.get("rotate", 0)
    h_flip = icon_props.get("hFlip", False)
    v_flip = icon_props.get("vFlip", False)

    # Color manipulation (for monotone / non-palette icons)
    if color:
        if "currentColor" in body:
            body = body.replace("currentColor", color)
        elif not is_palette:
            body = f'<g fill="{color}">{body}</g>'

    # Transformation wrap if needed
    transforms = []
    if rotate:
        transforms.append(f"rotate({rotate * 90} {width/2} {height/2})")
    if h_flip or v_flip:
        sx = -1 if h_flip else 1
        sy = -1 if v_flip else 1
        cx = width if h_flip else 0
        cy = height if v_flip else 0
        transforms.append(f"translate({cx} {cy}) scale({sx} {sy})")

    if transforms:
        body = f'<g transform="{" ".join(transforms)}">{body}</g>'

    # Sizing
    render_width = width
    render_height = height
    if size:
        render_height = int(size)
        render_width = int(round((width / height) * render_height)) if height else render_height

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{left} {top} {width} {height}" '
        f'width="{render_width}" height="{render_height}">'
        f'{body}'
        f'</svg>'
    )
    return svg

def main():
    parser = argparse.ArgumentParser(description="Extract SVG markup offline from Iconify datasets")
    parser.add_argument("identifier", help="Icon identifier in format 'prefix:name' (e.g. 'lucide:terminal')")
    parser.add_argument("--color", "-c", help="Color override for monotone icons (e.g. '#2563eb', 'orange')")
    parser.add_argument("--size", "-s", type=int, help="Output pixel size/height (width scales proportionally)")
    parser.add_argument("--output", "-o", help="Target SVG file path. If omitted, prints SVG to stdout")
    args = parser.parse_args()

    try:
        prefix, name = parse_icon_id(args.identifier)
        svg_code = build_svg(prefix, name, color=args.color, size=args.size)

        if args.output:
            out_dir = os.path.dirname(os.path.abspath(args.output))
            os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(svg_code)
            print(f"✓ Saved SVG to: {args.output}")
        else:
            print(svg_code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
