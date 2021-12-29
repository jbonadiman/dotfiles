# keybinds

# set variables

export NULLCMD=bat
export GOROOT=/usr/local/go
export GOPATH=~/.go

export IRCNAME=*
export IRCPORT=6667
export IRCNICK=un_known
export IRCUSER=un_known

# change zsh options
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt INC_APPEND_HISTORY_TIME

# create aliases
alias ls='exa -laFh --icons'
alias exa='exa -laFh --icons'
alias man='batman'
alias trail='<<<${(F)path}'
alias cat='bat'
alias python='python3'
alias clip='/mnt/c/Windows/System32/clip.exe'
alias rm='trash-put'

# customize prompt
PROMPT='
%(?.%F{green}√.%F{red}?%?)%f %B%F{240}%1~%f%b %L %(!.#.>) '

autoload -Uz vcs_info
precmd_vcs_info() { vcs_info }
precmd_functions+=( precmd_vcs_info )
setopt prompt_subst
RPROMPT=\$vcs_info_msg_0_
zstyle ':vcs_info:git:*' formats '%F{240}(%b) %f'
zstyle ':vcs_info:*' enable git
RPROMPT="$RPROMPT%F{248}%*%f"

# add locations to $PATH
# removes duplicates in the path variable
typeset -U path

path=(
  $path
  "$HOME/.local/bin",
  "$GOROOT/bin",
  "$GOPATH/bin"
)

# functions
function mkcd() {
  mkdir -p "$@" && cd "$_";
}

# zsh plugins

# init procedures
if exists docker && [[ -a ~/.docker_service.zsh ]]; then
    source ~/.docker_service.zsh
fi

export N_PREFIX="$HOME/n"; [[ :$PATH: == *":$N_PREFIX/bin:"* ]] || PATH+=":$N_PREFIX/bin"  # Added by n-install (see http://git.io/n-install-repo).

# activate syntax highlighting
source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh

export PATH="$HOME/.poetry/bin:$PATH"
