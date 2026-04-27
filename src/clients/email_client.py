from __future__ import annotations

import logging
from typing import Protocol

import requests

from src.clients.retry import retry_call

LOGGER = logging.getLogger(__name__)


class EmailClientProtocol(Protocol):
    def send(self, recipient: str, subject: str, html_body: str) -> None:
        ...


class SendGridEmailClient:
    def __init__(self, api_key: str, sender: str = "image-rebuild-bot@example.com"):
        self.api_key = api_key
        self.sender = sender

    def send(self, recipient: str, subject: str, html_body: str) -> None:
        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": self.sender},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body}],
        }

        def operation() -> requests.Response:
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=15,
            )
            if response.status_code >= 500:
                response.raise_for_status()
            return response

        response = retry_call(operation, logger=LOGGER, retry_exceptions=(requests.RequestException,))
        if response.status_code not in (200, 202):
            response.raise_for_status()
