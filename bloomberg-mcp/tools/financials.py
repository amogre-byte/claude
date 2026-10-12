"""
Tool: get_financial_statements
Returns historical financial statement data for a Bloomberg security.

Supports three statements (individually or together):
  - Income Statement  : Revenue, Gross Profit, EBITDA, EBIT, Net Income, EPS
  - Balance Sheet     : Cash, Receivables, Assets, Debt, Equity, Liabilities
  - Cash Flow         : Operating CF, CapEx, Free Cash Flow, Investing, Financing

Uses HistoricalDataRequest with periodicitySelection = ANNUAL or QUARTERLY
so each row in the response corresponds to one fiscal period.
"""

import datetime
from bloomberg_client import BloombergClient


# ---------------------------------------------------------------------------
# Field definitions — Bloomberg field name  →  human-readable label
# ---------------------------------------------------------------------------

INCOME_STATEMENT_FIELDS = {
    "SALES_REV_TURN":               "Revenue",
    "COST_OF_REVENUE":              "Cost of Revenue",
    "GROSS_PROFIT":                 "Gross Profit",
    "EBITDA":                       "EBITDA",
    "IS_OPER_INC":                  "EBIT (Operating Income)",
    "IS_INT_EXPENSE":               "Interest Expense",
    "PRETAX_INC":                   "Pre-tax Income",
    "IS_INC_TAX":                   "Income Tax",
    "NET_INCOME":                   "Net Income",
    "EPS_DILUTED_REPORTED":         "EPS (Diluted)",
}

BALANCE_SHEET_FIELDS = {
    "BS_CASH":                      "Cash & Equivalents",
    "BS_ACCT_RCV":                  "Accounts Receivable",
    "BS_INVENTORIES":               "Inventories",
    "BS_CUR_ASSET_REPORT":          "Current Assets",
    "BS_TOT_ASSET":                 "Total Assets",
    "BS_CUR_LIAB":                  "Current Liabilities",
    "SHORT_AND_LONG_TERM_DEBT":     "Total Debt",
    "BS_TOT_LIAB":                  "Total Liabilities",
    "BS_SH_HOLDERS_EQ":             "Shareholders' Equity",
}

CASH_FLOW_FIELDS = {
    "CF_CASH_FROM_OPER":                  "Operating Cash Flow",
    "CF_CAP_EXPEND_PRPTY_PLANT_EQIP":     "Capital Expenditure",
    "FREE_CASH_FLOW":                     "Free Cash Flow",
    "CF_CASH_FROM_INV_ACT":               "Cash from Investing",
    "CF_CASH_FROM_FIN_ACT":               "Cash from Financing",
    "CF_DVD_PAID":                        "Dividends Paid",
    "CF_NET_CHNG_CASH":                   "Net Change in Cash",
}

STATEMENT_MAP = {
    "income_statement": INCOME_STATEMENT_FIELDS,
    "balance_sheet":    BALANCE_SHEET_FIELDS,
    "cash_flow":        CASH_FLOW_FIELDS,
}

VALID_STATEMENTS = list(STATEMENT_MAP.keys())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _start_date_for(num_periods: int, period_type: str) -> str:
    """
    Compute a start date (YYYYMMDD) that comfortably covers num_periods
    of the requested frequency, with a one-period buffer.
    """
    today = datetime.date.today()
    if period_type == "QUARTERLY":
        years_back = (num_periods // 4) + 2
    else:  # ANNUAL
        years_back = num_periods + 1
    start = today.replace(year=today.year - years_back)
    return start.strftime("%Y%m%d")


def _parse_field(element):
    """Try float first, fall back to string."""
    try:
        return round(element.getValueAsFloat(), 4)
    except Exception:
        pass
    try:
        val = element.getValueAsString()
        return None if val in ("", "N/A") else val
    except Exception:
        return None


def _fetch_statement(
    client,
    ticker: str,
    fields_map: dict,
    period_type: str,
    num_periods: int,
) -> list[dict]:
    """
    Fire one HistoricalDataRequest for the given fields and return a list of
    period records, ordered oldest → newest.

    Each record: {"period": "YYYY-MM-DD", label: value, ...}
    """
    start_date = _start_date_for(num_periods, period_type)
    end_date = datetime.date.today().strftime("%Y%m%d")

    request = client.ref_data_service.createRequest("HistoricalDataRequest")
    request.append("securities", ticker)
    for field in fields_map:
        request.append("fields", field)
    request.set("startDate", start_date)
    request.set("endDate", end_date)
    request.set("periodicitySelection", period_type)
    request.set("periodicityAdjustment", "FISCAL")

    messages = client.send_request(request)

    records = []
    for msg in messages:
        if not msg.hasElement("securityData"):
            continue

        security_data = msg.getElement("securityData")

        if security_data.hasElement("securityError"):
            error = security_data.getElement("securityError")
            return [{"error": error.getElementAsString("message")}]

        field_data_array = security_data.getElement("fieldData")

        for i in range(field_data_array.numValues()):
            row = field_data_array.getValue(i)
            record = {"period": str(row.getElementAsDatetime("date"))}
            for field, label in fields_map.items():
                if row.hasElement(field):
                    record[label] = _parse_field(row.getElement(field))
                else:
                    record[label] = None
            records.append(record)

    # Trim to the most recent num_periods
    return records[-num_periods:] if len(records) > num_periods else records


# ---------------------------------------------------------------------------
# Tool factory
# ---------------------------------------------------------------------------

def get_financial_statements(client: BloombergClient):
    def get_financial_statements(
        ticker: str,
        statements: list[str] = ["income_statement", "balance_sheet", "cash_flow"],
        period_type: str = "ANNUAL",
        num_periods: int = 5,
    ) -> dict:
        """
        Retrieve historical financial statement data for a Bloomberg security.

        Args:
            ticker:
                Bloomberg ticker, e.g. "AAPL US Equity"

            statements:
                Which statements to fetch. Any combination of:
                  - "income_statement"
                  - "balance_sheet"
                  - "cash_flow"
                Pass ["income_statement", "balance_sheet", "cash_flow"] for all three.
                Default: all three.

            period_type:
                Fiscal period frequency — "ANNUAL" or "QUARTERLY".
                Default: "ANNUAL"

            num_periods:
                Number of fiscal periods to return, most recent first.
                Default: 5 (e.g. 5 fiscal years, or 5 quarters).

        Returns:
            A dict with:
              "ticker"        — the ticker as provided
              "period_type"   — "ANNUAL" or "QUARTERLY"
              "currency"      — Bloomberg-reported currency for the security
            Plus one key per requested statement, each containing a list of
            period records ordered oldest → newest. Each record has a "period"
            date string and one key per line item.

        Example:
            get_financial_statements(
                ticker="AAPL US Equity",
                statements=["income_statement"],
                period_type="ANNUAL",
                num_periods=3,
            )
            →
            {
              "ticker": "AAPL US Equity",
              "period_type": "ANNUAL",
              "currency": "USD",
              "income_statement": [
                {
                  "period": "2022-09-30",
                  "Revenue": 394328.0,
                  "Gross Profit": 170782.0,
                  "EBITDA": 130541.0,
                  "EBIT (Operating Income)": 119437.0,
                  "Net Income": 99803.0,
                  "EPS (Diluted)": 6.15
                },
                ...
              ]
            }
        """
        # Validate period_type
        period_type = period_type.upper()
        if period_type not in ("ANNUAL", "QUARTERLY"):
            return {"error": "period_type must be 'ANNUAL' or 'QUARTERLY'"}

        # Validate statements
        unknown = [s for s in statements if s not in VALID_STATEMENTS]
        if unknown:
            return {
                "error": f"Unknown statement(s): {unknown}. "
                         f"Valid options: {VALID_STATEMENTS}"
            }

        client.ensure_connected()

        # Fetch currency via a quick ReferenceDataRequest
        currency = "N/A"
        try:
            ref_req = client.ref_data_service.createRequest("ReferenceDataRequest")
            ref_req.append("securities", ticker)
            ref_req.append("fields", "CRNCY")
            for msg in client.send_request(ref_req):
                if msg.hasElement("securityData"):
                    sec = msg.getElement("securityData").getValue(0)
                    fd = sec.getElement("fieldData")
                    if fd.hasElement("CRNCY"):
                        currency = fd.getElement("CRNCY").getValueAsString()
                    break
        except Exception:
            pass

        result = {
            "ticker": ticker,
            "period_type": period_type,
            "currency": currency,
        }

        for statement_name in statements:
            fields_map = STATEMENT_MAP[statement_name]
            result[statement_name] = _fetch_statement(
                client, ticker, fields_map, period_type, num_periods
            )

        return result

    return get_financial_statements
