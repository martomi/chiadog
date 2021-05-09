# std
import json
import logging
from typing import List

# project
from . import Notifier, Event


class MqttNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing MQTT notifier.")
        super().__init__(title_prefix, config)

        self._username = None
        self._password = None

        try:
            credentials = config["credentials"]
            self._set_config(config)
            self._set_credentials(credentials)
        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

        self._init_mqtt()

    def _set_config(self, config: dict):
        """
        :raises KeyError: If a key in the config doesn't exist
        :param config: The YAML config for this notifier
        :returns: None
        """
        self._topic = config["topic"]
        self._qos: int = config["qos"] if "qos" in config else 0
        self._retain: bool = config["retain"] if "retain" in config else False

    def _set_credentials(self, credentials: dict):
        """
        :raises KeyError: If a key in the config doesn't exist
        :param config: The YAML config for this notifier
        :returns: None
        """
        self._host = credentials["host"]
        self._port: int = credentials["port"]

        if "username" in credentials and credentials["username"] != "":
            self._username = credentials["username"]
        if "password" in credentials and credentials["password"] != "":
            self._password = credentials["password"]

    def _init_mqtt(self) -> bool:
        try:
            client = __import__("paho.mqtt.client", globals(), locals(), ["Client"], 0)
            self._client = client.Client()
        except ImportError:
            logging.error(
                "The Paho MQTT module was not found, please refer to INTEGRATIONS.md for help on resolving"
                "this issue. The integration will not function correctly until this issue is resolved."
            )

            return False

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        if self._username and self._password:
            self._client.username_pw_set(self._username, self._password)

        self._client.connect(self._host, self._port)
        self._client.reconnect_delay_set()
        self._client.loop_start()

        return True

    def _on_connect(self, client, userdata, flags, rc):
        from paho.mqtt.client import connack_string  # type: ignore

        if self._password:
            logging.info(f"Connecting to MQTT host {self._host} with password authentication")
        else:
            logging.info(f"Connecting to MQTT host {self._host}")

        logging.info(f"MQTT Connection Status: {connack_string(rc)}")

    def _on_disconnect(self, client, userdata, rc):
        from paho.mqtt.client import error_string  # type: ignore

        logging.warning(f"Disconnected from MQTT: {error_string(rc)}")
        self._client.loop_stop()

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False

        try:
            paho = __import__("paho.mqtt.client", globals(), locals(), ["MQTT_ERR_SUCCESS", "MQTT_ERR_NO_CONN"], 0)
        except ImportError:
            logging.error(
                "Message delivery failed because the Paho MQTT module was not found. Please refer to "
                "INTEGRATIONS.md for help on resolving this issue. "
            )

            errors = True
            return not errors

        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:

                payload = json.dumps({"type": event.type.name, "prio": event.priority.name, "msg": event.message})

                response = self._client.publish(self._topic, payload=payload, qos=self._qos, retain=self._retain)

                if response.rc == paho.MQTT_ERR_SUCCESS:
                    pass
                elif response.rc == paho.MQTT_ERR_NO_CONN:
                    logging.warning("Message delivery failed because the MQTT Client was not connected")
                    errors = True
                else:
                    logging.warning("MQTT message delivery failed due to an unknown error")
                    errors = True

        return not errors
