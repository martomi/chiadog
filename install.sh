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
