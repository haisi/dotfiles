return {
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    opts = {
      flavour = "mocha",
      transparent_background = false,
      integrations = {
        blink_cmp = true,
        gitsigns = true,
        treesitter = true,
        which_key = true,
        native_lsp = { enabled = true },
        mason = true,
        fzf = true,
        indent_blankline = { enabled = true },
        snacks = true,
      },
    },
    config = function(_, opts)
      require("catppuccin").setup(opts)
      vim.cmd.colorscheme("catppuccin")
    end,
  },
}
