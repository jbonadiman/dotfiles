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
    c
    Write-Host "installing 'Ubisoft Connect'..."
    winget install --id 'Ubisoft.Connect' --accept-package-agreements

    Write-Host "installing 'WhatsApp'..."
    winget install --id 'WhatsApp.WhatsApp' --accept-package-agreements
}

function Install-DevPackages {
    Install-ShovelPkg 'gitkraken' 
    
    Add-Bucket 'extras'
    Install-ShovelPkg 'jetbrains-toolbox'

    Write-Host "installing 'DBeaver'..."
    winget install --id 'dbeaver.dbeaver'

    Write-Host "installing 'WSL'..."
    wsl --install

    Write-Host "installing 'Ubuntu 20.04 distro'..."
    winget install --id 'Canonical.Ubuntu.2004' --accept-package-agreements

    Copy-Item -Path "./cfg/terminal.settings.json" -Destination [IO.Path]::Combine($env:LOCALAPPDATA, "Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json")
}

function Install-Fonts {
  $fontsTempDir=[IO.Path]::Combine($env:TEMP, "fonts")
  $fonts=(New-Object -ComObject Shell.Application).Namespace(0x14)

  # Caskaydia Code NerdFont
  Invoke-WebRequest "https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/CascadiaCode/Regular/complete/Caskaydia%20Cove%20Regular%20Nerd%20Font%20Complete%20Windows%20Compatible.otf" -OutFile ([IO.Path]::Combine($fontsTempDir, "Caskaydia_NerdFont.otf"))

  Get-ChildItem -Path ([IO.Path]::Combine($fontsTempDir, "*")) -Include "*.ttf", "*.otf" | %{ $fonts.CopyHere($_.fullname) }
}

function Install-EssentialPackages {
    Install-Fonts

    Add-Bucket 'extras'
    
    Install-ShovelPkg 'aria2'
    Install-ShovelPkg 'advancedrenamer'
    Install-ShovelPkg 'authy'
    Install-ShovelPkg 'treesize-free'
    Install-ShovelPkg 'vlc'
    Install-ShovelPkg 'bitwarden'
}
