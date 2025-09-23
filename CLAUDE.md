# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the tooling repository for the Dead by Daylight Tooltips Twitch Extension. It contains Python scripts to fetch, process, and generate data from the Dead by Daylight wiki for use in the Twitch extension.

## Common Commands

### Environment Setup
- `uv venv` - Create virtual environment (uses Python 3.11+)
- `uv sync` - Install dependencies from uv.lock

### Data Fetching and Processing
- `make fetch` - Run the complete data fetching pipeline
- `make clean_fetch` - Clean and refetch all data with icon processing
- `make clean` - Remove generated data and virtual environment

### Individual Fetch Commands
- `uv run python -m dbd_tooling.fetch.perks` - Fetch perk data
- `uv run python -m dbd_tooling.fetch.powers_addons` - Fetch killer powers and addons
- `uv run python -m dbd_tooling.fetch.icons` - Process and optimize icons
- `uv run python -m dbd_tooling.aux.locale_gen` - Generate locale mappings
- `uv run python -m dbd_tooling.features.gen_feature_flags` - Generate feature flags

### Code Quality
The project uses ruff for linting (recommended extension in .vscode/extensions.json).

## Architecture

### Core Structure
- `dbd_tooling/` - Main package containing all tooling modules
  - `fetch/` - Data fetching and processing modules
    - `perks.py` - Fetches perk data from Dead by Daylight wiki
    - `powers_addons.py` - Fetches killer powers and addon data
    - `icons.py` - Processes and optimizes icon images
    - `shared.py` - Common constants and paths
    - `utils.py` - Utility functions for data processing
    - `locales/` - Internationalization data fetching
  - `aux/` - Auxiliary utilities (locale generation)
  - `features/` - Feature flag generation

### Data Flow
1. Web scraping from Dead by Daylight wiki (deadbydaylight.wiki.gg)
2. HTML parsing with BeautifulSoup4
3. Image processing and optimization with Pillow
4. JSON data generation for the Twitch extension
5. Static file copying from `static/` to `data/`

### Key Constants (dbd_tooling/fetch/shared.py)
- `DATA_FOLDER_PATH = "data"` - Output directory for all generated data
- `PERKS_URL` - Dead by Daylight wiki perks page
- File paths for survivors/killers JSON data and image directories

### Dependencies
- `aiohttp` - Async HTTP client for web requests
- `beautifulsoup4` - HTML parsing
- `pillow` - Image processing
- `requests` - HTTP requests
- `python-slugify` - URL-safe string generation
- `minify-html` - HTML minification

## Development Notes

- Uses `uv` as the package manager (replaces pip/poetry)
- Python 3.11+ required
- The project fetches data from external wiki sources and processes it for use in a Twitch extension
- Image processing includes frame generation and GIF creation for perks
- Supports multiple locales (French, German)
- Feature flags are dynamically generated based on fetched data