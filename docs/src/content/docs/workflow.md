---
title: Editing workflow
description: The golden rule, the edit/apply/commit loop, and chezmoi's naming convention.
---

## The golden rule

Nothing under `$HOME` that chezmoi manages is ever edited directly — `.zshenv`,
`.config/nvim`, `.config/i3/config`, all of it are generated **targets**. The next
`chezmoi apply` silently overwrites hand-edits to them. The only place to make
changes is the source repo, `~/.local/share/chezmoi`.

## The loop

1. **Find the source** for a target path:
   ```sh
   chezmoi source-path ~/.config/i3/config
   ```
   or browse `chezmoi managed` for the full list.
2. **Edit** the source file in the repo.
3. **Apply**:
   ```sh
   chezmoi apply -v
   ```
   prints a diff of exactly what changed.
4. **Verify** the change actually works.
5. **Commit** inside the source repo:
   ```sh
   chezmoi git -- add <file>
   chezmoi git -- commit -m "..."
   ```

The local branch is named `master`; the remote's default branch is `main`, so a
plain `chezmoi git -- push` fails on the upstream mismatch — use
`chezmoi git -- push origin HEAD:main` instead.

## Naming convention

chezmoi encodes file attributes in the source filename itself, so the repo can hold
real dotfiles (leading `.`) as ordinary, visible-in-`ls` filenames:

| Source path | Target path |
|---|---|
| `dot_foo` | `~/.foo` |
| `private_dot_config/zsh/bar.zsh` | `~/.config/zsh/bar.zsh` (`private_` → mode `0600`) |
| `CLAUDE.md` | `~/CLAUDE.md` (no leading dot, no prefix needed → unchanged) |

Nested directories only need the prefix on the first path segment that requires it —
`private_dot_config/nvim/lua/plugins/lsp.lua` maps straight to
`~/.config/nvim/lua/plugins/lsp.lua` with no further renaming of the segments below it.

Templates (`*.tmpl`) are chezmoi's [Go templates](https://pkg.go.dev/text/template):
the `.tmpl` suffix is stripped from the target name, and the file is rendered before
being written. The i3 config, for instance, uses a template conditional to include
laptop-only keybindings — see [Laptop function keys](/features/laptop-keys/).
