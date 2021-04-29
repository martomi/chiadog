# std
import logging
from typing import List
from paho.mqtt.client import MQTTMessageInfo, Client, MQTT_ERR_SUCCESS, MQTT_ERR_NO_CONN

from . import Notifier, Event


class MqttNotifier(Notifier):

    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing MQTT notifier.")
        super().__init__(title_prefix, config)
        try:

            credentials = config["credentials"]
            self._set_config(config)
            self._set_credentials(credentials)

        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

        self._init_mqtt()

    def _set_config(self, config: dict):

        self._topic = config["topic"]
        self._qos = config["qos"] if "qos" in config else 0
        self._retain = config["retain"] if "retain" in config else False

    def _set_credentials(self, credentials: dict):

        self._host = credentials["host"]
        self._port = credentials["port"]

        if "mqtt_username" in credentials and credentials["mqtt_username"] != "":
            self._username = credentials["mqtt_username"]
        if "mqtt_password" in credentials and credentials["mqtt_password"] != "":
            self._password = credentials["mqtt_password"]

    def _init_mqtt(self):
        self._client: Client = Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        if self._username and self._password:
            self._client.username_pw_set(self._username, self._password)

        self._client.connect(self._host, self._port)
        self._client.reconnect_delay_set()
        self._client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        if self._password:
            logging.info(f"Successfully connected to MQTT host {self._host} with password authentication")
        else:
            logging.info(f"Successfully connected to MQTT host {self._host}")

    def _on_disconnect(self, client, userdata, rc):

        logging.warning("Disconnected from MQTT: {}".format(rc))
        self._client.loop_stop()

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:

                payload = {
                    "type": event.type,
                    "prio": event.priority,
                    "msg": event.message
                }

                response: MQTTMessageInfo = self._client.publish(self._topic,
                                                                 payload=payload,
                                                                 qos=self._qos,
                                                                 retain=self._retain
                                                                 )

                if response.rc == MQTT_ERR_SUCCESS:
                    pass
                elif response.rc == MQTT_ERR_NO_CONN:
                    logging.warning(f"Message delivery failed because the MQTT Client was not connected")
                    errors = True
                else:
                    logging.warning(f"MQTT message delivery failed due to an unknown error")
                    errors = True

        return not errors
