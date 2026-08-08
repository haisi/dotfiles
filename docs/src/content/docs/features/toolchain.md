---
title: Toolchain management
description: mise for per-language runtimes, and how zoxide/herdr are installed without an apt package.
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

## Third-party apt repositories

Packages not in Ubuntu's default repos — [eza](https://github.com/eza-community/eza),
the [GitHub CLI](https://cli.github.com), [Docker](https://docs.docker.com/engine/install/ubuntu/),
and mise itself — each get their own GPG key under `/etc/apt/keyrings/` and their own
`apt_repository` entry, following the same key-then-repo-then-install shape every
time. `dpkg --print-architecture` and `lsb_release -cs` are resolved once and reused
across all of them.
