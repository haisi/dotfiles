---
title: Neovim
description: A lazy.nvim-based Neovim setup, one file per concern.
---

Config lives at `~/.config/nvim`, built on [lazy.nvim](https://github.com/folke/lazy.nvim),
split one file per concern:

```
lua/config/     options, keymaps, autocmds, the lazy.nvim bootstrap
lua/plugins/    one file per plugin group
```

| File | Plugins |
|---|---|
| `colorscheme.lua` | [catppuccin/nvim](https://github.com/catppuccin/nvim) |
| `completion.lua` | [saghen/blink.cmp](https://github.com/saghen/blink.cmp) |
| `editor.lua` | [folke/flash.nvim](https://github.com/folke/flash.nvim), [folke/which-key.nvim](https://github.com/folke/which-key.nvim), [kylechui/nvim-surround](https://github.com/kylechui/nvim-surround), [stevearc/oil.nvim](https://github.com/stevearc/oil.nvim), [windwp/nvim-autopairs](https://github.com/windwp/nvim-autopairs) |
| `formatting.lua` | [stevearc/conform.nvim](https://github.com/stevearc/conform.nvim) |
| `fzf.lua` | [ibhagwan/fzf-lua](https://github.com/ibhagwan/fzf-lua) |
| `git.lua` | [lewis6991/gitsigns.nvim](https://github.com/lewis6991/gitsigns.nvim) |
| `lsp.lua` | [neovim/nvim-lspconfig](https://github.com/neovim/nvim-lspconfig), [mason.nvim](https://github.com/williamboman/mason.nvim) + [mason-lspconfig](https://github.com/williamboman/mason-lspconfig.nvim) + [mason-tool-installer](https://github.com/WhoIsSethDaniel/mason-tool-installer.nvim) |
| `treesitter.lua` | [nvim-treesitter/nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter) |
| `ui.lua` | [folke/snacks.nvim](https://github.com/folke/snacks.nvim), [folke/todo-comments.nvim](https://github.com/folke/todo-comments.nvim), [nvim-lualine/lualine.nvim](https://github.com/nvim-lualine/lualine.nvim) |

## The treesitter branch pin

`nvim-treesitter` is pinned to its `master` branch on purpose. Its `main` branch is a
full, incompatible rewrite — it dropped the `configs.setup()` API and requires
Neovim 0.12+ (nightly). This setup targets stable Neovim 0.11.x, and upstream's own
README says `master`, not `main`, is the branch to use there. Keep the pin unless
Neovim itself gets upgraded to 0.12+.

## Sanity-checking changes headlessly

```sh
nvim --headless <file> -c "qa"
```

and inspect stderr / the exit code for Lua tracebacks. Lazy-loaded plugins
(`event = {...}`) don't expose their commands until that event fires, which a
headless one-shot invocation usually skips — force-load a plugin to run one of its
commands anyway:

```sh
nvim --headless -c "lua require('lazy').load({plugins={'<plugin-name>'}})" -c "<Command>" -c "qa"
```

For treesitter parsers specifically:

```sh
nvim --headless -c "lua require('lazy').load({plugins={'nvim-treesitter'}})" -c "TSInstallSync! <langs>" -c "qa"
```

Installing/updating treesitter parsers needs a C compiler (`build-essential`) plus
`git`/`curl`. LSP servers via `mason-lspconfig` mostly need Node (via
[mise](/features/toolchain/)) unless they ship a standalone prebuilt binary —
`lua_ls`, `marksman`, `stylua`, and `shfmt` are standalone; `bashls` and `jsonls`
need Node.
