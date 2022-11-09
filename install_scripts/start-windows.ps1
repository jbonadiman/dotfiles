function InstallScoop() {
	Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
	irm get.scoop.sh | iex
}

function InstallWsl() {
	dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
	dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

	$wslUpdateFile = "C:/Temp/wsl_update_x64.msi"
	Invoke-WebRequest -Uri https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi -OutFile $wslUpdateFile

	msiexec /i $wslUpdateFile /qr
	wsl --set-default-version 2

	scoop bucket add extras
	scoop install archwsl
}

function SetUpWsl() {


}



InstallScoop()
InstallWsl()
