# std
import unittest
from pathlib import Path

# project
from src.chia_log.parsers import farmer_server_parser


class TestFarmerServerParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = farmer_server_parser.FarmerServerParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/farmer_server"
        with open(self.example_logs_path / "nominal.txt") as f:
            self.nominal_logs = f.read()

    def tearDown(self) -> None:
        pass

    def testBasicParsing(self):
        for logs in [self.nominal_logs]:

            # Check that important fields are correctly parsed
            activity_messages = self.parser.parse(logs)
            self.assertNotEqual(len(activity_messages), 0, "No log messages found")

            expected_peer_hashes = ["20388420", "ea61688b", "fe1eb730", "c3e3eb9a",
                                    "20388420", "fe1eb730", "ea61688b", "c3e3eb9a"]
            expected_ip_addresses = ["127.0.0.1", "192.168.178.22", "178.19.176.201",
                                    "131.2.211.71", "127.0.0.1", "178.19.176.201",
                                    "192.168.178.22", "131.2.211.71"]

            for msg, peer_hash, ip_addr in zip(
                activity_messages,
                expected_peer_hashes,
                expected_ip_addresses,
            ):
                self.assertEqual(msg.peer_hash, peer_hash, "Peer hash don't match")
                self.assertEqual(msg.ip_addr, ip_addr, "IP Addr don't match")

            # Check arithmetic with parsed timestamps works
            prev_timestamp = activity_messages[0].timestamp
            for msg in activity_messages[1:]:
                seconds_since_last_activity = (msg.timestamp - prev_timestamp).seconds
                self.assertLess(seconds_since_last_activity, 10, "Unexpected duration between farmer_server events")
                prev_timestamp = msg.timestamp


if __name__ == "__main__":
    unittest.main()
