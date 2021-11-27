# Dotfiles

### TODO:

- [WSL] Install vim plugins from outside
- [WSL] Install shfmt so that bat-extras can be minified
- [WSL] Find a way to use the trash, so I don't use rm directly
- [WSL] Syntax highlighting in commands
- [WSL] Autocomplete in commands
- [WSL] Create keyboard layout routine
- [Windows] Add scoop update and cleanup as part of recipe
- [WSL] Fix N and rust checks, they are being installed everytime
- [Windows] Netflix package keeps reinstalling itself
- [Windows] Verify if WSL is installed -- A recently installed windows would be nice
- [Windows] winget search is so slow, I should find an alternative
- [All] Add separation installations tags (personal, essential, dev...)
- [All] Add command line options that defines what tags should be installed and if upgrades must be run
- [All] Use Yaml files for recipes 
- [Windows] Intercept Scoop messages and use them with the log library
- [Windows] Install Battle.net, Origin
- [WSL] exa is really slow right now with the -l option. I'm using -1 option for now, but I should change it back in exa version 0.11.0 (this improvement is marked for that version miletone)

### Annotations

Docker bug:
    ```/mnt/c/Windows/System32/wsl.exe -d $DOCKER_DISTRO sh -c "nohup sudo -b dockerd < /dev/null > $DOCKER_DIR/dockerd.log 2>&1"
    Causando erro:
    <3>init: (107) ERROR: UtilAcceptVsock:244: accept4 failed 110```
