# Dev setup

This machine's dotfiles and dev tooling are managed by [chezmoi](https://chezmoi.io) from
`~/.local/share/chezmoi`. Files under `$HOME` that chezmoi generates (`.zshenv`,
`.config/nvim`, `.config/zsh/*`, etc.) are build artifacts — never edit them directly, edit
the source in that repo instead.

For the full edit/apply/commit workflow, naming conventions, and known gotchas, see the
`dotfiles` skill.
