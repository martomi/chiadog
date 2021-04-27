# std
import logging
from typing import List
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# project
from . import Notifier, Event


class SMTPNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Email notifier.")
        super().__init__(title_prefix, config)
        try:
            credentials = config["credentials"]
            self.sender = credentials["sender"]
            self.sender_name = credentials["sender_name"]
            self.recipient = credentials["recipient"]
            self.username_smtp = credentials["username_smtp"]
            self.password_smtp = credentials["password_smtp"]
            self.host = credentials["host"]
            self.port = credentials["port"]

        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type in self._notification_types and event.service in self._notification_services:
                subject = self.get_title_for_event(event)
                text = event.message
                # Create message container - the correct MIME type is multipart/alternative.
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = email.utils.formataddr((self.sender_name, self.sender))
                msg["To"] = self.recipient

                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(text.replace("\n", "<br />"), "html")

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)

                # Try to send the message.
                try:
                    server = smtplib.SMTP(self.host, self.port, timeout=self._conn_timeout_seconds)
                    server.ehlo()
                    server.starttls()
                    # stmplib docs recommend calling ehlo() before & after starttls()
                    server.ehlo()
                    server.login(self.username_smtp, self.password_smtp)
                    server.sendmail(self.sender, self.recipient, msg.as_string())
                    server.quit()
                # Display an error message if something goes wrong.
                except Exception as e:
                    logging.error("SMTP Notify Error: ", e)
                    errors = True

        return not errors
