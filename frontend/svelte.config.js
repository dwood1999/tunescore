import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	compilerOptions: {
		runes: true,
	},

	vitePlugin: {
		inspector: false,
		dynamicCompileOptions({ filename }) {
			// Disable runes mode for lucide-svelte components
			if (filename?.includes('node_modules/lucide-svelte')) {
				return { runes: false };
			}
		},
	},

	kit: {
		adapter: adapter({
			out: 'build',
		}),
		paths: {
			base: '',
		},
		// Configure CSRF for remote development
		csrf: {
			trustedOrigins:
				process.env.NODE_ENV === 'production'
					? ['https://music.quilty.app']
					: ['http://localhost:5128', 'https://music.quilty.app'],
		},
	},
};

export default config;

