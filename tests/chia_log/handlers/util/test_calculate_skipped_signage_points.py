# std
import unittest
from datetime import datetime, timedelta
from random import randrange

# project
from src.chia_log.handlers.util.calculate_skipped_signage_points import calculate_skipped_signage_points


class TestCalculateSkippedSignagePoints(unittest.TestCase):
    def setUp(self) -> None:
        self.number = 1000
        self.timestamps = []
        self.ids = []
        start_ts = datetime.now()
        for i in range(self.number):
            self.timestamps.append(start_ts)
            self.ids.append((i % 64) + 1)
            start_ts += timedelta(seconds=randrange(7, 10))

    def testNoSkips(self):
        for i in range(1, self.number):
            valid, skipped = calculate_skipped_signage_points(
                prev_ts=self.timestamps[i - 1], prev_id=self.ids[i - 1], curr_ts=self.timestamps[i], curr_id=self.ids[i]
            )
            self.assertTrue(valid)
            self.assertEqual(skipped, 0)

    def testSingleSkips(self):
        skip_indices = [42, 63, 124, 234, 333, 335, 338, 420]
        skip_tss = []
        skip_ids = []
        for i in range(len(self.timestamps)):
            if i not in skip_indices:
                skip_tss.append(self.timestamps[i])
                skip_ids.append(self.ids[i])

        total_skipped = 0
        all_valid = True
        for i in range(1, len(skip_ids)):
            valid, skips = calculate_skipped_signage_points(
                prev_ts=skip_tss[i - 1], prev_id=skip_ids[i - 1], curr_ts=skip_tss[i], curr_id=skip_ids[i]
            )
            all_valid = all_valid and valid
            total_skipped += skips

        self.assertTrue(all_valid)
        self.assertEqual(len(skip_indices), total_skipped)

    def testMultipleSkipsInRow(self):
        skip_indices = range(42, 69)
        skip_tss = []
        skip_ids = []
        for i in range(len(self.timestamps)):
            if i not in skip_indices:
                skip_tss.append(self.timestamps[i])
                skip_ids.append(self.ids[i])

        total_skipped = 0
        all_valid = True
        for i in range(1, len(skip_ids)):
            valid, skips = calculate_skipped_signage_points(
                prev_ts=skip_tss[i - 1], prev_id=skip_ids[i - 1], curr_ts=skip_tss[i], curr_id=skip_ids[i]
            )
            all_valid = all_valid and valid
            total_skipped += skips

        self.assertTrue(all_valid)
        self.assertEqual(len(skip_indices), total_skipped)

    def testMultiRolloverSkip(self):
        skip_indices = range(42, 420)
        skip_tss = []
        skip_ids = []
        for i in range(len(self.timestamps)):
            if i not in skip_indices:
                skip_tss.append(self.timestamps[i])
                skip_ids.append(self.ids[i])

        total_skipped = 0
        all_valid = True
        for i in range(1, len(skip_ids)):
            valid, skips = calculate_skipped_signage_points(
                prev_ts=skip_tss[i - 1], prev_id=skip_ids[i - 1], curr_ts=skip_tss[i], curr_id=skip_ids[i]
            )
            all_valid = all_valid and valid
            total_skipped += skips

        self.assertTrue(all_valid)
        self.assertEqual(len(skip_indices), total_skipped)


if __name__ == "__main__":
    unittest.main()
