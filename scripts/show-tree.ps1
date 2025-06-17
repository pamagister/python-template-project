$basePath = Get-Location

Get-ChildItem -Recurse -Force |
Where-Object {
    $_.FullName -notmatch '\.pytest_cache|\.git|\.ruff|\.venv|\.github|\\build|\.idea|\\htmlcov|\\site|\\*.pyc'
} |
Sort-Object FullName |
ForEach-Object {
    $relativePath = $_.FullName.Substring($basePath.Path.Length + 1)
    $depth = ($relativePath -split '\\').Count - 1
    $indent = ('|   ' * $depth)
    $prefix = if ($_.PSIsContainer) { '[D]' } else { '[F]' }
    Write-Output "$indent$prefix $($_.Name)"
}
