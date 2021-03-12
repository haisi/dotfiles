# Finder: show hidden files by default
defaults write com.apple.finder AppleShowAllFiles -bool true
# Display full POSIX path as Finder window title
defaults write com.apple.finder _FXShowPosixPathInTitle -bool true
# Save screenshots to the desktop
defaults write com.apple.screencapture location -string “$HOME/Desktop”
