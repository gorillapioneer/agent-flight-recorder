param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Arguments
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$RepoRoot;$env:PYTHONPATH"
} else {
    $env:PYTHONPATH = $RepoRoot
}

python -m agent_flight_recorder @Arguments
exit $LASTEXITCODE

