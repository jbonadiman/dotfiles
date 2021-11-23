# Dotfiles

### TODO:

- [Windows] Configure Windows Terminal
- [Windows] Configure symlinks
- [Windows] Install required fonts
- [Windows] Install script
- [Windows] Fix CRLF in vim/editors
- [Windows] Set variable with Windows username in WSL
- [WSL] Fix bug and guarantee that Windows exe will be executed successfully
- [WSL] exa is really slow right now with the -l option. I'm using -1 option for now, but I should change it back in exa version 0.11.0 (this improvement is marked for that version miletone)
- [WSL] Install shfmt so that bat-extras can be minified
- [WSL] Find a way to use the trash, so I don't use rm directly
- [WSL] Syntax highlighting in commands
- [WSL] Autocomplete in commands
- [Windows] Install EdgeDeflector, Battle.net, Origin

### Annotations

Docker bug:
    ```/mnt/c/Windows/System32/wsl.exe -d $DOCKER_DISTRO sh -c "nohup sudo -b dockerd < /dev/null > $DOCKER_DIR/dockerd.log 2>&1"
    Causando erro:
    <3>init: (107) ERROR: UtilAcceptVsock:244: accept4 failed 110```
