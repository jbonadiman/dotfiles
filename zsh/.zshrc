export DOTFILES=$HOME/dotfiles

# change zsh options
HISTFILE=~/.zsh_history
HISTSIZE=10000
HISTCONTROL=ignoreboth
SAVEHIST=10000
setopt INC_APPEND_HISTORY_TIME

# customize prompt
PROMPT='
%(?.%F{green}√.%F{red}?%?)%f %B%F{240}%1~%f%b %L $'\n'%(!.#.λ) '

autoload -Uz vcs_info
precmd_vcs_info() { vcs_info }
precmd_functions+=( precmd_vcs_info )
setopt prompt_subst
RPROMPT=\$vcs_info_msg_0_
zstyle ':vcs_info:git:*' formats '%F{240}(%b) %f'
zstyle ':vcs_info:*' enable git
RPROMPT="$RPROMPT%F{248}%D{%H:%M:%S}%f"

source $DOTFILES/zsh/utils
source $DOTFILES/zsh/aliases
source $DOTFILES/zsh/keybinds

# . /opt/asdf-vm/asdf.sh

if [[ ! -f ~/.secrets ]]
then
  touch ~/.secrets
fi

source ~/.secrets

# activate syntax highlighting
source ~/.zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
