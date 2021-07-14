# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.1] - 2021-07-14

The purpose of this minor release is to get out a few fixes. No major new features in this release.

### Added
- Config: Now you can specify minutes (hh:mm) for daily stats scheduling (thanks [@kanasite](https://github.com/kanasite))

### Fixed
- Fix corrupt log offset file after unexpected shutdown of chiadog (thanks [@pieterhelsen](https://github.com/pieterhelsen))
- Windows: Fix parsing for finished signage points (thanks [@pieterhelsen](https://github.com/pieterhelsen))
- Windows: Fix check for rotated log files (thanks [@mezzovide](https://github.com/mezzovide))
- Install script: Fix detection for already installed packages (thanks [@bradclow](https://github.com/bradclow))
- Check version: Fix cleanup of git process after execution (thanks [@pieterhelsen](https://github.com/pieterhelsen))

## [0.6.0] - 2021-05-25

### Added

- Found proof notifications (again)
- Configurable frequency for daily stats summary (24h default)
- New flag `--version` to display the current version (thanks [@pieterhelsen](https://github.com/pieterhelsen))
- Scripts to automate launching for Windows (thanks [fiveangle](https://github.com/fiveangle))
- Windows WSL installation instructions (thanks [@ougni](https://github.com/ougni))

### Changed

- Increased the warning threshold for last farming events from 60 to 90 seconds.
- Individual skipped signage points do not trigger notifications anymore. They will be part of daily summary.
- Improved Linux install script by installing common dependencies
  (thanks [@pieterhelsen](https://github.com/pieterhelsen))

### Fixed

- Improved log rotation handling on Windows (thanks [@pieterhelsen](https://github.com/pieterhelsen))
- Misleading notifications for decreasing plots during copying. The warning threshold is now 2.
- Wallet notification formatting - received coins are now displayed without scientific notation.
- More correct handling of skipped signage points - most cases are correctly detected but not all.
  (thanks [@ctrlaltdel](https://github.com/ctrlaltdel) for test-case submission)
- More accurate daily stats about skipped signage points - now covered by unit test.

## [0.5.1] - 2021-05-17

The purpose of this minor release is to get out a few fixes. No new features in this release.

### Fixed

- Another fix for handling of signage points around network forks. Should further reduce false-alarm notifications.
- Correctly parse number of eligible plots when larger than 9 (thanks [@ctrlaltdel](https://github.com/ctrlaltdel))
- Correctly parse added coin events and send out reward notifications (thanks [@skweee](https://github.com/skweee))
- Check potential out-of-bound config values for MQTT integration
  (thanks [@pieterhelsen](https://github.com/pieterhelsen))

## [0.5.0] - 2021-05-13

### Added

- Daily Stats: Now include total searches and the percentage of slow seeks
  (thanks [@pieterhelsen](https://github.com/pieterhelsen))
- (Optional) Notification for received rewards / coins. You need to migrate your `config.yaml` by
  adding `wallet_events: true` to your notifiers. See the `config-example.yaml` for reference.
- (Optional) Integrations: MQTT Notifier (thanks [@pieterhelsen](https://github.com/pieterhelsen))
- (Optional) Custom SSH port for remote monitoring. See `config-example.yaml` for example.
  (thanks [@turekjiri](https://github.com/turekjiri))
- More detailed instructions for setting up on [Windows](https://github.com/martomi/chiadog/blob/dev/WINDOWS.md)
  (thanks [@pieterhelsen](https://github.com/pieterhelsen)). Windows support is still considered experimental. There's a
  known issue about [possible offline harvester notifications](https://github.com/martomi/chiadog/issues/72).
- Check for required Python version in the install script (thanks [@pieterhelsen](https://github.com/pieterhelsen))

### Changed

- Logs about out-of-order signage points are now moved to DEBUG log level. This will declutter the logs from events that
  are expected when the blockchain experiences a fork and a block is reversed.

### Fixed

- Wrongly detected skipped signage points caused as a consequence of out-of-order events. The previous signage point ID
  is now reset when this happens and correct tracking is resumed.
- Remote monitoring from Windows machine to Linux machine or vice-versa. (
  thanks [@pieterhelsen](https://github.com/pieterhelsen))
- Unit tests on Windows (now UTF-8 encoding is explicitly specified -
  thanks [@pieterhelsen](https://github.com/pieterhelsen))

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

[Unreleased]: https://github.com/martomi/chiadog/compare/v0.6.1...dev

[0.6.1]: https://github.com/martomi/chiadog/releases/tag/v0.6.1

[0.6.0]: https://github.com/martomi/chiadog/releases/tag/v0.6.0

[0.5.1]: https://github.com/martomi/chiadog/releases/tag/v0.5.1

[0.5.0]: https://github.com/martomi/chiadog/releases/tag/v0.5.0

[0.4.1]: https://github.com/martomi/chiadog/releases/tag/v0.4.1

[0.4.0]: https://github.com/martomi/chiadog/releases/tag/v0.4.0

[0.3.0]: https://github.com/martomi/chiadog/releases/tag/v0.3.0

[0.2.0]: https://github.com/martomi/chiadog/releases/tag/v0.2.0

[0.1.0]: https://github.com/martomi/chiadog/releases/tag/v0.1.0
