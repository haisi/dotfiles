---
title: Shell & terminal
description: zsh, starship, ghostty, and the aliases that make the terminal pleasant.
---

## zsh

`ZDOTDIR` is set to `~/.config/zsh` (from `dot_zshenv`), so the rest of zsh's config
lives there instead of scattering dotfiles across `$HOME`:

- `dot_zshrc` — the entry point
- `plugins.zsh` — a tiny dependency-free plugin manager (`_zplugin_load`) that
  `git clone --depth=1`s a plugin the first time it's needed and sources it;
  `zsh-autosuggestions`, `zsh-history-substring-search`, `zsh-vi-mode`, and
  `fast-syntax-highlighting` are loaded this way
- `prompt.zsh` / `starship.toml` — the prompt, via [starship](https://starship.rs)
- `aliases.zsh`, `bindings.zsh`, `fzf.zsh` — everyday ergonomics

A few aliases worth knowing:

```sh
ls   → eza --icons
ll   → eza -lh --icons --git
la   → eza -lah --icons --git
cat  → bat (or batcat, on Ubuntu's packaging)
grep → rg --color=auto
vim  → nvim
lf   → wraps the lf file manager so quitting `cd`s the shell into lf's last directory
```

`EDITOR`/`VISUAL` are `nvim`, and `MANPAGER` uses `bat`/`batcat` for syntax-highlighted
man pages when either is on `PATH`.

## Ghostty

The terminal is [Ghostty](https://ghostty.org). Its config pins the shell explicitly:

```
command = /usr/bin/zsh
```

Ghostty's shell auto-detection doesn't reliably pick up `/etc/passwd`'s login shell
change (`chsh -s zsh`, done by the bootstrap playbook) — it was falling back to
`/bin/bash` without this override.
