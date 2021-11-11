$step_name=''

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
    Add-Bucket 'extras'
    
    Install-ShovelPkg 'ccleaner'
    Install-ShovelPkg 'discord'
    Install-ShovelPkg 'gimp'
    Install-ShovelPkg 'inkscape'
    Install-ShovelPkg 'qbittorrent'

    Write-Host "installing 'Netflix'..."
    winget install --id '9WZDNCRFJ3TJ' --accept-package-agreements
    
    Write-Host "installing 'Amazon Games'..."
    winget install --id 'Amazon.Games' --accept-package-agreements
    
    Write-Host "installing 'Amazon Kindle'..."
    winget install --id 'Amazon.Kindle' --accept-package-agreements
    
    Write-Host "installing 'Epic Games'..."
    winget install --id 'EpicGames.EpicGamesLauncher' --accept-package-agreements
    
    Write-Host "installing 'GOG Galaxy'..."
    winget install --id 'GOG.Galaxy' --accept-package-agreements
    
    Write-Host "installing 'Steam'..."
    winget install --id 'Valve.Steam' --accept-package-agreements
    
    Write-Host "installing 'Telegram Desktop'..."
    winget install --id 'Telegram.TelegramDesktop' --accept-package-agreements
    
    Write-Host "installing 'Ubisoft Connect'..."
    winget install --id 'Ubisoft.Connect' --accept-package-agreements

    Write-Host "installing 'WhatsApp'..."
    winget install --id 'WhatsApp.WhatsApp' --accept-package-agreements
}

function Install-DevPackages {
    $SOURCES_DIR=Join-Path -Path $env:USERPROFILE -ChildPath 'sources'

    If (!(test-path $SOURCES_DIR))
    {
      Write-Host "creating source code directory..."
      New-Item -ItemType Directory -Force -Path $SOURCES_DIR
    }

    Install-ShovelPkg 'gitkraken' 
    
    Add-Bucket 'extras'
    Install-ShovelPkg 'jetbrains-toolbox'

    Write-Host "installing 'DBeaver'..."
    winget install --id 'dbeaver.dbeaver'

    Write-Host "installing 'WSL'..."
    wsl --install

    Write-Host "installing 'Ubuntu 20.04 distro'..."
    winget install --id 'Canonical.Ubuntu.2004' --accept-package-agreements
}

function Install-Shovel {
    $step_name='Installing Shovel'
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

    # O que fazer quando diretório não existe?
    Write-Host "[$step_name] configuring shovel command..."
    Get-ChildItem -Path (Join-Path -Path $scoop_path -ChildPath 'shims') -Filter 'scoop.*' | Copy-Item -Destination { Join-Path $_.Directory.FullName (($_.BaseName -replace 'scoop', 'shovel') + $_.Extension) }
}

function Install-EssentialPackages {
    Add-Bucket 'extras'
    
    Install-ShovelPkg 'aria2'
    Install-ShovelPkg 'advancedrenamer'
    Install-ShovelPkg 'authy'
    Install-ShovelPkg 'treesize-free'
    Install-ShovelPkg 'vlc'
    Install-ShovelPkg 'bitwarden'
}
