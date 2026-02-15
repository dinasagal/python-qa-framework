$fixedResultsPath = Join-Path (Get-Location) "allure-results"

if (Test-Path $fixedResultsPath) {
	allure serve $fixedResultsPath
	exit $LASTEXITCODE
}

$latest = Get-ChildItem -Directory allure-results-* -ErrorAction SilentlyContinue |
	Sort-Object Name -Descending |
	Select-Object -First 1

if ($null -eq $latest) {
	Write-Error "No Allure results found. Expected ./allure-results or ./allure-results-*"
	exit 1
}

allure serve $latest.FullName
