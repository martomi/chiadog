# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2021-04-27

### Added

- Daily report for number of occasions where plot seeking time is above 5 and 15 seconds.
  See [this issue](https://github.com/martomi/chiadog/issues/49) to understand why you really want response time < 5
  seconds and not 30 seconds. You're going to get a notification for anything over 20 seconds which is in the critical
  range.
- Windows: Experimental support (thanks [@skrustev](https://github.com/skrustev)) - not yet a one-click easy setup - it
  may require some tinkering. If you are comfortable with the shell, please try it out and provide us feedback.
- Windows: Support for remote harvesters on Windows machines (thanks [@pieterhelsen](https://github.com/pieterhelsen))

### Fixed

- [ZeroDivisionError](https://github.com/martomi/chiadog/issues/46) on the daily report. Occurs when running `chiadog`
  on a standalone harvester where logs about signage points are not present. Now this case is handled correctly.

## [0.4.0] - 2021-04-25

> This release contains backward incompatible changes to the config.yaml. Please transfer your API keys to a new copy of the config-example.yaml file when updating.

### Added

- (Optional) Daily summary notification with health status. The [README](./README.md) contains an example.
- (Recommended) Remote endpoint to monitor that `chiadog` is alive. Provides double redundancy in case of a crash,
  network failure or computer shutdown / reboot. For more information, refer to
  the [Advanced Usage](./README.md#advanced-usage) section.
- (Optional) Discord notifications (thanks [@kilbot](https://github.com/kilbot))
- (Optional) SMTP / Email notifications (thanks [@mikehw](https://github.com/mikehw))
- (Optional) Slack notifications (thanks [@Starttoaster](https://github.com/Starttoaster))
- Developers: There's now a [component diagram](./docs/architecture.png) to make auditing
  and [contributions](./CONTRIBUTING.md) easier.

### Changed

- The absolute number of skipped signage points is now calculated and reported.
- No more notifications about skipping individual signage points. They'll still appear in the logs and in the daily
  summary. If multiple SP skips are observed within 60 minutes, you'll still get a notification. This should decrease
  the unnecessary notifications.
- Notifications for found proofs are not sent anymore. These *were* going to be replaced by configurable notifications
  for received coins by the wallet because found proofs != farmed blocks and rewards. Unfortunately, this
  feature [had to be dropped](https://github.com/martomi/chiadog/pull/40) last minute because it relies on a log which
  got removed from the most recent Chia releases. You'll still get the number of found proofs in the daily summary
  notification. Perhaps next release will be parsing out the "Farmed" logs.

### Fixed

- Handling a previously uncaught exception for network requests which could cause `chiadog` to crash.

## [0.3.0] - 2021-04-13

### Added

- (Optional) Telegram notifications (thanks [@MiguelCarranza](https://github.com/MiguelCarranza)
  and [@greimela](https://github.com/greimela))
- (Optional) Custom script notifications (thanks [@ajacobson](https://github.com/ajacobson))

### Fixed

- Parser adjusted to new log format for Chia 1.0.4 (thanks [@greimela](https://github.com/greimela)). The new log format
  from Chia breaks all previous versions of `chiadog`. The changed parser is backward compatible with the old format
  too, so you're safe to install this even if still using an older version.

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

[Unreleased]: https://github.com/martomi/chiadog/compare/v0.4.1...dev

[0.4.1]: https://github.com/martomi/chiadog/releases/tag/v0.4.1

[0.4.0]: https://github.com/martomi/chiadog/releases/tag/v0.4.0

[0.3.0]: https://github.com/martomi/chiadog/releases/tag/v0.3.0

[0.2.0]: https://github.com/martomi/chiadog/releases/tag/v0.2.0

[0.1.0]: https://github.com/martomi/chiadog/releases/tag/v0.1.0
