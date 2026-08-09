---
title: New machine setup
description: Bringing up a fresh Ubuntu box with this dotfiles repo.
---

A fresh machine only needs three manual prerequisites — `curl`, `git`, and `chezmoi`
itself don't exist yet, so they can't be installed declaratively.

```sh
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl git
sh -c "$(curl -fsLS https://get.chezmoi.io)" -- init --apply haisi
```

That last command:

1. Clones this repo into `~/.local/share/chezmoi`
2. Applies every managed dotfile into `$HOME`
3. Runs `run_onchange_bootstrap.sh.tmpl`, which installs Ansible (if it's missing)
   and runs `dot_bootstrap/setup.yml` as root

The playbook handles everything else: zsh (and setting it as the login shell), fzf,
bat, eza, fd-find, ripgrep, starship, lf, chafa, ghostty, the GitHub CLI, Docker,
mise (with Node LTS and JDK 25), zoxide, herdr, htop, i3 + rofi, Spotify,
IntelliJ IDEA Ultimate, and the JetBrainsMono Nerd Font. You'll be prompted for your
sudo password exactly once.

:::note[Laptop hardware]
On a laptop, the same playbook also installs `brightnessctl` and wires up
media keys — see [Laptop function keys](/features/laptop-keys/). Nothing
extra to do; it detects the chassis type itself.
:::

## Changing what gets installed

Edit `dot_bootstrap/setup.yml` and run `chezmoi apply`. The content-hash-gated
`run_onchange_bootstrap.sh.tmpl` script notices the file changed and reruns the
playbook automatically — see [Overview](/overview/) for why it's wired up that way.
