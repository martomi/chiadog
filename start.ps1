$command = "py"
if (Get-Command python -errorAction SilentlyContinue) {
    $command = "python"
}
elseif (Get-Command python3 -errorAction SilentlyContinue) {
    $command = "python3"
}

# Activate the virtual environment
./.venv/Scripts/activate.ps1

# Start the ChiaDog
Invoke-expression "$($command) main.py --config config.yaml"
