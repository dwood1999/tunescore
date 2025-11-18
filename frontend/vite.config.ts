import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	preview: {
		host: '0.0.0.0',
		port: 5128,
		allowedHosts: ['music.quilty.app', 'localhost', '127.0.0.1'],
		proxy: {
			'/api': {
				target: 'http://localhost:8001',
				changeOrigin: true,
			},
		},
	},
	server: {
		host: '0.0.0.0',
		port: 5128,
		allowedHosts: ['music.quilty.app', 'localhost', '127.0.0.1'],
		proxy: {
			'/api': {
				target: 'http://localhost:8001',
				changeOrigin: true,
			},
		},
	},
});

