<script lang="ts">
	import { onMount } from 'svelte';
	import { Search, Music, TrendingUp, AlertCircle, Loader2 } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';

	let query = $state('');
	let results = $state<any[]>([]);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let searched = $state(false);
	let minSimilarity = $state(0.3);
	let limit = $state(20);

	// Example queries for inspiration
	const exampleQueries = [
		'sad love songs',
		'upbeat party music',
		'emotional ballads',
		'high energy electronic',
		'acoustic folk vibes',
		'dark moody rap',
	];

	async function handleSearch(e?: Event) {
		if (e) e.preventDefault();

		if (!query.trim() || query.trim().length < 3) {
			error = 'Please enter at least 3 characters';
			return;
		}

		loading = true;
		error = null;
		searched = true;

		try {
			const response = await fetch(
				`/api/v1/search/query?q=${encodeURIComponent(query)}&limit=${limit}&min_similarity=${minSimilarity}`
			);

			if (!response.ok) {
				throw new Error('Search failed');
			}

			results = await response.json();
		} catch (e) {
			console.error('Search failed:', e);
			error = e instanceof Error ? e.message : 'Failed to search tracks';
			results = [];
		} finally {
			loading = false;
		}
	}

	function setExampleQuery(example: string) {
		query = example;
		handleSearch();
	}

	function getSimilarityColor(score: number): string {
		if (score >= 0.7) return 'text-green-600';
		if (score >= 0.5) return 'text-blue-600';
		if (score >= 0.3) return 'text-yellow-600';
		return 'text-gray-600';
	}

	function getSimilarityLabel(score: number): string {
		if (score >= 0.7) return 'Excellent Match';
		if (score >= 0.5) return 'Good Match';
		if (score >= 0.3) return 'Fair Match';
		return 'Weak Match';
	}
</script>

<div class="max-w-6xl mx-auto space-y-6">
	<!-- Header -->
	<div class="text-center mb-8">
		<h1 class="text-4xl font-bold mb-3">Semantic Track Search</h1>
		<p class="text-lg text-muted-foreground max-w-2xl mx-auto">
			Search for tracks using natural language. Describe the mood, energy, theme, or vibe you're
			looking for.
		</p>
	</div>

	<!-- Search Form -->
	<Card class="p-6">
		<form onsubmit={(e) => { e.preventDefault(); handleSearch(); }} class="space-y-4">
			<div class="relative">
				<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
					<Search class="h-5 w-5 text-muted-foreground" />
				</div>
				<input
					type="text"
					bind:value={query}
					placeholder='Try "sad love songs" or "upbeat party music"...'
					class="block w-full pl-12 pr-4 py-3 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
					disabled={loading}
				/>
			</div>

			<!-- Advanced Options -->
			<details class="border rounded-lg p-4 bg-muted/30">
				<summary class="cursor-pointer font-medium text-sm text-muted-foreground">
					Advanced Options
				</summary>
				<div class="mt-4 grid md:grid-cols-2 gap-4">
					<div>
						<label for="minSimilarity" class="block text-sm font-medium mb-2">
							Minimum Similarity: {(minSimilarity * 100).toFixed(0)}%
						</label>
						<input
							id="minSimilarity"
							type="range"
							bind:value={minSimilarity}
							min="0"
							max="1"
							step="0.05"
							class="w-full"
						/>
						<p class="text-xs text-muted-foreground mt-1">
							Higher values = stricter matches
						</p>
					</div>
					<div>
						<label for="limit" class="block text-sm font-medium mb-2">
							Results Limit: {limit}
						</label>
						<input
							id="limit"
							type="range"
							bind:value={limit}
							min="5"
							max="50"
							step="5"
							class="w-full"
						/>
						<p class="text-xs text-muted-foreground mt-1">
							Max number of results to return
						</p>
					</div>
				</div>
			</details>

			<div class="flex flex-col sm:flex-row gap-3">
				<Button type="submit" class="flex-1" size="lg" disabled={loading}>
					{#if loading}
						<Loader2 class="w-4 h-4 mr-2 animate-spin" />
						Searching...
					{:else}
						<Search class="w-4 h-4 mr-2" />
						Search Tracks
					{/if}
				</Button>
			</div>
		</form>

		<!-- Example Queries -->
		{#if !searched}
			<div class="mt-6 pt-6 border-t">
				<h3 class="text-sm font-medium mb-3 text-muted-foreground">Try these examples:</h3>
				<div class="flex flex-wrap gap-2">
					{#each exampleQueries as example}
						<button
							onclick={() => setExampleQuery(example)}
							class="px-3 py-1.5 text-sm border border-gray-300 rounded-full hover:bg-primary hover:text-primary-foreground hover:border-primary transition-colors"
							disabled={loading}
						>
							{example}
						</button>
					{/each}
				</div>
			</div>
		{/if}
	</Card>

	<!-- Error Message -->
	{#if error}
		<Card class="p-6 border-red-200 bg-red-50">
			<div class="flex items-center gap-3 text-red-800">
				<AlertCircle class="h-5 w-5" />
				<p>{error}</p>
			</div>
		</Card>
	{/if}

	<!-- Loading State -->
	{#if loading}
		<Card class="p-12 text-center">
			<Loader2 class="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
			<p class="text-muted-foreground">Searching through your track catalog...</p>
		</Card>
	{/if}

	<!-- Results -->
	{#if searched && !loading && results.length === 0 && !error}
		<Card class="p-12 text-center">
			<div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 mb-4">
				<AlertCircle class="h-8 w-8 text-yellow-600" />
			</div>
			<h3 class="text-xl font-semibold mb-2">No tracks found</h3>
			<p class="text-muted-foreground mb-4">
				Try adjusting your search query or lowering the minimum similarity threshold.
			</p>
			<Button onclick={() => (searched = false)}>Try Different Query</Button>
		</Card>
	{/if}

	{#if results.length > 0}
		<div>
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-2xl font-semibold">
					Found {results.length} track{results.length !== 1 ? 's' : ''}
				</h2>
				<p class="text-sm text-muted-foreground">Sorted by relevance</p>
			</div>

			<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each results as track}
					<Card class="p-5 hover:shadow-lg transition-shadow group">
						<a href="/tracks/{track.track_id}" class="block">
							<div class="flex items-start gap-4 mb-4">
								<div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
									<Music class="h-6 w-6 text-primary" />
								</div>
								<div class="flex-1 min-w-0">
									<h3 class="font-semibold mb-1 truncate group-hover:text-primary transition-colors">
										{track.title || 'Untitled Track'}
									</h3>
									<p class="text-sm text-muted-foreground truncate">
										{track.artist_name || 'Unknown Artist'}
									</p>
								</div>
							</div>

							<!-- Similarity Score -->
							{#if track.similarity_score !== undefined}
								<div class="space-y-2">
									<div class="flex items-center justify-between text-sm">
										<span class="font-medium {getSimilarityColor(track.similarity_score)}">
											{getSimilarityLabel(track.similarity_score)}
										</span>
										<span class="text-muted-foreground">
											{(track.similarity_score * 100).toFixed(0)}% match
										</span>
									</div>
									<div class="h-2 bg-secondary rounded-full overflow-hidden">
										<div
											class="h-full bg-primary transition-all"
											style="width: {track.similarity_score * 100}%"
										></div>
									</div>
								</div>
							{/if}

							<!-- Metadata -->
							<div class="flex flex-wrap gap-2 mt-3">
								{#if track.genre}
									<Badge variant="secondary" class="text-xs">{track.genre}</Badge>
								{/if}
								{#if track.tunescore}
									<Badge variant="outline" class="text-xs">
										<TrendingUp class="w-3 h-3 mr-1" />
										TuneScore: {track.tunescore}
									</Badge>
								{/if}
							</div>

							<div class="mt-4 pt-4 border-t">
								<span class="text-sm text-muted-foreground group-hover:text-primary transition-colors">
									View details →
								</span>
							</div>
						</a>
					</Card>
				{/each}
			</div>
		</div>
	{/if}

	<!-- How It Works -->
	{#if !searched}
		<Card class="p-6 bg-muted/30">
			<h3 class="font-semibold mb-3">How Semantic Search Works</h3>
			<div class="space-y-2 text-sm text-muted-foreground">
				<p>
					• <strong>Natural Language:</strong> Describe what you're looking for in plain English
				</p>
				<p>
					• <strong>AI-Powered:</strong> Uses embeddings to understand meaning, not just keywords
				</p>
				<p>
					• <strong>Multi-Factor:</strong> Considers lyrics, themes, mood, and sonic characteristics
				</p>
				<p>
					• <strong>Similarity Scoring:</strong> Results ranked by how well they match your query
				</p>
			</div>
		</Card>
	{/if}
</div>

