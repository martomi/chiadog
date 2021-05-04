# Check Python version
if ! python3 -c 'import sys; assert sys.version_info >= (3,7)' 2> /dev/null;
then
  echo 'Found an unsupported version of Python'
  echo 'Chiadog requires Python 3.7+. Please update before proceeding with the installation'
  exit 1
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
