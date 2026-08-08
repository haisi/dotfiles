---
title: Repo layout & naming
description: What lives where in the chezmoi source repo.
---

```
dot_bootstrap/setup.yml           Ansible playbook — all system-level state
run_onchange_bootstrap.sh.tmpl    Reruns the playbook iff setup.yml's content changed
dot_zshenv                        → ~/.zshenv
private_dot_config/
  i3/config.tmpl                  → ~/.config/i3/config (templated, see Laptop function keys)
  i3status/config                 → ~/.config/i3status/config
  zsh/                            → ~/.config/zsh/ (ZDOTDIR)
  nvim/                           → ~/.config/nvim/
  ghostty/                        → ~/.config/ghostty/
  lf/                             → ~/.config/lf/
  herdr/                          → ~/.config/herdr/
CLAUDE.md                         → ~/CLAUDE.md (no prefix needed, no leading dot)
docs/                             This documentation site (ignored by chezmoi, see below)
```

## Why `docs/` isn't a managed target

chezmoi's naming convention means a plain directory name with no `dot_`/`private_`
prefix maps straight through unchanged — which would otherwise make chezmoi try to
apply this entire Astro project into `~/docs`. A `.chezmoiignore` entry excludes it
from chezmoi's target state entirely; it exists in this repo purely as a normal git
subdirectory that GitHub Actions builds and deploys to GitHub Pages.

`.git` and `.github` need no such entry — chezmoi ignores any source entry whose
name begins with `.` automatically, unless it's one of chezmoi's own recognized
config files (`.chezmoiignore`, `.chezmoiroot`, `.chezmoidata`, etc.). That's what
lets this repo hold a real `.git` and `.github/workflows/` alongside chezmoi-managed
`dot_`-prefixed sources without conflict.

See [Editing workflow](/workflow/) for the full naming convention table and the
edit/apply/commit loop.
