# std
from datetime import datetime
import logging

roll_over_point = 64
expected_diff_seconds = 9


def calculate_skipped_signage_points(prev_ts: datetime, prev_id: int, curr_ts: datetime, curr_id: int):
    """Calculate most likely amount of skipped signage points based on IDs and timestamps"""

    diff_id = curr_id - prev_id
    diff_id_roll = (roll_over_point - prev_id) + curr_id
    diff_seconds = (curr_ts - prev_ts).seconds

    # This is hacky addition to prevent false alarms for some network-wide issues that
    # aren't necessarily related to the local node. See "testNetworkScramble" test case.
    # Signage points are expected approx every 8-10 seconds. If a point was skipped for real
    # then we expect the time difference to be at least 2*8 seconds. Otherwise it's flaky event.
    if diff_seconds < expected_diff_seconds * 1.5:
        if diff_id != 1 and diff_id_roll != 1:
            logging.info(
                f"Probably out of order signage point IDs {prev_id} and {curr_id} "
                f"with timestamps {prev_ts} and {curr_ts}"
            )
        return 0

    one_roll_duration = roll_over_point * expected_diff_seconds

    roll_count = round(diff_seconds / one_roll_duration)
    expected_diff_id = round(diff_seconds / expected_diff_seconds)
    expected_diff_id = expected_diff_id % one_roll_duration

    distance_to_expected = abs(expected_diff_id - diff_id)
    distance_to_expected_roll = abs(expected_diff_id - diff_id_roll)

    if distance_to_expected < distance_to_expected_roll:
        return (diff_id + roll_over_point * roll_count) - 1

    return (diff_id_roll + roll_over_point * roll_count) - 1
