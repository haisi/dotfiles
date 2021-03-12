sudo xcode-select --install

defaults write com.apple.finder AppleShowAllFiles YES

# Brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew tap homebrew/cask

# Apps via Brew
brew install git
brew cask install itsycal # Calendar inside status bar
brew cask install spectacle # Move and resize windows with ease
brew cask install menumeters # Show CPU, network, RAM, etc. in status bar
brew install --cask alfred # Spotlight on steroids
brew install tree # Terminal: Shows tree structure of directory
brew install cloc # Terminal: lines of code counter
brew install --cask dash # API documentation browser
brew install --cask numi # Calculator on steroids
brew cask install spotify
brew cask install google-chrome

## Terminal
brew cask install iterm2 # Terminal
brew install zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
chsh -s $(which zsh)

## Dev tools
brew cask install visual-studio-code

brew cask install android-studio
brew install --cask android-file-transfer
brew install --cask android-platform-tools
brew install scrcpy #

brew cask install google-cloud-sdk
brew cask install docker

brew install node
brew install nvm
# export NVM_DIR="$HOME/.nvm"
#  [ -s "/usr/local/opt/nvm/nvm.sh" ] && . "/usr/local/opt/nvm/nvm.sh"  # This loads nvm
#  [ -s "/usr/local/opt/nvm/etc/bash_completion.d/nvm" ] && . "/usr/local/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion

brew tap lokalise/cli-2
brew install lokalise2

## Java
brew tap adoptopenjdk/openjdk
brew cask install adoptopenjdk/openjdk/adoptopenjdk8

# Through app store
echo "Install the following tools manually through the app store"
echo -e '\e]8;;https://apps.apple.com/us/app/gestimer/id990588172\aGestimer\e]8;;\a'
echo -e '\e]8;;https://apps.apple.com/us/app/gestimer/id1355679052\aDropover\e]8;;\a' #

## Through chrome web store
echo -e '\e]8;;https://chrome.google.com/webstore/detail/surfingkeys/gfbliohnnapiefjpjlpjnehglfpaknnc\aSurfingkeys\e]8;;\a'
echo -e '\e]8;;https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm?hl=en\auBlockOrigin\e]8;;\a'
echo -e '\e]8;;https://chrome.google.com/webstore/detail/json-formatter/bcjindcccaagfpapjjmafapmmgkkhgoa?hl=en\aJSONFormatter\e]8;;\a'
