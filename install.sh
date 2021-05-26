#!/bin/bash

# Function that checks if a package is installed locally
function package_installed() {
  dpkg -s "$1" &> /dev/null
}

# Check Python version
if ! python3 -c 'import sys; assert sys.version_info >= (3,7)' 2> /dev/null;
then
  echo 'Found an unsupported version of Python'
  echo 'Chiadog requires Python 3.7+. Please update before proceeding with the installation'
  exit 1
fi

# Check existence of required python build packages
if ! package_installed libpython3-dev || ! package_installed build-essential; then
  sudo apt-get update
  sudo apt-get install libpython3-dev build-essential -y
fi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
. ./venv/bin/activate

# Update pip3 to latest version
python3 -m pip install --upgrade pip

# Install dependencies
pip3 install wheel && pip3 install -r requirements.txt

# Deactivate virtual environment
deactivate
