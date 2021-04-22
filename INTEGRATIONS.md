# Supported Integrations for Notifications

The following integrations are **optional** - `chiadog`
is not dependent on any of them and can also run standalone. That being said, you'll get the most value out of it, when
you connect with one of the services below to receive real-time notifications about important events. You can also
enable more than one at the same time - please refer to the [config-example.yaml](config-example.yaml).

## Pushover

[Pushover](https://pushover.net/) is available for both Android and iOS. High priority notifications can be configured
from the Pushover app to overwrite any Silence or Do-Not-Disturb modes on your phone and sound a loud alarm at any time
of the day to make you aware of any issues in a timely manner.

Test with:

```
PUSHOVER_API_TOKEN=<api_token> PUSHOVER_USER_KEY=<user_key> python3 -m unittest tests.notifier.test_pushover_notifier
```

## SMTP / E-Mail

This integration uses SMTP to send an e-mail to a designated address. Alert information is sent in the subject line of
the e-mail. There several free SMTP relay providers with reasonable limits, some require that you have a domain name to
verify the sender email.

Test with:

```
SENDER="sender@example.com" SENDER_NAME="ChiaDog" RECIPIENT="you@example.com" HOST=smtp.example.com PORT=587 USERNAME_SMTP=username PASSWORD_SMTP=password python3 -m unittest tests.notifier.test_smtp_notifier
```

## Slack

[Slack](https://slack.com/) apps are a simple way to get notifications in a channel in your Slack workspace. Follow the
instructions for *Creating an App* on
the [Getting started with Incoming Webhooks](https://api.slack.com/messaging/webhooks#getting_started) guide.

Copy & paste the Webhook URL into your `config.yaml`, that's it!

Test with:

```
SLACK_WEBHOOK_URL=<webhook_url> python3 -m unittest tests.notifier.test_slack_notifier
```

## Discord

[Discord](https://discord.com/) built in Webhooks are a super simple way to get notifications sent to a text channel in
your server. Follow the instructions for *Making a Webhook* on
the [Intro to Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) page. Copy & paste
the Webhook URL into your `config.yaml`, that's it!

Test with:

```
DISCORD_WEBHOOK_URL=<webhook_url> python3 -m unittest tests.notifier.test_discord_notifier
```

## Telegram

This integration uses the [Telegram's Bot API](https://core.telegram.org/bots). You can create a new bot for yourself
by [sending a message to BotFather](https://core.telegram.org/bots#6-botfather).

For `chat_id` you need to enter your Telegram username or ID. For me only ID worked, you can find out your Telegram ID
by messaging the [IDBot](https://telegram.me/myidbot). You need to also first message your bot to make sure it knows
about you and can send you notifications.

Test with:

```
TELEGRAM_BOT_TOKEN=<bot_token> TELEGRAM_CHAT_ID=<your_id> python3 -m unittest tests.notifier.test_telegram_notifier
```

## Shell Script (beta)

*Beware: This feature is in **beta** stage and future versions might not maintain backward compatibility!
Currently, you need to parse out information from the message text which might change. In the future there'll be a
different mechanism for identifying message type and payload.*

Test with:

```
python3 -m unittest tests.notifier.test_script_notifier
```


