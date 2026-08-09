---
title: Toolchain management
description: mise for per-language runtimes, how tools get installed without an apt package (or via snap/third-party repos), and the herdr command palette.
---

## mise

[mise](https://mise.jdx.dev) manages per-language runtime versions as global
defaults — currently JDK 25 and Node LTS — installed via its own apt repository
rather than `nodejs`/`npm` directly, so upgrading a language version later is just
`mise use --global <tool>@<version>` instead of fighting apt.

`mise activate zsh` is already wired into `.zshrc`, so anything mise installs is on
`PATH` in any new shell — including terminals spawned from inside Neovim.

The bootstrap playbook installs versions idempotently: it checks
`mise ls <tool>` first and only runs `mise use --global` when the target version
isn't already there, so re-running the playbook doesn't reinstall or churn
versions that are already correct.

## Tools with no apt package

[zoxide](https://github.com/ajeetdsouza/zoxide) and
[herdr](https://herdr.dev) have no Ubuntu package, so they install to
`~/.local/bin` via their own curl-pipe installer scripts. Each is guarded by an
`ansible.builtin.stat` check on the installed binary, so re-running the playbook
is a no-op once it's there — the same idempotency guarantee as the apt-installed
tools, just implemented by hand since there's no package manager to lean on.

## herdr command palette

`prefix+shift+a` opens a `herdr` popup running `herdr-command-palette.py`
(`private_dot_config/herdr/config.toml`, as a `[[keys.command]]` entry). It mirrors
the i3/rofi palette: resolves herdr's built-in `[keys.*]` bindings plus any
`config.toml` overrides and `[[keys.command]]` entries, and offers them via `fzf`.

Dispatch is deliberately *not* `herdr pane send-keys` for built-in actions —
that writes literal bytes into a pane's PTY (input for whatever program is running
there), not herdr's own global keybinding dispatch, so it can't actually trigger
client-side actions like toggling the sidebar. Verified live: sending it to a pane
running `cat` just echoed the raw keys back instead of doing anything. Actions with
a real server-side equivalent (tab/workspace switching, closing a workspace, creating
a worktree) go through herdr's own CLI (`tab list`/`workspace list` + `focus`,
`worktree create`, ...) instead. Actions with no server-side equivalent at all (help,
settings, detach, copy mode, ...) stay in the palette as a dimmed, searchable
keybinding reference — selecting one just reports the key to press yourself.

## Third-party apt repositories

Packages not in Ubuntu's default repos — [eza](https://github.com/eza-community/eza),
the [GitHub CLI](https://cli.github.com), [Docker](https://docs.docker.com/engine/install/ubuntu/),
[Spotify](https://www.spotify.com), and mise itself — each get their own GPG key under
`/etc/apt/keyrings/` and their own `apt_repository` entry, following the same
key-then-repo-then-install shape every time. `dpkg --print-architecture` and
`lsb_release -cs` are resolved once and reused across all of them.

## Snap packages

IntelliJ IDEA Ultimate isn't in Ubuntu's default apt repos and, unlike the tools
above, doesn't publish its own apt repo either — it installs via
`community.general.snap` with `classic: true` (classic confinement, since it needs
broader filesystem access than a strictly sandboxed snap allows).
