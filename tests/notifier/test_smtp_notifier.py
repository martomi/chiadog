# std
import os
import unittest

# project
from src.notifier import Event, EventType, EventPriority, EventService
from src.notifier.smtp_notifier import SMTPNotifier


class TestSMTPNotifier(unittest.TestCase):
    def setUp(self) -> None:
        sender = os.getenv("SENDER")
        sender_name = os.getenv("SENDER_NAME")
        recipient = os.getenv("RECIPIENT")
        username_smtp = os.getenv("USERNAME_SMTP")
        password_smtp = os.getenv("PASSWORD_SMTP")
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        self.assertIsNotNone(sender, "You must export SENDER as env variable")
        self.assertIsNotNone(sender_name, "You must export SENDER_NAME as env variable")
        self.assertIsNotNone(recipient, "You must export RECIPIENT as env variable")
        self.assertIsNotNone(username_smtp, "You must export USERNAME_SMTP as env variable")
        self.assertIsNotNone(password_smtp, "You must export PASSWORD_SMTP as env variable")
        self.assertIsNotNone(host, "You must export HOST as env variable")
        self.assertIsNotNone(port, "You must export PORT as env variable")

        self.notifier = SMTPNotifier(
            title_prefix="Test",
            config={
                "enable": True,
                "sender": sender,
                "sender_name": sender_name,
                "recipient": recipient,
                "username_smtp": username_smtp,
                "password_smtp": password_smtp,
                "host": host,
                "port": port,
            },
        )

    @unittest.skipUnless(os.getenv("USERNAME_SMTP"), "Run only if SMTP available")
    def testSTMPLowPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.HARVESTER,
                    message="Low priority notification 1.",
                ),
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.HARVESTER,
                    message="Low priority notification 2.",
                ),
            ]
        )
        self.assertFalse(errors)

    @unittest.skipUnless(os.getenv("USERNAME_SMTP"), "Run only if SMTP available")
    def testSMTPNormalPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.NORMAL,
                    service=EventService.HARVESTER,
                    message="Normal priority notification 1.",
                ),
                Event(
                    type=EventType.USER,
                    priority=EventPriority.NORMAL,
                    service=EventService.HARVESTER,
                    message="Normal priority notification 2.",
                ),
            ]
        )
        self.assertFalse(errors)

    @unittest.skipUnless(os.getenv("USERNAME_SMTP"), "Run only if SMTP available")
    def testSTMPHighPriorityNotifications(self):
        errors = self.notifier.send_events_to_user(
            events=[
                Event(
                    type=EventType.USER,
                    priority=EventPriority.HIGH,
                    service=EventService.HARVESTER,
                    message="High priority notification 1.",
                ),
                Event(
                    type=EventType.USER,
                    priority=EventPriority.HIGH,
                    service=EventService.HARVESTER,
                    message="High priority notification 2.",
                ),
            ]
        )
        self.assertFalse(errors)
