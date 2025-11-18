import type { PageServerLoad } from './$types';

// Use different URLs based on environment
const BACKEND_URL = process.env.NODE_ENV === 'production' 
	? 'http://127.0.0.1:8001/api/v1'  // Production: use 127.0.0.1 for local backend
	: 'http://localhost:8001/api/v1';  // Development

async function fetchFromBackend<T>(endpoint: string): Promise<T> {
	try {
		const url = `${BACKEND_URL}${endpoint}`;
		console.log(`[Industry Pulse SSR] Fetching: ${url}`);
		
		const response = await fetch(url, {
			headers: {
				'Content-Type': 'application/json',
			},
		});
		
		if (!response.ok) {
			console.error(`[Industry Pulse SSR] API error: ${response.status} for ${endpoint}`);
			throw new Error(`HTTP ${response.status}`);
		}
		
		const data = await response.json();
		console.log(`[Industry Pulse SSR] Success: ${endpoint} returned ${Array.isArray(data) ? data.length : 1} items`);
		return data;
	} catch (error) {
		console.error(`[Industry Pulse SSR] Fetch failed for ${endpoint}:`, error);
		throw error;
	}
}

export const load: PageServerLoad = async () => {
	try {
		console.log('Loading Industry Pulse data from backend...');
		
		const [digest, charts, news, releases] = await Promise.all([
			fetchFromBackend('/industry-pulse/digest').catch((e) => {
				console.log('Digest fetch failed:', e.message);
				return null;
			}),
			fetchFromBackend<any[]>('/industry-pulse/charts?limit=10').catch((e) => {
				console.log('Charts fetch failed:', e.message);
				return [];
			}),
			fetchFromBackend<any[]>('/industry-pulse/news?days=7&limit=10').catch((e) => {
				console.log('News fetch failed:', e.message);
				return [];
			}),
			fetchFromBackend<any[]>('/industry-pulse/releases?days=7&limit=12').catch((e) => {
				console.log('Releases fetch failed:', e.message);
				return [];
			})
		]);

		console.log('Industry Pulse data loaded:', { 
			digestExists: !!digest, 
			chartsCount: charts.length, 
			newsCount: news.length, 
			releasesCount: releases.length 
		});

		return {
			digest,
			charts,
			news,
			releases
		};
	} catch (error) {
		console.error('Failed to load Industry Pulse data:', error);
		return {
			digest: null,
			charts: [],
			news: [],
			releases: []
		};
	}
};

