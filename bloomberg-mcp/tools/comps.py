"""
Tool: get_comparable_analysis
Returns a trading comparables table for a list of securities.

Fetched multiples (LTM = last twelve months, NTM = next twelve months consensus):
  - EV/EBITDA  (LTM & NTM)
  - P/E        (LTM & NTM)
  - EV/Revenue (LTM & NTM)

Also fetches: company name, currency, sector, market cap, enterprise value.
"""

from bloomberg_client import BloombergClient

COMPS_FIELDS = [
    "NAME",
    "CRNCY",
    "GICS_SECTOR_NAME",
    "CUR_MKT_CAP",
    "CURR_ENTP_VAL",
    # EV/EBITDA
    "EV_TO_T12M_EBITDA",       # LTM EV/EBITDA
    "BEST_EV_TO_EBITDA",       # NTM EV/EBITDA (Bloomberg consensus)
    # P/E
    "PE_RATIO",                # LTM P/E
    "BEST_PE_RATIO",           # NTM P/E  (Bloomberg consensus)
    # EV/Revenue
    "EV_TO_T12M_REVENUE",      # LTM EV/Revenue
    "BEST_EV_TO_SALES",        # NTM EV/Revenue (Bloomberg consensus)
]

# Human-readable labels for each field
FIELD_LABELS = {
    "NAME":               "Name",
    "CRNCY":              "Currency",
    "GICS_SECTOR_NAME":   "Sector",
    "CUR_MKT_CAP":        "Market Cap",
    "CURR_ENTP_VAL":      "Enterprise Value",
    "EV_TO_T12M_EBITDA":  "EV/EBITDA (LTM)",
    "BEST_EV_TO_EBITDA":  "EV/EBITDA (NTM)",
    "PE_RATIO":           "P/E (LTM)",
    "BEST_PE_RATIO":      "P/E (NTM)",
    "EV_TO_T12M_REVENUE": "EV/Revenue (LTM)",
    "BEST_EV_TO_SALES":   "EV/Revenue (NTM)",
}

# Numeric fields used to compute summary statistics
NUMERIC_MULTIPLE_FIELDS = [
    "EV_TO_T12M_EBITDA",
    "BEST_EV_TO_EBITDA",
    "PE_RATIO",
    "BEST_PE_RATIO",
    "EV_TO_T12M_REVENUE",
    "BEST_EV_TO_SALES",
]


def _parse_field(element):
    """Try numeric first, fall back to string, return None on failure."""
    try:
        return round(element.getValueAsFloat(), 2)
    except Exception:
        pass
    try:
        return element.getValueAsString()
    except Exception:
        return None


def _median(values: list) -> float | None:
    clean = sorted(v for v in values if isinstance(v, (int, float)))
    if not clean:
        return None
    mid = len(clean) // 2
    if len(clean) % 2 == 0:
        return round((clean[mid - 1] + clean[mid]) / 2, 2)
    return round(clean[mid], 2)


def _mean(values: list) -> float | None:
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 2)


def get_comparable_analysis(client: BloombergClient):
    def get_comparable_analysis(tickers: list[str]) -> dict:
        """
        Build a trading comparables table for a list of Bloomberg securities.

        Fetches LTM and NTM multiples (EV/EBITDA, P/E, EV/Revenue) for each
        company in one bulk Bloomberg request, then appends median and mean
        summary rows across the peer group.

        Args:
            tickers: List of Bloomberg tickers, e.g.
                     ["AAPL US Equity", "MSFT US Equity", "GOOGL US Equity"]

        Returns:
            A dict with two keys:
              "companies"  — dict mapping each ticker to its metrics:
                             {field_label: value, ...}
              "summary"    — dict with "Median" and "Mean" rows for every
                             numeric multiple field.

        Example:
            {
              "companies": {
                "AAPL US Equity": {
                  "Name": "Apple Inc",
                  "Currency": "USD",
                  "Sector": "Information Technology",
                  "Market Cap": 2850000.0,
                  "Enterprise Value": 2900000.0,
                  "EV/EBITDA (LTM)": 22.1,
                  "EV/EBITDA (NTM)": 20.4,
                  "P/E (LTM)": 28.5,
                  "P/E (NTM)": 26.2,
                  "EV/Revenue (LTM)": 7.1,
                  "EV/Revenue (NTM)": 6.8
                },
                ...
              },
              "summary": {
                "Median": {"EV/EBITDA (LTM)": 21.0, ...},
                "Mean":   {"EV/EBITDA (LTM)": 21.3, ...}
              }
            }
        """
        client.ensure_connected()

        # --- Build one bulk ReferenceDataRequest for all tickers ---
        request = client.ref_data_service.createRequest("ReferenceDataRequest")
        for ticker in tickers:
            request.append("securities", ticker)
        for field in COMPS_FIELDS:
            request.append("fields", field)

        messages = client.send_request(request)

        # --- Parse responses ---
        companies = {}
        for msg in messages:
            if not msg.hasElement("securityData"):
                continue
            security_data = msg.getElement("securityData")
            for i in range(security_data.numValues()):
                security = security_data.getValue(i)
                ticker = security.getElementAsString("security")

                if security.hasElement("securityError"):
                    error = security.getElement("securityError")
                    companies[ticker] = {
                        "error": error.getElementAsString("message")
                    }
                    continue

                field_data = security.getElement("fieldData")
                row = {}
                for field in COMPS_FIELDS:
                    label = FIELD_LABELS[field]
                    if field_data.hasElement(field):
                        row[label] = _parse_field(field_data.getElement(field))
                    else:
                        row[label] = None
                companies[ticker] = row

        # --- Compute summary statistics across valid companies ---
        summary = {"Median": {}, "Mean": {}}
        for field in NUMERIC_MULTIPLE_FIELDS:
            label = FIELD_LABELS[field]
            values = [
                companies[t][label]
                for t in companies
                if "error" not in companies[t] and companies[t].get(label) is not None
            ]
            summary["Median"][label] = _median(values)
            summary["Mean"][label] = _mean(values)

        return {"companies": companies, "summary": summary}

    return get_comparable_analysis
