$command = "py"
if (Get-Command python -errorAction SilentlyContinue) {
    $command = "python"
}
elseif (Get-Command python3 -errorAction SilentlyContinue) {
    $command = "python3"
}

# Create virtual environment
Invoke-expression "$($command) -m venv .venv"

# Activate the virtual environment
./.venv/Scripts/activate.ps1

# Update pip to latest version
Invoke-expression "$($command) -m pip install --upgrade pip"

# Install dependencies
pip install wheel

pip install -r requirements.txt 

# Deactivate virtual env
deactivate
