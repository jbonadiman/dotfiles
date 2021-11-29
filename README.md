# Dotfiles

### Fixes:
- [Windows] Scoop already added bucket message is not a warning
- [Windows] Scoop env var doesnt get updated in the same execution. Is it because the subshell is still running? Should I run a separate one?
- [Windows] Scoops install script could not be run because of the policy, but there was no error
- [Windows] Accept winget first run policy agreement
- [Windows] winget install not working with checkcall
- [Windows] Dependency error installing winget through MSIX. Installing manually is just fine

### TODO:

- [Windows] Should set powershell Execution-Policy that allow script execution for new fresh installations
- [Windows] Shellcheck should be installed as a scoop base package
- [Windows] Use wsl --status to check if wsl is installed
- [Windows] Find a way to backup StartAllBack cfg
- [Windows] Install imagemagick through scoop
- [Windows] Symlink powershell profile
- [Windows] Install Stremio.Stremio through winget
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
- [All] Upgrade also upgrade pip and/or python
- [All] Use Yaml files for recipes 
- [Windows] Intercept Scoop messages and use them with the log library
- [Windows] Install Battle.net, Origin
- [WSL] exa is really slow right now with the -l option. I'm using -1 option for now, but I should change it back in exa version 0.11.0 (this improvement is marked for that version miletone)

### Annotations
