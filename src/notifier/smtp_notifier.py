# std
import logging
from typing import List
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# project
from . import Notifier, Event, EventType


class SMTPNotifier(Notifier):
    def __init__(self, title_prefix: str, config: dict):
        logging.info("Initializing Email notifier.")
        super().__init__(title_prefix, config)
        try:
            self.sender = config["sender"]
            self.sender_name = config["sender_name"]
            self.recipient = config["recipient"]
            self.username_smtp = config["username_smtp"]
            self.password_smtp = config["password_smtp"]
            self.host = config["host"]
            self.port = config["port"]

        except KeyError as key:
            logging.error(f"Invalid config.yaml. Missing key: {key}")

        self._smtp = None

    def get_smtp_server(self):
        # Reuse the existing SMTP connection if it is available
        if self._smtp and self._smtp.noop()[0]:
            return self._smtp
        if self._smtp:
            self._smtp.quit()
        self._smtp = smtplib.SMTP(self.host, self.port)
        self._smtp.ehlo()
        self._smtp.starttls()
        # stmplib docs recommend calling ehlo() before & after starttls()
        self._smtp.ehlo()
        self._smtp.login(self.username_smtp, self.password_smtp)
        return self._smtp

    def __del__(self):
        if self._smtp:
            self._smtp.quit()

    def send_events_to_user(self, events: List[Event]) -> bool:
        errors = False
        for event in events:
            if event.type == EventType.USER:
                priority = ""

                if event.priority == event.priority.HIGH:
                    priority = "🚨"
                elif event.priority == event.priority.NORMAL:
                    priority = "⚠️"
                subject = f"{priority} {self._title_prefix} {event.service.name} {event.message}"
                text = ""
                # Create message container - the correct MIME type is multipart/alternative.
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = email.utils.formataddr((self.sender_name, self.sender))
                msg["To"] = self.recipient

                # Record the MIME types of both parts - text/plain and text/html.
                part1 = MIMEText(text, "plain")
                part2 = MIMEText(text, "html")

                # Attach parts into message container.
                # According to RFC 2046, the last part of a multipart message, in this case
                # the HTML message, is best and preferred.
                msg.attach(part1)
                msg.attach(part2)

                # Try to send the message.
                try:
                    server = self.get_smtp_server()
                    server.sendmail(self.sender, self.recipient, msg.as_string())
                # Display an error message if something goes wrong.
                except Exception as e:
                    logging.error("SMTP Notify Error: ", e)
                    errors = True

        return errors
