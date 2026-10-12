# claude

Project-level Claude Code configuration.

## Bloomberg MCP server

`.mcp.json` registers a `bloomberg` MCP server over stdio, running the
vendored server in `bloomberg-mcp/` (sourced from
[hdhaynaut-droid/bloomberg-mcp](https://github.com/hdhaynaut-droid/bloomberg-mcp),
see `bloomberg-mcp/NOTICE.md`). It exposes Bloomberg Terminal data
(prices, historical data, security reference data, comps, financials) as
tools Claude can call directly.

To use it:

1. Install dependencies: `pip install -r bloomberg-mcp/requirements.txt`
   (requires the Bloomberg Python API, `blpapi` — see
   `bloomberg-mcp/README.md` for install details).
2. Have Bloomberg Terminal running and logged in on the same machine
   (the server connects to it locally on port 8194).
3. Open this project in Claude Code — the `bloomberg` MCP server starts
   automatically via `.mcp.json`.
