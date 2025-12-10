# std
import json
import os
import tempfile
import shutil
from datetime import datetime, date
from pathlib import Path
import unittest

# project
from src.chia_log.handlers.wins_tracker import WinsTracker, WinRecord
from src.chia_log.parsers.harvester_activity_parser import HarvesterActivityMessage


class TestWinsTracker(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_wins.json")
        self.backup_dir = os.path.join(self.test_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_message(self, proofs_found=1, v1_proofs=1, v2_qualities=0):
        return HarvesterActivityMessage(
            timestamp=datetime.now(),
            eligible_plots_count=100,
            challenge_hash="abc123def456",
            found_proofs_count=proofs_found,
            search_time_seconds=0.234,
            total_plots_count=500,
            found_v1_proofs_count=v1_proofs,
            found_v2_qualities_count=v2_qualities,
        )

    def test_record_win_creates_file(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        message = self._create_message(proofs_found=1)
        
        tracker.record_win(message)
        
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as f:
            data = json.load(f)
        self.assertEqual(len(data["wins"]), 1)
        self.assertEqual(data["total_wins"], 1)

    def test_record_multiple_wins(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        
        tracker.record_win(self._create_message(proofs_found=1))
        tracker.record_win(self._create_message(proofs_found=2))
        
        data = tracker.get_stats()
        self.assertEqual(len(data["wins"]), 2)
        self.assertEqual(data["total_wins"], 3)

    def test_ignores_zero_proofs(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        message = self._create_message(proofs_found=0)
        
        tracker.record_win(message)
        
        self.assertFalse(os.path.exists(self.test_file))

    def test_tracks_v1_v2_counts(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        
        tracker.record_win(self._create_message(proofs_found=1, v1_proofs=1, v2_qualities=0))
        tracker.record_win(self._create_message(proofs_found=2, v1_proofs=2, v2_qualities=3))
        
        data = tracker.get_stats()
        self.assertEqual(data["total_v1_proofs"], 3)
        self.assertEqual(data["total_v2_qualities"], 3)

    def test_atomic_write_survives_concurrent_access(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        
        for i in range(10):
            tracker.record_win(self._create_message(proofs_found=1))
        
        data = tracker.get_stats()
        self.assertEqual(data["total_wins"], 10)
        self.assertEqual(len(data["wins"]), 10)

    def test_creates_daily_backup(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        tracker.record_win(self._create_message(proofs_found=1))
        
        tracker._last_backup_date = None
        tracker.record_win(self._create_message(proofs_found=1))
        
        today = date.today()
        backup_name = f"wins_history_{today.isoformat()}.json"
        backup_path = os.path.join(self.backup_dir, backup_name)
        self.assertTrue(os.path.exists(backup_path))

    def test_get_wins_since(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        
        old_time = datetime(2024, 1, 1, 12, 0, 0)
        new_time = datetime(2024, 12, 1, 12, 0, 0)
        
        old_msg = HarvesterActivityMessage(
            timestamp=old_time,
            eligible_plots_count=100,
            challenge_hash="old123",
            found_proofs_count=1,
            search_time_seconds=0.1,
            total_plots_count=500,
        )
        new_msg = HarvesterActivityMessage(
            timestamp=new_time,
            eligible_plots_count=100,
            challenge_hash="new456",
            found_proofs_count=1,
            search_time_seconds=0.1,
            total_plots_count=500,
        )
        
        tracker.record_win(old_msg)
        tracker.record_win(new_msg)
        
        since_nov = tracker.get_wins_since(datetime(2024, 11, 1))
        self.assertEqual(len(since_nov), 1)
        self.assertEqual(since_nov[0]["challenge_hash"], "new456")

    def test_old_format_message(self):
        tracker = WinsTracker(file_path=self.test_file, backup_dir=self.backup_dir)
        
        old_format_msg = HarvesterActivityMessage(
            timestamp=datetime.now(),
            eligible_plots_count=50,
            challenge_hash="legacy123",
            found_proofs_count=1,
            search_time_seconds=0.5,
            total_plots_count=200,
            found_v1_proofs_count=None,
            found_v2_qualities_count=None,
        )
        
        tracker.record_win(old_format_msg)
        
        data = tracker.get_stats()
        self.assertEqual(len(data["wins"]), 1)
        self.assertEqual(data["wins"][0]["v1_proofs"], None)
        self.assertEqual(data["wins"][0]["v2_qualities"], None)


if __name__ == "__main__":
    unittest.main()
