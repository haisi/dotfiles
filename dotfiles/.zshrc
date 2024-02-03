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
export PATH="/usr/local/opt/openjdk/bin:$PATH"
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"
export PATH="/Applications/IntelliJ IDEA CE.app/Contents/MacOS:$PATH"

export NVM_DIR="$HOME/.nvm"
  [ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"  # This loads nvm
  [ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion

# History in cache directory:
HISTFILE=~/.cache/zsh/history
HISTSIZE=10000
SAVEHIST=10000
HIST_STAMPS="yyyy-mm-dd"

# See all options: https://zsh.sourceforge.io/Doc/Release/Options.html

setopt append_history # Append history to the history file (no overwriting)
setopt extended_history # Save each command’s beginning timestamp (in seconds since the epoch) and the duration (in seconds) to the history file
setopt inc_append_history # Immediately append to the history file, not just when a term is killed
setopt share_history # Share history across terminals

# options
unsetopt menu_complete

setopt always_to_end # If a completion is performed with the cursor within a word, and a full completion is inserted, the cursor is moved to the end of the word.
setopt auto_menu # Automatically use menu completion after the second consecutive request
setopt complete_in_word
setopt hist_expire_dups_first
setopt hist_ignore_all_dups  # don't record dupes in history
setopt hist_ignore_dups
setopt hist_ignore_space # Remove command lines from the history list when the first character on the line is a space
setopt hist_reduce_blanks # Remove superfluous blanks from each command line being added to the history list.
setopt hist_verify # Whenever the user enters a line with history expansion, don’t execute the line directly; instead, perform history expansion and reload the line into the editing buffer.
setopt prompt_subst

autoload -U compinit
compinit

source ~/my-mac/zsh-plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source ~/my-mac/zsh-plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
source ~/my-mac/zsh-plugins/zsh-history-substring-search/zsh-history-substring-search.zsh

export LANG=en_US.UTF-8

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

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
