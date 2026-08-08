// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://selman.li',
	base: '/dotfiles',
	integrations: [
		starlight({
			title: 'haisi/dotfiles',
			description: 'A chezmoi + Ansible managed dotfiles setup: i3, zsh, Neovim, and reproducible machine bootstrap.',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/haisi/dotfiles' }],
			editLink: {
				baseUrl: 'https://github.com/haisi/dotfiles/edit/main/docs/',
			},
			lastUpdated: true,
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{
					label: 'Start here',
					items: [
						{ label: 'Overview', slug: 'overview' },
						{ label: 'New machine setup', slug: 'getting-started' },
						{ label: 'Editing workflow', slug: 'workflow' },
					],
				},
				{
					label: 'Features',
					items: [
						{ label: 'Shell & terminal', slug: 'features/shell' },
						{ label: 'i3 window manager', slug: 'features/i3' },
						{ label: 'Neovim', slug: 'features/neovim' },
						{ label: 'Laptop function keys', slug: 'features/laptop-keys' },
						{ label: 'Toolchain management', slug: 'features/toolchain' },
					],
				},
				{
					label: 'Reference',
					items: [{ label: 'Repo layout & naming', slug: 'reference/layout' }],
				},
			],
		}),
	],
});
