# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2021-04-05

### Added

- Ability to monitor logs of remote harvesters over SSH
- A check for skipped signage points on the full node
- More logs to stdout for better transparency of what happens
- Configurable title prefix for notifications
    - Helps distinguish notifications from different harvesters

### Changed

- Warning threshold for time since last farming event increased to 60 seconds
    - This prevents receiving "false alarm" notification multiple time per day

### Fixed

- Possible race condition when initializing LogHandler

## [0.1.0] - 2021-04-04

### Added

- First release of ChiaDog!
- Adds basic log file parser for chia logs.
- Adds basic condition checks for harvester operations.
- Adds integration for Pushover (mobile notifications).

[Unreleased]: https://github.com/martomi/chiadog/compare/v0.2.0...dev

[0.2.0]: https://github.com/martomi/chiadog/releases/tag/v0.2.0

[0.1.0]: https://github.com/martomi/chiadog/releases/tag/v0.1.0
