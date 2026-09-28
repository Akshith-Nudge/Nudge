# Commerce Intelligence

This project discovers marketplace pages, captures rendered evidence, extracts product parameters, normalizes products, and calculates deterministic metrics. The initial marketplace targets are Blinkit, Zepto, and Swiggy Instamart.

## Requirements

- Python 3.11
- Chromium for Playwright (`python -m playwright install chromium`)
- Docker Desktop if you need the included PostgreSQL/Redis services
- A `GROQ_API_KEY` for AI extraction on pages that do not expose Product/ItemList JSON-LD. Pages with supported structured data work without an AI key.

## Local test

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[browser,ai,dev]"
python -m playwright install chromium
Copy-Item .env.example .env
docker compose up -d postgres redis
python -m pytest -q
```

Run a scrape:

```powershell
python scripts\run_market_research.py `
  --company "Yoga Bar" `
  --keyword "protein bars" `
  --marketplace Blinkit `
  --marketplace Zepto `
  --region Bangalore `
  --max-urls 2
```

The JSON output contains `final_params` (raw, evidence-linked observations), `availability`, `sov`, source URLs, and per-source failures. No product, price, stock state, rank, or region is fabricated: unavailable fields remain `null`, and a marketplace failure is reported without aborting other marketplaces.

Use `docker compose down` when finished. Scraping results depend on marketplace availability, consent flows, location selection, rate limits, and changes to third-party pages; validate the evidence URLs before using results operationally.
