# std
import unittest
from pathlib import Path

# project
from src.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self) -> None:
        self.config_dir = Path(__file__).resolve().parents[1]

    def testBasic(self):
        with self.assertRaises(ValueError):
            _ = Config(self.config_dir / "wrong.yaml")

        config = Config(self.config_dir / "config-example.yaml")
        notifier_config = config.get_notifier_config()
        self.assertEqual(notifier_config["pushover"]["enable"], False)
        self.assertEqual(notifier_config["pushover"]["credentials"]["api_token"], "dummy_token")
        self.assertEqual(notifier_config["pushover"]["credentials"]["user_key"], "dummy_key")

        chia_logs_config = config.get_chia_logs_config()
        self.assertEqual(chia_logs_config["file_log_consumer"]["enable"], True)
        self.assertEqual(chia_logs_config["file_log_consumer"]["file_path"], "~/.chia/mainnet/log/debug.log")


if __name__ == "__main__":
    unittest.main()
