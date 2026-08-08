vim.g.mapleader = " "
vim.g.maplocalleader = " "

local opt = vim.opt

opt.number = true
opt.relativenumber = true
opt.mouse = "a"
opt.termguicolors = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.scrolloff = 8
opt.wrap = false

opt.expandtab = true
opt.shiftwidth = 2
opt.tabstop = 2
opt.smartindent = true

opt.ignorecase = true
opt.smartcase = true

opt.splitright = true
opt.splitbelow = true

opt.undofile = true
opt.swapfile = false
opt.updatetime = 250
opt.timeoutlen = 300

opt.clipboard = "unnamedplus"
opt.list = true
opt.listchars = { tab = "» ", trail = "·", nbsp = "␣" }

opt.completeopt = { "menu", "menuone", "noselect" }
opt.pumheight = 10
opt.confirm = true
