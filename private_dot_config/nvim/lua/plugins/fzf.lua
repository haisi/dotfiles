return {
  {
    -- shells out to the system `fzf` binary, so it stays consistent with
    -- the fzf-driven shell/lf workflow already set up outside nvim
    "ibhagwan/fzf-lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    opts = {
      winopts = { height = 0.85, width = 0.85 },
    },
    keys = {
      { "<leader><space>", "<cmd>FzfLua files<CR>", desc = "Find files" },
      { "<leader>ff", "<cmd>FzfLua files<CR>", desc = "Find files" },
      { "<leader>fg", "<cmd>FzfLua live_grep<CR>", desc = "Live grep" },
      { "<leader>fb", "<cmd>FzfLua buffers<CR>", desc = "Buffers" },
      { "<leader>fh", "<cmd>FzfLua helptags<CR>", desc = "Help tags" },
      { "<leader>fr", "<cmd>FzfLua oldfiles<CR>", desc = "Recent files" },
      { "<leader>fw", "<cmd>FzfLua grep_cword<CR>", desc = "Word under cursor" },
      { "<leader>fc", "<cmd>FzfLua colorschemes<CR>", desc = "Colorschemes" },
      { "<leader>/", "<cmd>FzfLua lgrep_curbuf<CR>", desc = "Search buffer" },
    },
  },
}
