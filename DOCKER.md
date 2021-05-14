## Installation on Docker

### Clone the repository

```
git clone https://github.com/martomi/chiadog.git
cd chiadog
```

### Build the Docker image

#### Latest version

```
docker image build -t chiadog:latest .
```

#### Specific version

```
docker image build -t chiadog:0.5.0 --build-arg BRANCH=v0.5.0 .
```

### Copy the example config file

```
cp config-example.yaml config.yaml
```

### Edit the configuration

Open up `config.yaml` in your editor and configure it to your preferences.

## Monitoring a local harvester / farmer

### Start the watchdog

```
docker run --name chiadog --rm -v ${HOME}/.chia/mainnet/log/debug.log:/chiadog/debug.log:ro \
    -v ${PWD}/config.yaml:/chiadog/config.yaml:ro -d \
    chiadog:${VERSION}
```

You should adapt the following options to your environment:
 - `${HOME}/.chia/mainnet/log/debug.log` should be replaced by the path of your `debug.log` file
 - `/chiadog/debug.log` should be replaced by the value of `chia_logs.file_log_consumer.file_path` setting
 - `${VERSION}` should be replaced by the version of the previously built Docker image

### Verify that your plots are detected

```
docker logs -f chiadog
```

Within a few seconds you should see INFO log:

```
Detected new plots. Farming with 42 plots.
```
