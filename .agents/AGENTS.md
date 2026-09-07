# Iconify Icon Sets Repository — Agent Guide

## 📌 Repository Overview
This repository contains offline datasets for over 200+ icon collections and 300,000+ vector icons in the Iconify JSON format. It serves as the local source of truth for offline icon searching, SVG compilation, and UI asset generation across the system.

- **Primary Local Path:** `/home/alphasunny/AppData/iconify-icon-sets`
- **Origin Remote:** `https://github.com/uriakleahcim/iconify-icon-sets`
- **Upstream Source:** `https://github.com/iconify/icon-sets`

---

## 🗂️ Directory & File Structure
```
iconify-icon-sets/
├── json/                     # 230+ JSON icon sets (e.g., mdi.json, lucide.json, fluent-emoji.json)
├── collections.json          # Master metadata catalog (license, author, count, category, tags)
├── collections.md            # Human-readable index of all collections
├── .agents/
│   ├── AGENTS.md             # This guide for AI agents and developers
│   └── scripts/
│       ├── search_icon.py       # Fast CLI search across all JSON datasets
│       ├── extract_svg.py       # Standalone offline SVG compiler/extractor
│       ├── inspect_collection.py # Collection metadata inspection
│       └── validate_dataset.py  # Health check & integrity diagnostics
├── src/                      # TypeScript build source
├── package.json              # NPM package definition (@iconify/json)
└── sync-version.cjs          # Version sync helper
```

---

## ⚙️ System CLI Integration (`iconify`)
The local system binary at `~/.local/bin/iconify` is directly integrated with this directory:
- It points to `~/AppData/iconify-icon-sets/json` as its `JSON_DIR`.
- Output SVGs are saved to `~/AppData/Assets/icons/`.
- Managed in the unified command registry at `/home/alphasunny/UserAccess/env.yaml`.

### Common System Commands:
```bash
# Pull and compile an icon offline into ~/AppData/Assets/icons/
iconify pull lucide:terminal --color "#38bdf8" --height 64

# Auto-search and pull if prefix is omitted
iconify pull docker --color blue --height 128

# Search offline icon datasets
iconify search kubernetes

# Asset management
iconify count
iconify list
```

---

## 🛠️ Companion Helper Scripts (`.agents/scripts/`)
For direct scripting, agent pair-programming, or standalone automation without modifying system assets:

### 1. `search_icon.py` (Fast Search)
Performs fast substring pre-filtering before JSON parsing:
```bash
python3 .agents/scripts/search_icon.py <query> [-c <collection>] [-l <limit>]
# Example:
python3 .agents/scripts/search_icon.py github --limit 10
python3 .agents/scripts/search_icon.py server --collection lucide
```

### 2. `extract_svg.py` (Direct SVG Compiler)
Compiles complete, valid SVG XML offline with color, size, and transformation support:
```bash
python3 .agents/scripts/extract_svg.py <prefix:name> [--color <c>] [--size <px>] [--output <file.svg>]
# Examples:
# Print SVG to terminal/pipe:
python3 .agents/scripts/extract_svg.py lucide:cpu --color "#10b981" --size 32

# Export directly to a file:
python3 .agents/scripts/extract_svg.py simple-icons:python --color "#3776AB" --output ./python-logo.svg
```

### 3. `inspect_collection.py` (Collection Metadata)
Inspects license, author, tags, sample icons, and total icon counts from `collections.json`:
```bash
# Inspect a single collection:
python3 .agents/scripts/inspect_collection.py lucide

# List collections sorted by size:
python3 .agents/scripts/inspect_collection.py --list

# Filter collections by category:
python3 .agents/scripts/inspect_collection.py --category Brands
```

### 4. `validate_dataset.py` (Health Check)
Verifies dataset completeness, detects missing collections, and validates JSON syntax:
```bash
python3 .agents/scripts/validate_dataset.py --sample-check
```

---

## 📐 Iconify JSON Schema & Parsing Rules
When reading or transforming icons programmatically:
1. **Dimensions & ViewBox:**
   - Base viewBox coordinates are `left`, `top`, `width`, `height`.
   - Default fallback: root level properties (typically `width: 16/24`, `height: 16/24`, `left: 0`, `top: 0`).
   - If an individual icon specifies `width` or `height`, those override root values.
2. **Aliases:**
   - Icons under `"aliases"` reference `"parent"`. Always copy parent icon properties first, then apply alias overrides (`rotate`, `hFlip`, `vFlip`, etc.).
3. **Monotone vs. Palette Icons:**
   - Check `data["info"]["palette"]`:
     - If `false`: The icon is monotone. It uses `currentColor` or no fill. Custom colors can safely be applied.
     - If `true`: The icon contains multi-color layers (e.g. `fluent-emoji`, `catppuccin`). Do not override fills globally.
4. **Performance Consideration:**
   - Some datasets (e.g., `fluent-emoji.json`) are ~99MB. When searching across files, always perform a fast raw text substring pre-check before calling `json.loads()`.

---

## 🔒 Git & Contribution Guidelines
- **Commit Author:** `uriakleahcim <uriakleahcim@users.noreply.github.com>`
- **Tracked Branch:** `main` tracking `origin/main` (`uriakleahcim/iconify-icon-sets`)
- **Upstream Syncing:** To fetch new icon updates from upstream:
  ```bash
  git fetch upstream master
  ```
