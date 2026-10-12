# Bloomberg MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that connects **Claude** directly to a live **Bloomberg Terminal**, enabling natural-language financial analysis driven by real market data.

Ask Claude things like:
> *"Run a trading comps analysis on Apple, Microsoft, Google, Amazon and Meta."*
> *"What's the current price of TSLA US Equity?"*
> *"Show me NVIDIA's revenue and EBITDA multiples versus its peers."*

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Bloomberg Terminal** | Must be running and logged in on the same machine |
| **Bloomberg Python API (`blpapi`)** | [Download from Bloomberg](https://www.bloomberg.com/professional/support/api-library/) — install via `pip install blpapi` or the wheel from the Bloomberg portal |
| **Python 3.10+** | Tested on 3.11 and 3.13 |
| **Claude Desktop** | [Download here](https://claude.ai/download) — the MCP server connects to Claude via the desktop app config |

> **Note:** Bloomberg API access requires an active Bloomberg Terminal subscription. The Python API communicates with the Terminal process running locally on your machine (default port 8194).

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/hdhaynaut-droid/bloomberg-mcp.git
cd bloomberg-mcp
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If `blpapi` fails to install via pip, download the Python wheel directly from the [Bloomberg API Library](https://www.bloomberg.com/professional/support/api-library/) and install it with:

```bash
pip install blpapi-3.x.x-py3-none-any.whl
```

### 3. Configure Claude Desktop

Copy the example config and edit it with your actual path:

```bash
cp claude_desktop_config.json.example claude_desktop_config.json
```

Then edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bloomberg": {
      "command": "python",
      "args": [
        "C:\\path\\to\\bloomberg-mcp\\server.py"
      ]
    }
  }
}
```

Copy the contents of this file into your Claude Desktop configuration file, which lives at:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

> `claude_desktop_config.json` is listed in `.gitignore` to prevent personal paths from being committed.

### 4. Verify the connection

With Bloomberg Terminal running, test the connection:

```bash
python test_connection.py
```

You should see session start and reference data service confirmation messages.

---

## Usage — Example Prompts

Once Claude Desktop is restarted with the MCP server registered, try these prompts:

**Comparables analysis**
```
Run a trading comps analysis on AAPL US Equity, MSFT US Equity, GOOGL US Equity, AMZN US Equity, and META US Equity.
```

**Current prices**
```
Get me the current price for NVDA US Equity, AMD US Equity and INTC US Equity.
```

**Historical data**
```
Show me Apple's daily closing price from January to March 2024.
```

**Security reference data**
```
What sector is TSLA in, and what's its current market cap?
```

---

## Available Tools

| Tool | Description |
|---|---|
| `get_comparable_analysis` | Trading comps table: EV/EBITDA, P/E, EV/Revenue (LTM & NTM) for a list of tickers, with median and mean summary |
| `get_bulk_prices` | Current last price (`PX_LAST`) for one or more tickers |
| `get_historical_data` | Daily OHLCV data for a ticker over a date range |
| `get_security_info` | Reference data: name, sector, currency, market cap, shares outstanding, etc. |
| `get_recent_company_news` | *(Coming soon)* Recent news headlines for a security |

---

## Architecture

### How MCP works

The [Model Context Protocol](https://modelcontextprotocol.io/) is an open standard that lets LLMs like Claude call external tools via a local server process. Claude Desktop discovers available tools by reading `claude_desktop_config.json`, which points to a local MCP server. When Claude decides to use a tool during a conversation, it sends a structured request to the server over stdio; the server executes the function and returns structured data.

```
Claude Desktop  ──stdio──►  server.py (FastMCP)  ──blpapi──►  Bloomberg Terminal
                ◄──────────                      ◄────────────
```

### Project structure

```
bloomberg-mcp/
├── server.py                       # FastMCP entry point — registers all tools
├── bloomberg_client.py             # blpapi session manager (shared singleton)
├── requirements.txt                # Python dependencies
├── claude_desktop_config.json.example   # Safe config template (no real paths)
├── .gitignore
├── LICENSE
└── tools/
    ├── __init__.py
    ├── comps.py           # Trading comparables (EV/EBITDA, P/E, EV/Rev — LTM & NTM)
    ├── prices.py          # Bulk last price
    ├── historical.py      # Daily OHLCV history
    ├── security_info.py   # Reference/static data
    └── news.py            # News headlines (not yet implemented)
```

### Bloomberg API integration

All tools share a single `BloombergClient` instance initialised in `server.py`. The client manages the `blpapi.Session` lifecycle:

- **`ensure_connected()`** — lazily connects on first tool call; re-uses the session for all subsequent calls within the same server process.
- **`send_request(request)`** — sends a request and collects all response events until a `RESPONSE`-type event is received, returning a flat list of `blpapi.Message` objects.

All data requests use the `//blp/refdata` service:
- `ReferenceDataRequest` — for current/reference fields (used by `prices`, `security_info`, `comps`)
- `HistoricalDataRequest` — for date-range time series (used by `historical`)

### Bloomberg field reference

Key fields used by the comps tool:

| Bloomberg Field | Label | Notes |
|---|---|---|
| `EV_TO_T12M_EBITDA` | EV/EBITDA (LTM) | Trailing twelve months |
| `BEST_EV_TO_EBITDA` | EV/EBITDA (NTM) | Bloomberg consensus estimates |
| `PE_RATIO` | P/E (LTM) | Trailing P/E |
| `BEST_PE_RATIO` | P/E (NTM) | Forward P/E consensus |
| `EV_TO_T12M_REVENUE` | EV/Revenue (LTM) | Trailing revenue multiple |
| `BEST_EV_TO_SALES` | EV/Revenue (NTM) | Forward revenue consensus |
| `CUR_MKT_CAP` | Market Cap | In local currency (millions) |
| `CURR_ENTP_VAL` | Enterprise Value | In local currency (millions) |

---

## Limitations

- **Requires a live Bloomberg Terminal session** — there is no offline or mock mode.
- **Subscription dependent** — some fields (especially `BEST_*` consensus estimates) require Bloomberg Estimates (`BEst`) subscription.
- **Windows path in config** — the Claude Desktop config uses an absolute path; each user must set their own after cloning.
- **News tool not yet implemented** — `get_recent_company_news` raises `NotImplementedError`.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## License

[MIT](LICENSE)
