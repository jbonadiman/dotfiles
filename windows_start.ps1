$step_name="Shovel Installation"

$addedBuckets=@{
    extra=$false;
    java=$false;
    'nerd-fonts'=$false;
}

function Add-Bucket ($bucketName) {
    if (-NOT $addedBuckets[$bucketName]) {
        Write-Host "adding '$bucketName' bucket to shovel..."
        shovel bucket add $bucketName
        $addedBuckets[$bucketName] = $true
    }
}

function Install-ShovelPkg ($package) {
    Write-Host "installing '$package'..."
    shovel install $package
}

function Install-Browser {
    Invoke-WebRequest -OutFile "FirefoxInstaller.exe" -Uri https://download.mozilla.org/?product=firefox-stub
    ./FirefoxInstaller.exe
}

function Install-PersonalPackages {
    winget install netflix --accept-package-agreements
}

function Install-DevPackages {
    Install-ShovelPkg "gitkraken"
    
    Add-Bucket "extra"
    Install-ShovelPkg "jetbrains-toolbox"

    Add-Bucket "java"
    Install-ShovelPkg "openjdk"
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

function Install-BasePackages {
    Install-ShovelPkg "aria2"
}
