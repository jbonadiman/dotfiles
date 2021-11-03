$step_name="Shovel Installation"



$step_name="Packages Installation"

Write-Host "installing 'aria2'..."
shovel install aria2

Write-Host "adding 'java' bucket to shovel..."
shovel bucket add java

Write-Host "installing 'openjdk'..."
shovel install openjdk

Write-Host "adding 'jetbrains' bucket to shovel..."
shovel bucket add jetbrains

Write-Host "adding 'nerd-fonts' bucket to shovel..."
shovel bucket add nerd-fonts

function Install-PersonalPackages {
    winget install netflix --accept-package-agreements
}

function Install-Shovel {
    Write-Host "[$step_name] installing 'scoop'..."
    iwr -useb get.scoop.sh | iex

    Write-Host "[$step_name] installing base packages..."
    scoop install 7zip, git, innounp, dark, wixtoolset, lessmsi

    Write-Host "[$step_name] changing scoop core to shovel..."
    scoop config SCOOP_REPO 'https://github.com/Ash258/Scoop-Core'
    scoop update
    scoop bucket add 'Base'

    Write-Host "[$step_name] adding 'SCOOP' to environment variables..."
    $scoop_path = Join-Path -Path $env:USERPROFILE -ChildPath 'scoop'
    [Environment]::SetEnvironmentVariable('SCOOP', $scoop_path, 'User');$env:SCOOP=$scoop_path

    Write-Host "[$step_name] setting config to automatically load autocomplete module..."
    Add-Content $PROFILE "Import-Module '$(Join-Path -Path $scoop_path -ChildPath 'apps\scoop\current\supporting\completion\Scoop-Completion.psd1')' -ErrorAction SilentlyContinue"
    Import-Module $(Join-Path -Path $scoop_path -ChildPath 'apps\scoop\current\supporting\completion\Scoop-Completion.psd1') -ErrorAction SilentlyContinue

    Write-Host "[$step_name] configuring shovel command..."
    Get-ChildItem -Path (Join-Path -Path $scoop_path -ChildPath 'shims') -Filter 'scoop.*' | Copy-Item -Destination { Join-Path $_.Directory.FullName (($_.BaseName -replace 'scoop', 'shovel') + $_.Extension) }
}
