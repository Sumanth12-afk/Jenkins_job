from __future__ import annotations

import logging
from typing import Protocol

import requests

from src.clients.retry import retry_call

LOGGER = logging.getLogger(__name__)


class EmailClientProtocol(Protocol):
    def send(self, recipient: str, subject: str, html_body: str) -> None:
        ...


import smtplib
from email.message import EmailMessage

class SMTPEmailClient:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, sender: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender = sender

    def send(self, recipient: str, subject: str, html_body: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = recipient
        msg.set_content("Please view this email in an HTML-compatible client.")
        msg.add_alternative(html_body, subtype="html")

        def operation() -> None:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)

        retry_call(operation, logger=LOGGER, retry_exceptions=(smtplib.SMTPException,))

