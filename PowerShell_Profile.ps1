If (Test-Path 'env:SCOOP') {
    Import-Module $(Join-Path -Path $env:SCOOP -ChildPath 'apps\scoop\current\supporting\completion\Scoop-Completion.psd1') -ErrorAction SilentlyContinue
}