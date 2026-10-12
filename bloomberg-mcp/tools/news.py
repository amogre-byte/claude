"""
Tool: get_recent_company_news
Returns recent news headlines for a security via Bloomberg news service.
"""

from bloomberg_client import BloombergClient


def get_recent_company_news(client: BloombergClient):
    def get_recent_company_news(ticker: str, max_headlines: int = 10) -> list[dict]:
        """
        Get recent news headlines for a Bloomberg security.

        Args:
            ticker:         Bloomberg ticker, e.g. "AAPL US Equity"
            max_headlines:  Maximum number of headlines to return (default 10)

        Returns:
            List of {headline, date, source} dicts ordered newest first.
        """
        client.ensure_connected()

        # TODO: Determine correct Bloomberg service for news
        #       Options: //blp/news (NewsSearchRequest) or EQY_DVD_CASH_GROSS via refdata
        #       Bloomberg news access depends on Terminal subscription level
        # TODO: Build and send news request for the ticker
        # TODO: Parse and return list of {headline, date, source}

        raise NotImplementedError("get_recent_company_news not yet implemented")

    return get_recent_company_news
