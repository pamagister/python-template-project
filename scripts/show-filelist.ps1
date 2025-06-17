Get-ChildItem -Recurse -Force |
Where-Object {
    $_.FullName -notmatch '\.pytest_cache|\.git|\.ruff|\.venv|\.github|\\build|\.idea|\\htmlcov|\\site|\\*.pyc'
} |
ForEach-Object {
    Write-Output $_.FullName
}
