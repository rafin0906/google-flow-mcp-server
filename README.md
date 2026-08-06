# Google Flow Editorial Poster Scraper & Automation

A Playwright-based automation pipeline for generating sports editorial graphic posters using Google Flow.

## Project Architecture

```
newlab/
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                   # Primary entry point
├── flow_scraper.py           # Legacy entry point wrapper
└── app/
    ├── __init__.py
    ├── config.py             # Configs, selectors, and directory paths
    ├── prompts.py            # FLOW_PROMPT text templates
    ├── utils/
    │   ├── __init__.py
    │   ├── clipboard.py      # Windows clipboard image copy helper
    │   └── image.py          # Directory image scanning logic
    └── automation/
        ├── __init__.py
        └── flow.py           # Playwright UI steps & automation pipeline
```

## Prerequisites

- Python 3.10+
- Google Chrome browser
- Pre-configured `chrome_profile/` directory logged into Google

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Playwright browsers are installed:
   ```bash
   playwright install chromium
   ```

3. Place target image files in `input_images/`.

## Running Automation

Execute via `main.py`:
```bash
python main.py
```

Or via legacy entry point `flow_scraper.py`:
```bash
python flow_scraper.py
```
