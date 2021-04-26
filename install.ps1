# Create virtual environment
python -m venv .venv

# Activate the virtual environment
./.venv/Scripts/activate.ps1

# Update pip to latest version
python -m pip install --upgrade pip

# Install dependencies
pip install wheel

pip install -r requirements.txt 

# Deactivate virtual env
deactivate
