# Installing Chiadog on Windows

## Pre-requisites

- Linux, MacOS & Windows
- [Python 3.7+](https://www.python.org/downloads/windows/)
- [Git](https://git-scm.com/downloads)
- Enabled `INFO` logs on your chia farmer

This guide contains instructions on how to set up a **local** `chiadog` consumer on Windows.
If you are looking for instructions on how to set up remote monitoring on a Windows machine, 
please refer to [this article](/wiki/Monitoring-Multiple-Harvesters) 
instead.

Looking for installation instructions for Linux or MacOS? Head over to the 
general [README](README.md).

## How to enable INFO logs on chia farmer?

First we'll set Chia's log level to `INFO`. This ensures that all logs necessary for `chiadog` to operate 
are available under `C:\Users\[YOUR-USER]\.chia\mainnet\log\debug.log`.

1. Open the file `C:\Users\[YOUR-USER]\.chia\mainnet\config\config.yaml` in your favorite text editor
2. Find the line that reads `log_level: DEBUG` (under the `farmer` section) and change this to `log_level: INFO`
3. Restart the GUI or run `chia start --restart farmer` from the command line

## Installation

_For updating from previous version, see section below._

1. Open a `PowerShell` command line

2. Clone the repository somewhere on your computer (ex. `C:\Users\[YOUR-USER]\`)

```
cd C:\Users\[YOUR-USER]\
git clone https://github.com/martomi/chiadog.git
cd chiadog
```

3. Create a virtual environment for `chiadog` to run in

```
# Create a new virtual environment in this folder called 'venv'
python.exe -m venv venv

# Activate the newly created virtual environment
. ./venv/Scripts/activate
```

**Note**: if you get an error saying 'The term 'python.exe' is not recognized' or 'Python was not found', change 
`python.exe` in the last line of the above code block to `py.exe` or `python3.exe`. 
If none of these work, it is likely that Python was not installed on your system. Refer to 
[this website](https://www.python.org/downloads/windows/) in order to download the latest version. 

4. Update `pip` package manager and install `chiadog` dependencies 

```
# Update pip3 to latest version
python.exe -m pip install --upgrade pip

# Install dependencies
pip3 install wheel
pip3 install -r requirements.txt

# Deactivate the virtual environment again
deactivate
```

5. Make a copy of the example config file

```
cp config-example.yaml config.yaml
```

6. Open up the newly created `config.yaml` in your favorite text editor and configure it 
   to your preferences.

## Updating to the latest release

_Skip this if you just did a fresh install of `chiadog`_.

```
cd chiadog

git fetch
git checkout main
git pull

# Recreate and activate the virtual environment
python.exe -m venv venv
. ./venv/Scripts/activate

# Reinstall dependencies
pip3 install wheel
pip3 install -r requirements.txt

# Deactivate the virtual environment again
deactivate
```

> Important: Automated migration of config is not supported. Please check that your `config.yaml` has all new 
> fields introduced in `config-example.yaml` and add anything missing. If correctly migrated, you shouldn't get 
> any ERROR logs.

## Monitoring a local harvester / farmer

1. Open `config.yaml` and configure `file_log_consumer`:
   - You need to enable the file log consumer to read local chia log files
   - Double-check that the path to your chia logs is correct
   - The file path to the log file on Windows needs to be specified in full. 
     E.g. `C:\Users\[YOUR-USER]\.chia\mainnet\log\debug.log` 

2. From PowerShell, activate the virtual environment and start `chiadog`

```
# Make sure you are in the directory that you previously installed chiadog in
cd C:\Users\[YOUR-USER]\chiadog

# Activate the virtual environment
. ./venv/Scripts/activate

# Start the watchdog
python.exe main.py --config config.yaml
```

3. Verify that your plots are detected. Within a few seconds you should see INFO log:

```
Detected new plots. Farming with 42 plots.
```

## Monitoring a remote harvester
Chiadog allows you to monitor multiple remote harvesters while running chiadog on a separate machine. 
Please refer to the Wiki article on [Monitoring Remote Harvesters](/wiki/Monitoring-Multiple-Harvesters)
for more information on how to set this up.
