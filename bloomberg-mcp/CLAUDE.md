# Bloomberg MCP Project

## Project overview
This is a Bloomberg Terminal MCP server that exposes live Bloomberg data as tools for Claude.
It uses `blpapi` (Bloomberg Python API) and FastMCP to register tools that Claude can call
directly in conversation.

## Output directory
Save generated files (Excel, CSV, PDFs, scripts) to the project root directory.
Never save outputs to the home directory or other locations.

## Project structure
- `server.py` — FastMCP entry point; registers all tools
- `bloomberg_client.py` — shared blpapi session manager
- `tools/` — one file per tool:
  - `prices.py` — `get_bulk_prices`: current last price for a list of tickers
  - `historical.py` — `get_historical_data`: daily OHLCV over a date range
  - `security_info.py` — `get_security_info`: reference/static data
  - `comps.py` — `get_comparable_analysis`: trading comps table (EV/EBITDA, P/E, EV/Rev)
  - `financials.py` — `get_financial_statements`: income statement, balance sheet, cash flow
  - `news.py` — stub, not yet implemented

## Bloomberg ticker format
Always use full Bloomberg tickers: `AAPL US Equity`, `MSFT US Equity`, `GOOGL US Equity`, etc.

## Key conventions
- All tools are factory functions: `def get_X(client)` returns an inner `def get_X(...)` — the inner function must share the same name for FastMCP registration to work correctly.
- Bloomberg fields returning `None` mean the data requires a higher subscription tier (e.g. `BEST_*` consensus fields need Bloomberg Estimates).
- Financial data is in local currency (millions) unless otherwise noted.
