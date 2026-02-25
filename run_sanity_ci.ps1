Write-Host "Running tests in CI mode (headless)..."

$env:CI="true"
pytest -m sanity -v

