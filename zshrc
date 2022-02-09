# set variables

export NULLCMD=bat

export IRCNAME=*
export IRCPORT=6667
export IRCNICK=un_known
export IRCUSER=un_known

export N_PREFIX="$HOME/n"; [[ :$PATH: == *":$N_PREFIX/bin:"* ]] || PATH+=":$N_PREFIX/bin"  # Added by n-install (see http://git.io/n-install-repo).

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

# TODO: Add WSL check
alias clip='/mnt/c/Windows/System32/clip.exe'
alias rm='trash-put'
alias vim='nvim'

# TODO: Add WSL check
alias pbcopy='clip.exe'
alias pbpaste="pwsh.exe -command 'Get-Clipboard' | tr -d '\r' | head -n -1"

alias gc='git commit -m'
alias gb='git checkout -b'
alias ga='git add'
alias gd='git diff'
alias gs='git status'
alias gl='git log'
alias gam='git commit --amend'
alias gp='git push'

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
  "$HOME/.local/bin"
  "$GOROOT/bin"
  "$GOPATH/bin"
  "$HOME/.poetry/bin"
)

# functions
function mkcd() {
  mkdir -p "$@" && cd "$_";
}

# zsh plugins

# init procedures

# activate syntax highlighting
source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh

