# Dotfiles

### TODO:

- [Windows] Install required fonts
- [Windows] Install script
- [Windows] Fix CRLF in vim/editors
- [Windows] Set variable with Windows username in WSL
- [Windows] Make sure US-International is the only keyboard
- [Windows] Install StartAllBack (winget install --id "StartIsBack.StartAllBack")
- [Windows] Install PowerToys
- [WSL] Fix bug and guarantee that Windows exe will be executed successfully
- [WSL] exa is really slow right now with the -l option. I'm using -1 option for now, but I should change it back in exa version 0.11.0 (this improvement is marked for that version miletone)
- [WSL] Install shfmt so that bat-extras can be minified
- [WSL] Find a way to use the trash, so I don't use rm directly
- [WSL] Syntax highlighting in commands
- [WSL] Autocomplete in commands
- [Windows] Install EdgeDeflector, Battle.net, Origin
- [All] Add separation installations tags (personal, essential, dev...)
- [All] Add command line options that defines what tags should be installed and if upgrades must be run

### Annotations

Docker bug:
    ```/mnt/c/Windows/System32/wsl.exe -d $DOCKER_DISTRO sh -c "nohup sudo -b dockerd < /dev/null > $DOCKER_DIR/dockerd.log 2>&1"
    Causando erro:
    <3>init: (107) ERROR: UtilAcceptVsock:244: accept4 failed 110```
