from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import quote

import requests

from src.clients.retry import retry_call

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class JenkinsBuildTrigger:
    queue_url: str | None
    status_code: int


class JenkinsClientProtocol(Protocol):
    def trigger_build(self, job_name: str, parameters: dict[str, str]) -> JenkinsBuildTrigger:
        ...


class JenkinsClient:
    def __init__(self, base_url: str, user: str, api_token: str, timeout_seconds: int = 15):
        self.base_url = base_url.rstrip("/")
        self.auth = (user, api_token)
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()

    def trigger_build(self, job_name: str, parameters: dict[str, str]) -> JenkinsBuildTrigger:
        encoded_job = "/job/".join(quote(part, safe="") for part in job_name.strip("/").split("/"))
        url = f"{self.base_url}/job/{encoded_job}/buildWithParameters"

        def operation() -> requests.Response:
            response = self.session.post(
                url,
                auth=self.auth,
                params=parameters,
                timeout=self.timeout_seconds,
            )
            if response.status_code >= 500:
                response.raise_for_status()
            return response

        response = retry_call(operation, logger=LOGGER, retry_exceptions=(requests.RequestException,))
        if response.status_code not in (200, 201, 202, 303):
            response.raise_for_status()
        return JenkinsBuildTrigger(
            queue_url=response.headers.get("Location"),
            status_code=response.status_code,
        )
