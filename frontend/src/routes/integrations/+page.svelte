<script lang="ts">
	import { onMount } from 'svelte';
	import { Music2, Youtube, Search, TrendingUp, ExternalLink, CheckCircle, AlertCircle, Loader2 } from 'lucide-svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';

	let spotifySearchQuery = $state('');
	let spotifySearchResults = $state<any[]>([]);
	let spotifySearching = $state(false);
	let spotifySearchType = $state<'track' | 'artist'>('track');

	let youtubeSearchQuery = $state('');
	let youtubeSearchResults = $state<any[]>([]);
	let youtubeSearching = $state(false);

	let trendingMusic = $state<any[]>([]);
	let loadingTrending = $state(false);

	let activeTab = $state<'spotify' | 'youtube'>('spotify');

	async function searchSpotify() {
		if (!spotifySearchQuery.trim()) return;

		spotifySearching = true;
		try {
			const endpoint = spotifySearchType === 'track' 
				? `/api/v1/integrations/spotify/search/track?q=${encodeURIComponent(spotifySearchQuery)}&limit=20`
				: `/api/v1/integrations/spotify/search/artist?q=${encodeURIComponent(spotifySearchQuery)}&limit=20`;

			const response = await fetch(endpoint);
			if (!response.ok) throw new Error('Spotify search failed');

			spotifySearchResults = await response.json();
		} catch (e) {
			console.error('Spotify search failed:', e);
			spotifySearchResults = [];
		} finally {
			spotifySearching = false;
		}
	}

	async function searchYouTube() {
		if (!youtubeSearchQuery.trim()) return;

		youtubeSearching = true;
		try {
			const response = await fetch(
				`/api/v1/integrations/youtube/search/video?q=${encodeURIComponent(youtubeSearchQuery)}&limit=20`
			);
			if (!response.ok) throw new Error('YouTube search failed');

			youtubeSearchResults = await response.json();
		} catch (e) {
			console.error('YouTube search failed:', e);
			youtubeSearchResults = [];
		} finally {
			youtubeSearching = false;
		}
	}

	async function loadTrendingMusic() {
		loadingTrending = true;
		try {
			const response = await fetch('/api/v1/integrations/youtube/trending/music?limit=20');
			if (!response.ok) throw new Error('Failed to load trending music');

			trendingMusic = await response.json();
		} catch (e) {
			console.error('Failed to load trending music:', e);
			trendingMusic = [];
		} finally {
			loadingTrending = false;
		}
	}

	onMount(() => {
		loadTrendingMusic();
	});

	function formatNumber(num: number): string {
		if (num >= 1000000) {
			return (num / 1000000).toFixed(1) + 'M';
		} else if (num >= 1000) {
			return (num / 1000).toFixed(1) + 'K';
		}
		return num.toString();
	}
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<!-- Header -->
	<div class="text-center mb-8">
		<h1 class="text-4xl font-bold mb-3">Integrations Hub</h1>
		<p class="text-lg text-muted-foreground max-w-2xl mx-auto">
			Connect external data sources to enrich your music intelligence.
			Search Spotify and YouTube for market data and performance insights.
		</p>
	</div>

	<!-- Tab Navigation -->
	<div class="flex gap-2 border-b">
		<button
			onclick={() => (activeTab = 'spotify')}
			class="px-6 py-3 font-medium border-b-2 transition-colors {activeTab === 'spotify'
				? 'border-green-600 text-green-600'
				: 'border-transparent text-muted-foreground hover:text-foreground'}"
		>
			<div class="flex items-center gap-2">
				<Music2 class="h-4 w-4" />
				Spotify
			</div>
		</button>
		<button
			onclick={() => (activeTab = 'youtube')}
			class="px-6 py-3 font-medium border-b-2 transition-colors {activeTab === 'youtube'
				? 'border-red-600 text-red-600'
				: 'border-transparent text-muted-foreground hover:text-foreground'}"
		>
			<div class="flex items-center gap-2">
				<Youtube class="h-4 w-4" />
				YouTube
			</div>
		</button>
	</div>

	<!-- Spotify Tab -->
	{#if activeTab === 'spotify'}
		<div class="space-y-6">
			<!-- Search Form -->
			<Card class="p-6">
				<h2 class="text-xl font-semibold mb-4">Search Spotify</h2>
				<div class="space-y-4">
					<div class="flex gap-2">
						<button
							onclick={() => (spotifySearchType = 'track')}
							class="px-4 py-2 rounded-lg border {spotifySearchType === 'track'
								? 'bg-green-600 text-white border-green-600'
								: 'bg-background border-gray-300'}"
						>
							Tracks
						</button>
						<button
							onclick={() => (spotifySearchType = 'artist')}
							class="px-4 py-2 rounded-lg border {spotifySearchType === 'artist'
								? 'bg-green-600 text-white border-green-600'
								: 'bg-background border-gray-300'}"
						>
							Artists
						</button>
					</div>

					<form onsubmit={(e) => { e.preventDefault(); searchSpotify(); }} class="flex gap-2">
						<div class="relative flex-1">
							<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
							<input
								type="text"
								bind:value={spotifySearchQuery}
								placeholder="Search Spotify {spotifySearchType}s..."
								class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-600"
								disabled={spotifySearching}
							/>
						</div>
						<Button type="submit" disabled={spotifySearching} class="bg-green-600 hover:bg-green-700">
							{#if spotifySearching}
								<Loader2 class="w-4 h-4 animate-spin" />
							{:else}
								Search
							{/if}
						</Button>
					</form>
				</div>

				<!-- Results -->
				{#if spotifySearchResults.length > 0}
					<div class="mt-6 space-y-3">
						<h3 class="font-semibold">Found {spotifySearchResults.length} {spotifySearchType}s</h3>
						<div class="grid gap-3 max-h-96 overflow-y-auto">
							{#each spotifySearchResults as result}
								<div class="p-4 border rounded-lg hover:bg-secondary/50 transition-colors">
									<div class="flex items-start justify-between gap-4">
										<div class="flex-1">
											<h4 class="font-semibold mb-1">{result.name}</h4>
											{#if spotifySearchType === 'track' && result.artists}
												<p class="text-sm text-muted-foreground mb-2">
													by {result.artists.map((a: any) => a.name).join(', ')}
												</p>
											{/if}
											{#if result.popularity !== undefined}
												<Badge variant="secondary" class="text-xs">
													Popularity: {result.popularity}/100
												</Badge>
											{/if}
										</div>
										{#if result.external_urls?.spotify}
											<a
												href={result.external_urls.spotify}
												target="_blank"
												rel="noopener noreferrer"
												class="text-green-600 hover:text-green-700"
											>
												<ExternalLink class="h-4 w-4" />
											</a>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</Card>

			<!-- Spotify Features -->
			<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
				<Card class="p-5">
					<div class="flex items-center gap-3 mb-3">
						<div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
							<CheckCircle class="h-5 w-5 text-green-600" />
						</div>
						<h3 class="font-semibold">Track Data</h3>
					</div>
					<p class="text-sm text-muted-foreground">
						Access detailed track metadata and audio features from Spotify's catalog.
					</p>
				</Card>

				<Card class="p-5">
					<div class="flex items-center gap-3 mb-3">
						<div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
							<TrendingUp class="h-5 w-5 text-green-600" />
						</div>
						<h3 class="font-semibold">Artist Stats</h3>
					</div>
					<p class="text-sm text-muted-foreground">
						Analyze artist popularity, follower counts, and related artists.
					</p>
				</Card>

				<Card class="p-5">
					<div class="flex items-center gap-3 mb-3">
						<div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
							<Music2 class="h-5 w-5 text-green-600" />
						</div>
						<h3 class="font-semibold">Audio Features</h3>
					</div>
					<p class="text-sm text-muted-foreground">
						Get sonic analysis including tempo, key, energy, and danceability.
					</p>
				</Card>
			</div>
		</div>
	{/if}

	<!-- YouTube Tab -->
	{#if activeTab === 'youtube'}
		<div class="space-y-6">
			<!-- Search Form -->
			<Card class="p-6">
				<h2 class="text-xl font-semibold mb-4">Search YouTube Music</h2>
				<form onsubmit={(e) => { e.preventDefault(); searchYouTube(); }} class="flex gap-2">
					<div class="relative flex-1">
						<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
						<input
							type="text"
							bind:value={youtubeSearchQuery}
							placeholder="Search YouTube videos..."
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-600"
							disabled={youtubeSearching}
						/>
					</div>
					<Button type="submit" disabled={youtubeSearching} class="bg-red-600 hover:bg-red-700">
						{#if youtubeSearching}
							<Loader2 class="w-4 h-4 animate-spin" />
						{:else}
							Search
						{/if}
					</Button>
				</form>

				<!-- Results -->
				{#if youtubeSearchResults.length > 0}
					<div class="mt-6 space-y-3">
						<h3 class="font-semibold">Found {youtubeSearchResults.length} videos</h3>
						<div class="grid gap-3 max-h-96 overflow-y-auto">
							{#each youtubeSearchResults as video}
								<div class="p-4 border rounded-lg hover:bg-secondary/50 transition-colors">
									<div class="flex items-start justify-between gap-4">
										<div class="flex-1">
											<h4 class="font-semibold mb-1">{video.title}</h4>
											{#if video.channelTitle}
												<p class="text-sm text-muted-foreground mb-2">{video.channelTitle}</p>
											{/if}
											<div class="flex flex-wrap gap-2 text-xs">
												{#if video.viewCount}
													<Badge variant="secondary">
														{formatNumber(video.viewCount)} views
													</Badge>
												{/if}
												{#if video.likeCount}
													<Badge variant="secondary">
														{formatNumber(video.likeCount)} likes
													</Badge>
												{/if}
											</div>
										</div>
										{#if video.videoId}
											<a
												href={`https://www.youtube.com/watch?v=${video.videoId}`}
												target="_blank"
												rel="noopener noreferrer"
												class="text-red-600 hover:text-red-700"
											>
												<ExternalLink class="h-4 w-4" />
											</a>
										{/if}
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</Card>

			<!-- Trending Music -->
			<Card class="p-6">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-xl font-semibold">Trending Music</h2>
					<Button variant="outline" onclick={loadTrendingMusic} disabled={loadingTrending} size="sm">
						{#if loadingTrending}
							<Loader2 class="w-4 h-4 animate-spin" />
						{:else}
							Refresh
						{/if}
					</Button>
				</div>

				{#if loadingTrending}
					<div class="flex items-center justify-center py-12">
						<Loader2 class="h-8 w-8 animate-spin text-primary" />
					</div>
				{:else if trendingMusic.length > 0}
					<div class="grid md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
						{#each trendingMusic as video}
							<div class="p-4 border rounded-lg hover:bg-secondary/50 transition-colors">
								<div class="flex items-start justify-between gap-4">
									<div class="flex-1">
										<h4 class="font-semibold mb-1 text-sm">{video.title}</h4>
										{#if video.channelTitle}
											<p class="text-xs text-muted-foreground mb-2">{video.channelTitle}</p>
										{/if}
										<div class="flex flex-wrap gap-1 text-xs">
											{#if video.viewCount}
												<Badge variant="secondary" class="text-xs">
													{formatNumber(video.viewCount)} views
												</Badge>
											{/if}
										</div>
									</div>
									{#if video.videoId}
										<a
											href={`https://www.youtube.com/watch?v=${video.videoId}`}
											target="_blank"
											rel="noopener noreferrer"
											class="text-red-600 hover:text-red-700"
										>
											<ExternalLink class="h-4 w-4" />
										</a>
									{/if}
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="text-center py-12">
						<AlertCircle class="h-12 w-12 text-yellow-600 mx-auto mb-4" />
						<p class="text-muted-foreground">No trending music available</p>
					</div>
				{/if}
			</Card>

			<!-- YouTube Features -->
			<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
				<Card class="p-5">
					<div class="flex items-center gap-3 mb-3">
						<div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
							<TrendingUp class="h-5 w-5 text-red-600" />
						</div>
						<h3 class="font-semibold">Video Stats</h3>
					</div>
					<p class="text-sm text-muted-foreground">
						Track views, likes, comments, and engagement metrics for music videos.
					</p>
				</Card>

				<Card class="p-5">
					<div class="flex items-center gap-3 mb-3">
						<div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
							<Youtube class="h-5 w-5 text-red-600" />
						</div>
						<h3 class="font-semibold">Channel Data</h3>
					</div>
					<p class="text-sm text-muted-foreground">
						Analyze channel subscribers, total views, and content performance.
					</p>
				</Card>

				<Card class="p-5">
					<div class="flex items-center gap-3 mb-3">
						<div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
							<CheckCircle class="h-5 w-5 text-red-600" />
						</div>
						<h3 class="font-semibold">Trending Data</h3>
					</div>
					<p class="text-sm text-muted-foreground">
						Stay updated with trending music videos and viral content.
					</p>
				</Card>
			</div>
		</div>
	{/if}

	<!-- Info Box -->
	<Card class="p-6 bg-muted/30">
		<h3 class="font-semibold mb-3">About Integrations</h3>
		<div class="space-y-2 text-sm text-muted-foreground">
			<p>
				• <strong>Market Intelligence:</strong> Access real-time data from Spotify and YouTube to inform your strategies
			</p>
			<p>
				• <strong>Competitive Analysis:</strong> Compare your tracks against industry benchmarks and trending content
			</p>
			<p>
				• <strong>Discovery Tools:</strong> Find similar artists, related tracks, and emerging trends
			</p>
			<p>
				• <strong>Data Enrichment:</strong> Supplement your TuneScore analysis with external platform metrics
			</p>
		</div>
	</Card>
</div>

