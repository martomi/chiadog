# Contributing

I've added a good amount of doxygen style comments and structured the code in a way that
should make this easier. Happy to provide feedback on PRs.

## Modular and extendable design

Here are some jump-off points where you can start adding extensions:

- additional [condition checks](src/chia_log/handlers/harvester_activity_handler.py) e.g. time since last eligible plot
- additional [parsers](src/chia_log/parsers) to monitor other parts of the log output (e.g. timelord)
- additional [log consumers](src/chia_log/log_consumer.py) to support watchdog over the network (NetworkLogConsumer)
- additional [notifiers](src/notifier) to support notifications over Slack, WhatsApp, E-mail, etc.

## Further feature ideas

- Handlers for automated recovery
    - auto-restart chia processes if node cannot re-sync
    - auto-restart xHCI devices to recover external HDDs

## Formatting and linting

Before submitting a PR make sure that your feature is covered with tests.

Install dependencies for auto-formatting and linting:

```
pip3 install black flake8 mypy
```

Run formatting, type checking and linting:

```
black src tests && mypy src tests && flake8 src tests
```

Run all tests:

```
PUSHOVER_API_TOKEN=<your_token> PUSHOVER_USER_KEY=<your_key> python3 -m unittest
```

Check that all passes and there aren't any warnings.
