# std
from datetime import datetime
from typing import Tuple
import logging

roll_over_point = 64
expected_diff_seconds = 9
smallest_expected_diff_seconds = 7


def calculate_skipped_signage_points(
    prev_ts: datetime, prev_id: int, curr_ts: datetime, curr_id: int
) -> Tuple[bool, int]:
    """Calculate most likely amount of skipped signage points based on IDs and timestamps
    If we detect out-of-order signage point event, the calculation is flagged as invalid.

    :returns Validity and number of skipped signage points in case of valid calculation
    """
    valid = True
    diff_id = curr_id - prev_id
    diff_id_roll = (roll_over_point - prev_id) + curr_id
    diff_seconds = (curr_ts - prev_ts).seconds

    one_roll_duration = roll_over_point * expected_diff_seconds

    roll_count = round(diff_seconds / one_roll_duration)
    expected_diff_id = round(diff_seconds / expected_diff_seconds)
    expected_diff_id = expected_diff_id % one_roll_duration

    distance_to_expected = abs(expected_diff_id - diff_id)
    distance_to_expected_roll = abs(expected_diff_id - diff_id_roll)

    if distance_to_expected < distance_to_expected_roll:
        skipped = (diff_id + roll_over_point * roll_count) - 1
    else:
        skipped = (diff_id_roll + roll_over_point * roll_count) - 1

    # Handle possible bursts of shuffled signage points resulting from a fork
    upper_bound_expected_diff_id = round(diff_seconds / smallest_expected_diff_seconds)
    if skipped > upper_bound_expected_diff_id:
        valid, skipped = False, 0
        logging.debug(
            f"Probably out of order signage point IDs {prev_id} and {curr_id} "
            f"with timestamps {prev_ts} and {curr_ts}"
        )

    return valid, skipped
