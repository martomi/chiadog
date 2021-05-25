# Installing Chiadog on Windows

> This is still considered **experimental**. If you have any issues please report
> them after browsing the existing issues
> [labeled with bug](https://github.com/martomi/chiadog/labels/bug) to avoid duplicates.

> If you get unexpected "Your harvester appears offline! No events for the past xxxx seconds" notifications,
> please report [here](https://github.com/martomi/chiadog/issues/72).

## Pre-requisites

- Windows / Windows + WSL(Ubuntu)
- [Python 3.7+](https://www.python.org/downloads/windows/)
- [Git](https://git-scm.com/downloads)
- Enabled `INFO` logs on your chia farmer

This guide contains instructions on how to set up a **local** `chiadog` consumer on Windows. If you are looking for
instructions on how to set up remote monitoring on a Windows machine, please refer
to [this article](/wiki/Monitoring-Multiple-Harvesters)
instead.

Looking for installation instructions for Linux or MacOS? Head over to the general [README](README.md).

## How to enable INFO logs on chia farmer?

First we'll set Chia's log level to `INFO`. This ensures that all logs necessary for `chiadog` to operate are available
under `C:\Users\[YOUR-USER]\.chia\mainnet\log\debug.log`.

1. Open the file `C:\Users\[YOUR-USER]\.chia\mainnet\config\config.yaml` in your favorite text editor
2. Find the line that reads `log_level: DEBUG` (under the `farmer` section) and change this to `log_level: INFO`
3. Restart the GUI or run `chia start --restart farmer` from the command line

## 1.1 Powershell(Native) Installation

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
. .\venv\Scripts\activate
```

**Note**: if you get an error saying 'The term 'python.exe' is not recognized' or 'Python was not found', change
`python.exe` in the last line of the above code block to `py.exe` or `python3.exe`. If none of these work, it is likely
that Python was not installed on your system. Refer to
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

6. Open up the newly created `config.yaml` in your favorite text editor and configure it to your preferences.

## 1.2 WSL(Ubuntu) Installation

**Reminder**: `INFO` level log in Chia must be enabled (`chia configure -log-level=INFO`)

**Windows Subsystem for Linux (WSL)**: Allows you to run Linux distributions (e.g. Ubuntu) within Windows 10. If you
don't have WSL already, follow the instructions [here](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

1. Open `WSL-Ubuntu`

```
   git clone https://github.com/martomi/chiadog.git
   cd chiadog
```

2. Run the install script.

```
./install.sh
```

3. Copy the example config file

```
cp config-example.yaml config.yaml
```

4. Open up `config.yaml` in your editor

   4.1 Set chia log location:

   ```yaml
   chia_logs:
     file_log_consumer:
       enable: true
       file_path: "/mnt/c/Users/<user-name>/.chia/mainnet/log/debug.log"
   ```

   4.2 configure it to your preferences for notification services (same as OSX/Ubuntu)

---

## Updating to the latest release

_Skip this if you just did a fresh install of `chiadog`_.

```
cd chiadog

git fetch
git checkout main
git pull

# Recreate and activate the virtual environment
python.exe -m venv venv
. .\venv\Scripts\activate

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

2. Launch the watchdog:

```
# Make sure you are in the directory that you previously installed chiadog in
cd C:\Users\[YOUR-USER]\chiadog

# Start the watchdog
.\start.cmd
```
Note: You may also create a shortcut to this script and move it to any convenient name and location to launch chiadog by double-clicking it.

3. Verify that your plots are detected. Within a few seconds you should see INFO log:

```
Detected new plots. Farming with 42 plots.
```

## Monitoring a remote harvester

Chiadog allows you to monitor multiple remote harvesters while running chiadog on a separate machine. Please refer to
the Wiki article on [Monitoring Remote Harvesters](/wiki/Monitoring-Multiple-Harvesters)
for more information on how to set this up.
