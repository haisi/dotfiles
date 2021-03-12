# My Dotfiles

Automating my MacBook setup in case my Mac dies again 😤. Inspired by [this Medium article](https://medium.com/@webprolific/getting-started-with-dotfiles-43c3602fd789).

## Installing the Dotfiles

Let’s assume you have the relevant dotfiles together in `~/.dotfiles`.
You can create a symlink from here to the directory where they are expected (usually your home directory, `~`):

```bash
ln -sv “~/.dotfiles/runcom/.bash_profile” ~
ln -sv “~/.dotfiles/runcom/.inputrc” ~
ln -sv “~/.dotfiles/git/.gitconfig” ~
```