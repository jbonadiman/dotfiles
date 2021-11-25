
function Install-Browser {
    Invoke-WebRequest -OutFile "FirefoxInstaller.exe" -Uri https://download.mozilla.org/?product=firefox-stub
    ./FirefoxInstaller.exe
}

function Install-PersonalPackages {
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
    Write-Host "installing 'DBeaver'..."
    winget install --id 'dbeaver.dbeaver'

    Write-Host "installing 'WSL'..."
    wsl --install

    Write-Host "installing 'Ubuntu 20.04 distro'..."
    winget install --id 'Canonical.Ubuntu.2004' --accept-package-agreements

    Copy-Item -Path "./cfg/terminal.settings.json" -Destination [IO.Path]::Combine($env:LOCALAPPDATA, "Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json")
}