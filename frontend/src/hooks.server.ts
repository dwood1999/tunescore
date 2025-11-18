import type { Handle } from '@sveltejs/kit';

// Note: API proxying is handled by Nginx
// All /api/* requests are proxied directly to the backend by Nginx
// This hook only handles non-API requests for SvelteKit routing
export const handle: Handle = async ({ event, resolve }) => {
	return resolve(event);
};

