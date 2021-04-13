# Contributing

I've added a good amount of doxygen style comments and structured the code in a way that should make this easier. Happy
to provide feedback on PRs.

## Modular and extendable design

Here are some jump-off points where you can start adding extensions:

- additional [condition checks](src/chia_log/handlers/harvester_activity_handler.py) e.g. time since last eligible plot
- additional [parsers](src/chia_log/parsers) to monitor other parts of the log output (e.g. timelord)
- additional [notifiers](src/notifier) to support notifications over Slack, WhatsApp, E-mail, etc.

## How to contribute?

1. Fork the repository
2. Create a feature or bugfix branch from `dev`
3. Push your changes to the branch on your forked repository
4. Submit a PR towards `dev` branch of this repository.

> Note: It's important to base your work on top of the `dev` branch. The `main` branch will only be
> updated once a new release is ready to be pushed. I'll then be merging all changes from `dev` into `main`.

## Commit messages

Please be short and descriptive. In this repository we use the imperative form. For more information on good commit
messages, I recommend the following article:

- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/).

## Formatting and linting

Before submitting a PR make sure that your feature is covered with tests.

1. Install dependencies for auto-formatting and linting:

```
pip3 install black flake8 mypy
```

2. Run formatting, type checking and linting:

```
black src tests && mypy src tests && flake8 src tests
```

3. Run tests:

```
PUSHOVER_API_TOKEN=<your_token> PUSHOVER_USER_KEY=<your_key> TELEGRAM_BOT_TOKEN=<your_token> TELEGRAM_CHAT_ID=<your_chat_id>  python3 -m unittest
```

Check that all passes and there aren't any warnings.

> TODO: Make notifier tests optional so that not everyone needs to get tokens for all integrations.
> For now, if you don't have all tokens, you can selectively run just the tests for your feature.

## Have fun

Most importantly: Have fun and if you're unsure about some contribution, don't shy away from submit a Pull Request
anyway. We can use that as a basis for discussions, provide feedback and iterate on further improvements. Cheers!