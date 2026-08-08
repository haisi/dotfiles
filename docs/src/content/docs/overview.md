---
title: Overview
description: How chezmoi and Ansible split responsibility for this machine's setup.
---

This repo manages an entire Ubuntu machine's configuration from a single source of
truth. It splits the work across two tools that are good at different things:

- **[chezmoi](https://chezmoi.io)** owns everything under `$HOME` — dotfiles,
  `.config/`, shell setup. It templates files where a config needs to differ
  by hardware, and it's the thing you run day to day (`chezmoi apply`).
- **[Ansible](https://www.ansible.com)** owns the system: apt packages, third-party
  repositories, group membership, udev rules — anything that needs root or lives
  outside `$HOME`. It runs as a single local playbook, `dot_bootstrap/setup.yml`.

## How they connect

chezmoi triggers Ansible for you. A `run_onchange_` script is content-hashed against
`setup.yml`: every time that file's content changes, the next `chezmoi apply` reruns
the playbook automatically. Editing `setup.yml` and applying is the entire workflow —
there's no separate "now go run Ansible" step to remember.

```
dot_bootstrap/setup.yml            ← desired system state (packages, repos, users)
run_onchange_bootstrap.sh.tmpl     ← hash-gated: reruns the playbook iff setup.yml changed
```

## Why split it this way

Putting system-level changes in Ansible rather than shell scripts sprinkled through
chezmoi templates keeps installs **idempotent and legible**: every task states the
desired end state ("this package is present", "this user is in this group") instead
of an imperative recipe, and re-running the whole playbook is always safe because
each task checks before it acts.

Everything is designed to survive being applied more than once, and to be a safe
no-op the second time.

See [New machine setup](/getting-started/) to bring up a fresh box, or
[Editing workflow](/workflow/) for the day-to-day edit/apply/commit loop.
