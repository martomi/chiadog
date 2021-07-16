# std
import http.client
import logging
import json
import urllib.parse
import re
from datetime import datetime, timedelta
from http.client import HTTPConnection, HTTPResponse
from typing import List, Tuple
from urllib.parse import ParseResult

# project
from . import Notifier, Event


class GrafanaNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Grafana notifier.")
        super().__init__(title_prefix, config)
        try:
            credentials = config["credentials"]
            self._base_url = str(credentials["base_url"]).rstrip("/")
            self._api_token = credentials["api_token"]
            self._dashboard_id = credentials.get("dashboard_id", -1)
            self._panel_id = credentials.get("panel_id", -1)
            self._offline_annotation_id = 0
            self._offline_duration = 0.0
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        success = True
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:
                start, end, duration = self._get_time_range(event.message)
                if (
                    event.message.find("Your harvester appears to be offline") >= 0
                    and self._offline_annotation_id != 0
                    and self._offline_duration < duration
                ):
                    # update annotation
                    success = self._update_annotation(event)
                else:
                    # new annotation
                    success = self._create_annotation(event)

        return success

    def _update_annotation(self, event: Event) -> bool:
        logging.debug(f"Updating annotation with id: {self._offline_annotation_id}")
        start, end, duration = self._get_time_range(event.message)

        json_payload = {
            "text": event.message,
            "time": start,
            "timeEnd": end,
        }

        endpoint = urllib.parse.urlparse(f"{self._base_url}/api/annotations/{self._offline_annotation_id}")
        response = self._send_request("PATCH", endpoint, json_payload)

        if response.getcode() != 200:
            logging.warning(f"Problem sending event to user, code: {response.getcode()}")
            return False
        else:
            self._offline_duration = duration

        return True

    def _create_annotation(self, event: Event) -> bool:
        logging.debug("Creating new annotation")
        start, end, duration = self._get_time_range(event.message)

        json_payload = {
            "text": event.message,
            "tags": [event.priority.name, event.service.name],
            "time": start,
            "timeEnd": end,
        }

        if self._dashboard_id >= 0:
            json_payload["dashboardId"] = self._dashboard_id

        if self._panel_id >= 0:
            json_payload["panelId"] = self._panel_id

        endpoint = urllib.parse.urlparse(f"{self._base_url}/api/annotations")
        response = self._send_request("POST", endpoint, json_payload)
        if response.getcode() != 200:
            logging.warning(f"Problem sending event to user, code: {response.getcode()}")
            return False
        else:
            result = json.loads(response.read().decode("utf-8"))
            if event.message.find("Your harvester appears to be offline") >= 0:
                self._offline_annotation_id = result["id"]
                self._offline_duration = duration

        return True

    def _get_time_range(self, message: str) -> Tuple[int, int, float]:
        res = re.search(r"(\d.+\d?)(?=\s+seconds)", message)
        now = datetime.now()
        if res:
            seconds = float(res.group(1))
            start = now - timedelta(seconds=seconds)
            return self._get_milliseconds(start), self._get_milliseconds(now), seconds

        return self._get_milliseconds(now), self._get_milliseconds(now), 0

    def _get_connection(self, endpoint: ParseResult) -> HTTPConnection:
        if endpoint.scheme == "http":
            conn = http.client.HTTPConnection(endpoint.netloc, timeout=self._conn_timeout_seconds)
            logging.warning("The HTTP protocol is insecure. Consider using HTTPS to connect to Grafana.")
        elif endpoint.scheme == "https":
            conn = http.client.HTTPSConnection(endpoint.netloc, timeout=self._conn_timeout_seconds)
        else:
            raise ValueError(f"Expected an HTTP or HTTPS URL, instead got {endpoint.scheme} which is unsupported")

        return conn

    def _send_request(self, method: str, endpoint: ParseResult, payload: dict) -> HTTPResponse:
        request_body = json.dumps(payload)
        conn = self._get_connection(endpoint)

        conn.request(
            method=method,
            url=endpoint.path,
            body=request_body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self._api_token}",
            },
        )
        response = conn.getresponse()

        return response

    @staticmethod
    def _get_milliseconds(time: datetime) -> int:
        return round(time.timestamp() * 1000)
