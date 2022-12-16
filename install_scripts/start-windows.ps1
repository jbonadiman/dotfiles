Write-Output "setting up powershell permissions..."
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Output "installing scoop..."
iex "& {$(irm get.scoop.sh)} -RunAsAdmin"

Write-Output "installing 'git' using scoop..."
scoop install git

Write-Output "installing 'sudo' using scoop..."
scoop install sudo

Write-Output "adding 'extras' bucket to scoop..."
scoop bucket add extras

Write-Output "installing 'vcredist' using scoop..."
scoop install vcredist-aio

Write-Output "installing 'winget' using scoop..."
scoop install winget

Write-Output "installing 'wsl' using winget..."
sudo winget install --accept-source-agreements --accept-package-agreements --id 9P9TQF7MRM4R

# TODO: WSL not enabled
Write-Output "installing 'archwsl' using scoop..."
scoop install archwsl

Write-Output "setting up archwsl..."
arch run "sh ./initial-setup-archwsl.sh $Args"

Write-Output "defining archwsl default user to $Args"
arch config --default-user $Args

Write-Output "setting up winrm for ansible communication..."
irm "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1" | iex


