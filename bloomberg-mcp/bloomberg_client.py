"""
Bloomberg Client
Manages the blpapi session lifecycle. All tools share a single instance.
"""

import blpapi

BLOOMBERG_HOST = "localhost"
BLOOMBERG_PORT = 8194


class BloombergClient:
    def __init__(self):
        self.session = None
        self.ref_data_service = None

    def connect(self):
        """Start session and open the reference data service."""
        options = blpapi.SessionOptions()
        options.setServerHost(BLOOMBERG_HOST)
        options.setServerPort(BLOOMBERG_PORT)

        self.session = blpapi.Session(options)

        if not self.session.start():
            raise ConnectionError("Could not start Bloomberg session. Is the Terminal running?")

        if not self.session.openService("//blp/refdata"):
            raise ConnectionError("Could not open Bloomberg reference data service.")

        self.ref_data_service = self.session.getService("//blp/refdata")

    def disconnect(self):
        """Cleanly close the session."""
        if self.session:
            self.session.stop()
            self.session = None

    def ensure_connected(self):
        """Connect if not already connected."""
        if self.session is None:
            self.connect()

    def send_request(self, request) -> list:
        """
        Send a request and collect all response messages.
        Returns a flat list of blpapi Message objects.
        """
        self.session.sendRequest(request)
        messages = []
        while True:
            event = self.session.nextEvent(500)
            for msg in event:
                messages.append(msg)
            if event.eventType() == blpapi.Event.RESPONSE:
                break
        return messages
