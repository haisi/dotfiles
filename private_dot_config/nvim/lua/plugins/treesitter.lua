return {
  {
    "nvim-treesitter/nvim-treesitter",
    branch = "master", -- the "main" branch dropped the configs.setup() API used below
    build = ":TSUpdate",
    event = { "BufReadPost", "BufNewFile" },
    opts = {
      ensure_installed = {
        "bash",
        "lua",
        "vim",
        "vimdoc",
        "query",
        "markdown",
        "markdown_inline",
        "json",
        "yaml",
        "toml",
        "python",
        "javascript",
        "typescript",
        "html",
        "css",
        "regex",
        "diff",
        "gitcommit",
      },
      auto_install = true,
      highlight = { enable = true },
      indent = { enable = true },
    },
    config = function(_, opts)
      require("nvim-treesitter.configs").setup(opts)
    end,
  },
}
