$user="joao"

# Setup PowerShell permissions
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install scoop
irm get.scoop.sh | iex

# Install winget
scoop install winget

# Install WSL from the Windows Store
winget install wsl

# Install ArchWSL distro
scoop bucket add extras
scoop install archwsl

# Setups ArchWSL distro
arch run "sh ./initial-setup-archwsl.sh $user"
arch config --default-user $user

# Setups WinRM for Ansible communication
irm "https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1" | iex


