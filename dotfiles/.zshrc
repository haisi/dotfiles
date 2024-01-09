# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# If you come from bash you might have to change your $PATH.
source ~/my-mac/zsh-plugins/powerlevel10k/powerlevel10k.zsh-theme
export PATH=$(brew --prefix)/opt/findutils/libexec/gnubin:$HOME/bin:/usr/local/bin:$PATH:/usr/local/bin/kubectl
export PATH="/usr/local/anaconda3/bin:$PATH"

# History in cache directory:
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.cache/zsh/history

# options
unsetopt menu_complete
unsetopt flowcontrol

setopt prompt_subst
setopt always_to_end
setopt append_history
setopt auto_menu
setopt complete_in_word
setopt extended_history
setopt hist_expire_dups_first
setopt hist_ignore_dups
setopt hist_ignore_space
setopt hist_verify
setopt inc_append_history
setopt share_history
setopt HIST_IGNORE_ALL_DUPS  # don't record dupes in history
setopt HIST_REDUCE_BLANKS

autoload -U compinit
compinit


source ~/my-mac/zsh-plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/my-mac/zsh-plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/my-mac/zsh-plugins/zsh-history-substring-search/zsh-history-substring-search.zsh

# Uncomment the following line to display red dots whilst waiting for completion.
# Caution: this setting can cause issues with multiline prompts (zsh 5.7.1 and newer seem to work)
# See https://github.com/ohmyzsh/ohmyzsh/issues/5765
COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
HIST_STAMPS="yyyy-mm-dd"

# https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md
#antigen bundle zsh-users/zsh-autosuggestions

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git git-extra
    colored-man
    kubectl kubectx
    sudo # when you try a command which requires sudo (fails), when you arrow back, it adds sudo (or hit escape key twice)
    # https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/web-search
    web-search
    dirhistory
    # acs: show all aliases by group
    # acs -h/--help: print help mesage
    # acs <keyword>: filter aliases by <keyword> and highlight
    # acs -g <group>/--group <group>: show only aliases for group <group>. Multiple uses of the flag show all groups
    # acs --groups: show only group names
    aliases
    )

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Load the shell dotfiles, and then some:
# * ~/.path can be used to extend `$PATH`.
# * ~/.extra can be used for other settings you don’t want to commit.
for file in ~/.{path,bash_prompt,exports,aliases,functions,extra}; do
	[ -r "$file" ] && [ -f "$file" ] && source "$file";
done;
unset file;

source ~/.exports
source ~/.aliases
source ~/.functions
source ~/.path
# alias ohmyzsh="mate ~/.oh-my-zsh"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
