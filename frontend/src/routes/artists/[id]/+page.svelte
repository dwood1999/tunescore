<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { 
		TrendingUp, Users, Music, ListMusic, ArrowLeft, 
		Sparkles, BarChart3, Calendar, ExternalLink, Award,
		Target, Zap, TrendingDown
	} from 'lucide-svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';

	let artist = $state<any>(null);
	let metrics = $state<any>(null);
	let trajectory = $state<any>(null);
	let playlists = $state<any[]>([]);
	let breakoutScore = $state<any>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedPlatform = $state('spotify');
	let timeRange = $state(90);

	onMount(async () => {
		const artistId = parseInt($page.params.id);
		if (!artistId) {
			error = 'Invalid artist ID';
			loading = false;
			return;
		}

		try {
			// Load artist data
			const [metricsRes, playlistsRes, breakoutRes] = await Promise.allSettled([
				fetch(`/api/v1/artist-intelligence/artists/${artistId}/metrics?days=${timeRange}&platform=${selectedPlatform}`),
				fetch(`/api/v1/artist-intelligence/artists/${artistId}/playlists`),
				fetch(`/api/v1/artist-intelligence/artists/${artistId}/breakout-score`)
			]);

			if (metricsRes.status === 'fulfilled' && metricsRes.value.ok) {
				metrics = await metricsRes.value.json();
			}

			if (playlistsRes.status === 'fulfilled' && playlistsRes.value.ok) {
				playlists = await playlistsRes.value.json();
			}

			if (breakoutRes.status === 'fulfilled' && breakoutRes.value.ok) {
				breakoutScore = await breakoutRes.value.json();
			}

			// Mock artist data for now (replace with actual API call)
			artist = {
				id: artistId,
				name: metrics?.name || 'Artist',
				spotify_id: metrics?.spotify_id,
				genres: metrics?.genres || []
			};

		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load artist data';
		} finally {
			loading = false;
		}
	});

	function formatNumber(num: number): string {
		if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
		if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
		return num.toString();
	}

	function getVelocityColor(velocity: number): string {
		if (velocity > 0.1) return 'text-green-600';
		if (velocity > 0) return 'text-blue-600';
		if (velocity < -0.1) return 'text-red-600';
		return 'text-gray-600';
	}

	function getBreakoutColor(score: number): string {
		if (score >= 80) return 'from-green-500 to-emerald-500';
		if (score >= 60) return 'from-blue-500 to-cyan-500';
		if (score >= 40) return 'from-yellow-500 to-orange-500';
		return 'from-orange-500 to-red-500';
	}
</script>

<div class="container mx-auto px-4 py-8 max-w-7xl">
	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
			<p class="mt-4 text-muted-foreground">Loading artist intelligence...</p>
		</div>
	{:else if error}
		<div class="text-center py-12">
			<p class="text-destructive mb-4">{error}</p>
			<a href="/dashboard" class="text-primary underline">← Back to Dashboard</a>
		</div>
	{:else if artist}
		<!-- Header -->
		<div class="mb-8">
			<a href="/dashboard" class="text-primary hover:underline mb-4 inline-flex items-center gap-2">
				<ArrowLeft class="h-4 w-4" />
				Back to Dashboard
			</a>
			
			<div class="flex items-start justify-between gap-6 mt-4">
				<div class="flex-1">
					<h1 class="text-4xl font-bold mb-2">{artist.name}</h1>
					<div class="flex flex-wrap gap-2 mb-4">
						{#each artist.genres as genre}
							<Badge variant="secondary">{genre}</Badge>
						{/each}
					</div>
					{#if artist.spotify_id}
						<a
							href={`https://open.spotify.com/artist/${artist.spotify_id}`}
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex items-center gap-2 text-sm text-green-600 hover:text-green-700"
						>
							<ExternalLink class="h-4 w-4" />
							View on Spotify
						</a>
					{/if}
				</div>
			</div>
		</div>

		<!-- Breakout Score (Hero Card) -->
		{#if breakoutScore}
			<div class="bg-gradient-to-r {getBreakoutColor(breakoutScore.breakout_score)} rounded-xl p-8 mb-8 text-white shadow-xl">
				<div class="flex items-center gap-2 mb-4">
					<Zap class="h-6 w-6" />
					<h2 class="text-2xl font-bold">Breakout Score</h2>
					<Badge variant="secondary" class="ml-auto bg-white/20 text-white border-white/30">
						TuneScore Predictive
					</Badge>
				</div>
				
				<div class="grid md:grid-cols-4 gap-6">
					<div>
						<div class="text-7xl font-bold mb-2">
							{breakoutScore.breakout_score}
						</div>
						<div class="text-xl opacity-90">
							out of 100
						</div>
						<div class="text-sm opacity-75 mt-2">
							Confidence: {(breakoutScore.confidence * 100).toFixed(0)}%
						</div>
					</div>

					<div class="md:col-span-3 grid grid-cols-3 gap-4">
						{#if breakoutScore.predicted_7d_streams}
							<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
								<div class="text-sm opacity-75 mb-1">Predicted 7-day streams</div>
								<div class="text-3xl font-bold">
									{formatNumber(breakoutScore.predicted_7d_streams)}
								</div>
							</div>
						{/if}
						{#if breakoutScore.predicted_14d_streams}
							<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
								<div class="text-sm opacity-75 mb-1">Predicted 14-day streams</div>
								<div class="text-3xl font-bold">
									{formatNumber(breakoutScore.predicted_14d_streams)}
								</div>
							</div>
						{/if}
						{#if breakoutScore.predicted_follower_growth}
							<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
								<div class="text-sm opacity-75 mb-1">Follower growth</div>
								<div class="text-3xl font-bold">
									+{formatNumber(breakoutScore.predicted_follower_growth)}
								</div>
							</div>
						{/if}
					</div>
				</div>

				<!-- Factors -->
				{#if breakoutScore.factors}
					<div class="mt-6 pt-6 border-t border-white/20">
						<div class="text-sm opacity-75 mb-3">Key Factors:</div>
						<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
							{#each Object.entries(breakoutScore.factors) as [key, value]}
								<div class="flex items-center gap-2">
									<div class="h-2 w-2 rounded-full bg-white/40"></div>
									<span class="text-sm capitalize">{key.replace(/_/g, ' ')}: {value}</span>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- Multi-Platform Metrics -->
		{#if metrics}
			<div class="mb-8">
				<h2 class="text-2xl font-semibold mb-4">Platform Metrics</h2>
				
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
					<!-- Spotify -->
					<div class="border rounded-lg p-6 bg-gradient-to-br from-green-50 to-transparent dark:from-green-950/20 hover:shadow-lg transition-shadow">
						<div class="flex items-center justify-between mb-4">
							<div class="flex items-center gap-2">
								<div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
									<Music class="h-5 w-5 text-green-600" />
								</div>
								<span class="font-semibold">Spotify</span>
							</div>
						</div>
						{#if metrics.spotify}
							<div class="space-y-3">
								<div>
									<div class="text-sm text-muted-foreground">Followers</div>
									<div class="text-2xl font-bold">
										{formatNumber(metrics.spotify.followers || 0)}
									</div>
									{#if metrics.spotify.velocity_7d}
										<div class="text-xs {getVelocityColor(metrics.spotify.velocity_7d)}">
											{metrics.spotify.velocity_7d > 0 ? '↑' : '↓'} {(Math.abs(metrics.spotify.velocity_7d) * 100).toFixed(1)}% (7d)
										</div>
									{/if}
								</div>
								{#if metrics.spotify.monthly_listeners}
									<div>
										<div class="text-sm text-muted-foreground">Monthly Listeners</div>
										<div class="text-xl font-semibold">
											{formatNumber(metrics.spotify.monthly_listeners)}
										</div>
									</div>
								{/if}
							</div>
						{:else}
							<div class="text-sm text-muted-foreground">No data available</div>
						{/if}
					</div>

					<!-- YouTube -->
					<div class="border rounded-lg p-6 bg-gradient-to-br from-red-50 to-transparent dark:from-red-950/20 hover:shadow-lg transition-shadow">
						<div class="flex items-center justify-between mb-4">
							<div class="flex items-center gap-2">
								<div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
									<Music class="h-5 w-5 text-red-600" />
								</div>
								<span class="font-semibold">YouTube</span>
							</div>
						</div>
						{#if metrics.youtube}
							<div class="space-y-3">
								<div>
									<div class="text-sm text-muted-foreground">Subscribers</div>
									<div class="text-2xl font-bold">
										{formatNumber(metrics.youtube.subscribers || 0)}
									</div>
									{#if metrics.youtube.velocity_7d}
										<div class="text-xs {getVelocityColor(metrics.youtube.velocity_7d)}">
											{metrics.youtube.velocity_7d > 0 ? '↑' : '↓'} {(Math.abs(metrics.youtube.velocity_7d) * 100).toFixed(1)}% (7d)
										</div>
									{/if}
								</div>
								{#if metrics.youtube.total_views}
									<div>
										<div class="text-sm text-muted-foreground">Total Views</div>
										<div class="text-xl font-semibold">
											{formatNumber(metrics.youtube.total_views)}
										</div>
									</div>
								{/if}
							</div>
						{:else}
							<div class="text-sm text-muted-foreground">Not connected</div>
						{/if}
					</div>

					<!-- Instagram -->
					<div class="border rounded-lg p-6 bg-gradient-to-br from-pink-50 to-transparent dark:from-pink-950/20 hover:shadow-lg transition-shadow">
						<div class="flex items-center justify-between mb-4">
							<div class="flex items-center gap-2">
								<div class="w-10 h-10 rounded-full bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center">
									<Users class="h-5 w-5 text-pink-600" />
								</div>
								<span class="font-semibold">Instagram</span>
							</div>
						</div>
						{#if metrics.instagram}
							<div class="space-y-3">
								<div>
									<div class="text-sm text-muted-foreground">Followers</div>
									<div class="text-2xl font-bold">
										{formatNumber(metrics.instagram.followers || 0)}
									</div>
									{#if metrics.instagram.velocity_7d}
										<div class="text-xs {getVelocityColor(metrics.instagram.velocity_7d)}">
											{metrics.instagram.velocity_7d > 0 ? '↑' : '↓'} {(Math.abs(metrics.instagram.velocity_7d) * 100).toFixed(1)}% (7d)
										</div>
									{/if}
								</div>
							</div>
						{:else}
							<div class="text-sm text-muted-foreground">Not connected</div>
						{/if}
					</div>

					<!-- TikTok -->
					<div class="border rounded-lg p-6 bg-gradient-to-br from-purple-50 to-transparent dark:from-purple-950/20 hover:shadow-lg transition-shadow">
						<div class="flex items-center justify-between mb-4">
							<div class="flex items-center gap-2">
								<div class="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
									<Music class="h-5 w-5 text-purple-600" />
								</div>
								<span class="font-semibold">TikTok</span>
							</div>
						</div>
						{#if metrics.tiktok}
							<div class="space-y-3">
								<div>
									<div class="text-sm text-muted-foreground">Followers</div>
									<div class="text-2xl font-bold">
										{formatNumber(metrics.tiktok.followers || 0)}
									</div>
									{#if metrics.tiktok.velocity_7d}
										<div class="text-xs {getVelocityColor(metrics.tiktok.velocity_7d)}">
											{metrics.tiktok.velocity_7d > 0 ? '↑' : '↓'} {(Math.abs(metrics.tiktok.velocity_7d) * 100).toFixed(1)}% (7d)
										</div>
									{/if}
								</div>
							</div>
						{:else}
							<div class="text-sm text-muted-foreground">Not connected</div>
						{/if}
					</div>
				</div>
			</div>
		{/if}

		<!-- Growth Trajectory Chart -->
		{#if trajectory}
			<div class="border rounded-lg p-6 mb-8 bg-white dark:bg-gray-900">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center gap-2">
						<TrendingUp class="h-5 w-5 text-primary" />
						<h2 class="text-xl font-semibold">Growth Trajectory</h2>
					</div>
					<div class="flex gap-2">
						<Button
							variant={timeRange === 30 ? 'default' : 'outline'}
							size="sm"
							onclick={() => { timeRange = 30; }}
						>
							30d
						</Button>
						<Button
							variant={timeRange === 90 ? 'default' : 'outline'}
							size="sm"
							onclick={() => { timeRange = 90; }}
						>
							90d
						</Button>
					</div>
				</div>
				
				<div class="h-64 bg-secondary/20 rounded-lg p-4 flex items-center justify-center">
					<div class="text-muted-foreground">
						<BarChart3 class="h-12 w-12 mx-auto mb-2 opacity-50" />
						<p class="text-sm">Chart.js visualization will render here</p>
						<p class="text-xs mt-1">Showing {timeRange}-day follower growth trend</p>
					</div>
				</div>
			</div>
		{/if}

		<!-- Playlist Appearances -->
		<div class="border rounded-lg p-6 mb-8 bg-white dark:bg-gray-900">
			<div class="flex items-center gap-2 mb-4">
				<ListMusic class="h-5 w-5 text-primary" />
				<h2 class="text-xl font-semibold">Playlist Appearances</h2>
				<Badge variant="secondary" class="ml-auto">
					{playlists.length} playlists
				</Badge>
			</div>

			{#if playlists.length > 0}
				<div class="space-y-2">
					{#each playlists as playlist}
						<div class="flex items-center justify-between p-4 hover:bg-secondary/50 rounded-lg transition-colors border">
							<div class="flex-1">
								<div class="font-semibold mb-1">{playlist.playlist_name}</div>
								<div class="flex items-center gap-4 text-sm text-muted-foreground">
									{#if playlist.playlist_type}
										<span class="inline-flex items-center gap-1">
											<Badge variant="outline" class="text-xs">
												{playlist.playlist_type}
											</Badge>
										</span>
									{/if}
									{#if playlist.playlist_followers}
										<span class="flex items-center gap-1">
											<Users class="h-3 w-3" />
											{formatNumber(playlist.playlist_followers)} followers
										</span>
									{/if}
									{#if playlist.added_at}
										<span class="flex items-center gap-1">
											<Calendar class="h-3 w-3" />
											Added {new Date(playlist.added_at).toLocaleDateString()}
										</span>
									{/if}
								</div>
							</div>
							{#if playlist.position}
								<div class="text-right">
									<div class="text-2xl font-bold text-primary">#{playlist.position}</div>
									<div class="text-xs text-muted-foreground">position</div>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<div class="text-center py-12 text-muted-foreground">
					<ListMusic class="h-16 w-16 mx-auto mb-4 opacity-30" />
					<p class="text-lg">No playlist appearances tracked yet</p>
					<p class="text-sm mt-2">
						Playlist data will appear here as tracks are added to Spotify playlists
					</p>
				</div>
			{/if}
		</div>

		<!-- Velocity Metrics -->
		{#if metrics}
			<div class="border rounded-lg p-6 bg-white dark:bg-gray-900">
				<div class="flex items-center gap-2 mb-4">
					<Target class="h-5 w-5 text-primary" />
					<h2 class="text-xl font-semibold">Growth Velocity</h2>
				</div>

				<div class="grid md:grid-cols-2 gap-4">
					<div class="p-4 bg-gradient-to-br from-blue-50 to-transparent dark:from-blue-950/20 rounded-lg border">
						<div class="text-sm text-muted-foreground mb-2">7-Day Growth Rate</div>
						<div class="flex items-center gap-3">
							{#if metrics[selectedPlatform]?.velocity_7d}
								<div class="text-4xl font-bold {getVelocityColor(metrics[selectedPlatform].velocity_7d)}">
									{metrics[selectedPlatform].velocity_7d > 0 ? '+' : ''}{(metrics[selectedPlatform].velocity_7d * 100).toFixed(1)}%
								</div>
								{#if metrics[selectedPlatform].velocity_7d > 0}
									<TrendingUp class="h-6 w-6 text-green-600" />
								{:else}
									<TrendingDown class="h-6 w-6 text-red-600" />
								{/if}
							{:else}
								<div class="text-2xl text-muted-foreground">N/A</div>
							{/if}
						</div>
					</div>

					<div class="p-4 bg-gradient-to-br from-purple-50 to-transparent dark:from-purple-950/20 rounded-lg border">
						<div class="text-sm text-muted-foreground mb-2">28-Day Growth Rate</div>
						<div class="flex items-center gap-3">
							{#if metrics[selectedPlatform]?.velocity_28d}
								<div class="text-4xl font-bold {getVelocityColor(metrics[selectedPlatform].velocity_28d)}">
									{metrics[selectedPlatform].velocity_28d > 0 ? '+' : ''}{(metrics[selectedPlatform].velocity_28d * 100).toFixed(1)}%
								</div>
								{#if metrics[selectedPlatform].velocity_28d > 0}
									<TrendingUp class="h-6 w-6 text-green-600" />
								{:else}
									<TrendingDown class="h-6 w-6 text-red-600" />
								{/if}
							{:else}
								<div class="text-2xl text-muted-foreground">N/A</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>

