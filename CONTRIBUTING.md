# Contributing

## High-level Architecture Overview

You can get a high-level glimpse on how the different components interact in the diagram below. That should
make it easier to navigate the codebase. Please refer to the in-line code documentation for more information.

![High-level architecture diagram](./docs/architecture.png "High-level architecture diagram")

You can open and edit the [architecture.drawio](./docs/architecture.drawio) file on [diagrams.net](https://app.diagrams.net).

## How to contribute?

1. Fork the repository
2. Create a feature or bugfix branch from `main`
3. Push your changes to the branch on your forked repository
4. Submit a PR towards `main` branch of this repository.

## Commit messages

Please use short and descriptive titles and expand on the "why" inside the body of the commit message if necessary.
In this repository we use the imperative form. For more information on good commit
messages, I recommend the following article:

- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/).

## Formatting and linting

Before submitting a PR make sure that your feature is covered with tests.

1. Install dependencies for auto-formatting and linting:

```
pip3 install -r testing_requirements.txt
```

2. Run formatting, type checking and linting:

```
black src tests *.py && mypy src tests *.py && flake8 src tests *.py
```

3. Run tests:

```
PUSHOVER_API_TOKEN=<your_token> PUSHOVER_USER_KEY=<your_key> TELEGRAM_BOT_TOKEN=<your_token> TELEGRAM_CHAT_ID=<your_chat_id>  python3 -m unittest
```

Check that all passes and there aren't any warnings.

If you did not modify any logic in one of the notifiers, you can skip these tests and run all others without specifying
any tokens:

```
python3 -m unittest
```

4. Verify test coverage:

As before, include env variables needed to live test functionality you touched.

```
python3 -m coverage run -m unittest
python3 -m coverage report
```

## Testing remote APIs

To strike a balance between hermetic tests and actually testing against a live API, `VCR.py` is utilized.
By default tests with prerecorded interactions are tested hermetically. If you instead want to test live or record a new cassette, remove the cassette file and run the test with sufficient env variables to produce a valid replacement result.

For example:
```
rm tests/cassette/keep_alive_monitor/*
REMOTE_PING_URL=https://hc-ping.com/<your-token> python3 -m unittest tests.notifier.test_keep_alive_monitor
```

> **Warning**
> Before committing a cassette file make sure you've sanitized it of your own tokens!
> Normally this is done at the VCR config level, see: [VCR.py: Filter sensitive data from the request](https://vcrpy.readthedocs.io/en/latest/advanced.html#filter-sensitive-data-from-the-request)

## Have fun

Most importantly: Have fun and if you're unsure about some contribution, don't shy away from submit a Pull Request
anyway. We can use that as a basis for discussions, provide feedback and iterate on further improvements. Cheers!
