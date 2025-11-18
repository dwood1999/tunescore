<script lang="ts">
	import { onMount } from 'svelte';
	import { Users, TrendingUp, Music, FileText, BarChart3, AlertCircle, Loader2, CheckCircle2 } from 'lucide-svelte';
	import Button from '$lib/components/ui/button.svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';

	let artists = $state<any[]>([]);
	let loading = $state(false);
	let comparing = $state(false);
	let error = $state<string | null>(null);
	let comparisonResult = $state<any | null>(null);

	let artist1Id = $state<number | null>(null);
	let artist2Id = $state<number | null>(null);

	onMount(async () => {
		// Load all artists
		loading = true;
		try {
			const response = await fetch('/api/v1/tracks');
			if (!response.ok) throw new Error('Failed to load tracks');
			
			const tracks = await response.json();
			
			// Extract unique artists from tracks
			const artistMap = new Map();
			for (const track of tracks) {
				if (track.artist_id && track.artist_name) {
					if (!artistMap.has(track.artist_id)) {
						artistMap.set(track.artist_id, {
							id: track.artist_id,
							name: track.artist_name,
							trackCount: 0,
						});
					}
					artistMap.get(track.artist_id).trackCount++;
				}
			}
			
			artists = Array.from(artistMap.values()).sort((a, b) => b.trackCount - a.trackCount);
		} catch (e) {
			console.error('Failed to load artists:', e);
			error = e instanceof Error ? e.message : 'Failed to load artists';
		} finally {
			loading = false;
		}
	});

	async function handleCompare() {
		if (!artist1Id || !artist2Id) {
			error = 'Please select both artists to compare';
			return;
		}

		if (artist1Id === artist2Id) {
			error = 'Please select two different artists';
			return;
		}

		comparing = true;
		error = null;
		comparisonResult = null;

		try {
			const response = await fetch(`/api/v1/search/artists/compare/${artist1Id}/${artist2Id}`);
			
			if (!response.ok) {
				throw new Error('Comparison failed');
			}

			comparisonResult = await response.json();
		} catch (e) {
			console.error('Comparison failed:', e);
			error = e instanceof Error ? e.message : 'Failed to compare artists';
		} finally {
			comparing = false;
		}
	}

	function getSimilarityColor(score: number): string {
		if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
		if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
		if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
		if (score >= 20) return 'text-orange-600 bg-orange-50 border-orange-200';
		return 'text-red-600 bg-red-50 border-red-200';
	}

	function getMatchLabel(score: number): string {
		if (score >= 80) return 'Nearly Identical';
		if (score >= 60) return 'Very Similar';
		if (score >= 40) return 'Similar';
		if (score >= 20) return 'Somewhat Similar';
		return 'Different';
	}

	function resetComparison() {
		artist1Id = null;
		artist2Id = null;
		comparisonResult = null;
		error = null;
	}
</script>

<div class="max-w-7xl mx-auto space-y-6">
	<!-- Header -->
	<div class="text-center mb-8">
		<h1 class="text-4xl font-bold mb-3">Artist Comparison Tool</h1>
		<p class="text-lg text-muted-foreground max-w-2xl mx-auto">
			Compare two artists based on their sonic and lyrical fingerprints.
			Perfect for A&R intelligence and talent discovery.
		</p>
	</div>

	<!-- Artist Selection -->
	{#if !comparisonResult}
		<Card class="p-6">
			<h2 class="text-xl font-semibold mb-4">Select Artists to Compare</h2>

			{#if loading}
				<div class="flex items-center justify-center py-12">
					<Loader2 class="h-8 w-8 animate-spin text-primary" />
				</div>
			{:else if artists.length < 2}
				<div class="text-center py-12">
					<AlertCircle class="h-12 w-12 text-yellow-600 mx-auto mb-4" />
					<p class="text-muted-foreground mb-4">
						You need at least 2 artists with analyzed tracks to use this feature.
					</p>
					<Button href="/upload">Upload More Tracks</Button>
				</div>
			{:else}
				<div class="grid md:grid-cols-2 gap-6">
					<!-- Artist 1 -->
					<div>
						<label for="artist1" class="block text-sm font-medium mb-2">Artist 1</label>
						<select
							id="artist1"
							bind:value={artist1Id}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
						>
							<option value={null}>Select first artist...</option>
							{#each artists as artist}
								<option value={artist.id}>
									{artist.name} ({artist.trackCount} track{artist.trackCount !== 1 ? 's' : ''})
								</option>
							{/each}
						</select>
					</div>

					<!-- Artist 2 -->
					<div>
						<label for="artist2" class="block text-sm font-medium mb-2">Artist 2</label>
						<select
							id="artist2"
							bind:value={artist2Id}
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
						>
							<option value={null}>Select second artist...</option>
							{#each artists as artist}
								<option value={artist.id} disabled={artist.id === artist1Id}>
									{artist.name} ({artist.trackCount} track{artist.trackCount !== 1 ? 's' : ''})
								</option>
							{/each}
						</select>
					</div>
				</div>

				<div class="mt-6">
					<Button
						onclick={handleCompare}
						disabled={!artist1Id || !artist2Id || comparing}
						class="w-full"
						size="lg"
					>
						{#if comparing}
							<Loader2 class="w-4 h-4 mr-2 animate-spin" />
							Analyzing...
						{:else}
							<Users class="w-4 h-4 mr-2" />
							Compare Artists
						{/if}
					</Button>
				</div>

				{#if error}
					<div class="mt-4 p-4 border border-red-200 bg-red-50 rounded-lg flex items-center gap-3 text-red-800">
						<AlertCircle class="h-5 w-5" />
						<p>{error}</p>
					</div>
				{/if}
			{/if}
		</Card>
	{/if}

	<!-- Comparison Results -->
	{#if comparisonResult}
		<div class="space-y-6">
			<!-- Header with Artist Names -->
			<Card class="p-6">
				<div class="flex items-center justify-between mb-6">
					<h2 class="text-2xl font-bold">Comparison Results</h2>
					<Button variant="outline" onclick={resetComparison}>
						Compare Different Artists
					</Button>
				</div>

				<div class="grid md:grid-cols-2 gap-6 mb-6">
					<div class="text-center p-4 border rounded-lg">
						<Music class="h-8 w-8 text-primary mx-auto mb-2" />
						<h3 class="font-semibold text-lg">{comparisonResult.artist1?.name || 'Artist 1'}</h3>
						<p class="text-sm text-muted-foreground">{comparisonResult.artist1?.track_count || 0} tracks analyzed</p>
					</div>
					<div class="text-center p-4 border rounded-lg">
						<Music class="h-8 w-8 text-primary mx-auto mb-2" />
						<h3 class="font-semibold text-lg">{comparisonResult.artist2?.name || 'Artist 2'}</h3>
						<p class="text-sm text-muted-foreground">{comparisonResult.artist2?.track_count || 0} tracks analyzed</p>
					</div>
				</div>

				<!-- Overall Similarity -->
				<div class="text-center p-6 border-2 rounded-lg {getSimilarityColor(comparisonResult.overall_similarity || 0)}">
					<div class="text-5xl font-bold mb-2">
						{(comparisonResult.overall_similarity || 0).toFixed(0)}
					</div>
					<div class="text-xl font-semibold mb-1">Overall Similarity</div>
					<div class="text-sm opacity-80">
						{getMatchLabel(comparisonResult.overall_similarity || 0)}
					</div>
				</div>
			</Card>

			<!-- Detailed Breakdown -->
			<div class="grid md:grid-cols-2 gap-6">
				<!-- Sonic Similarity -->
				<Card class="p-6">
					<div class="flex items-center gap-2 mb-4">
						<Music class="h-5 w-5 text-primary" />
						<h3 class="text-xl font-semibold">Sonic Similarity</h3>
					</div>
					<div class="text-center mb-6">
						<div class="text-4xl font-bold text-primary mb-2">
							{(comparisonResult.sonic_similarity || 0).toFixed(0)}
						</div>
						<div class="h-2 bg-secondary rounded-full overflow-hidden">
							<div
								class="h-full bg-primary transition-all"
								style="width: {comparisonResult.sonic_similarity || 0}%"
							></div>
						</div>
					</div>

					{#if comparisonResult.sonic_breakdown}
						<div class="space-y-3 text-sm">
							{#each Object.entries(comparisonResult.sonic_breakdown) as [key, value]}
								<div>
									<div class="flex justify-between mb-1">
										<span class="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
										<span class="font-medium">{typeof value === 'number' ? value.toFixed(1) : value}</span>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</Card>

				<!-- Lyrical Similarity -->
				<Card class="p-6">
					<div class="flex items-center gap-2 mb-4">
						<FileText class="h-5 w-5 text-primary" />
						<h3 class="text-xl font-semibold">Lyrical Similarity</h3>
					</div>
					<div class="text-center mb-6">
						<div class="text-4xl font-bold text-primary mb-2">
							{(comparisonResult.lyrical_similarity || 0).toFixed(0)}
						</div>
						<div class="h-2 bg-secondary rounded-full overflow-hidden">
							<div
								class="h-full bg-primary transition-all"
								style="width: {comparisonResult.lyrical_similarity || 0}%"
							></div>
						</div>
					</div>

					{#if comparisonResult.lyrical_breakdown}
						<div class="space-y-3 text-sm">
							{#each Object.entries(comparisonResult.lyrical_breakdown) as [key, value]}
								<div>
									<div class="flex justify-between mb-1">
										<span class="text-muted-foreground capitalize">{key.replace(/_/g, ' ')}</span>
										<span class="font-medium">{typeof value === 'number' ? value.toFixed(1) : value}</span>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</Card>
			</div>

			<!-- Insights -->
			{#if comparisonResult.insights && comparisonResult.insights.length > 0}
				<Card class="p-6">
					<div class="flex items-center gap-2 mb-4">
						<CheckCircle2 class="h-5 w-5 text-green-600" />
						<h3 class="text-xl font-semibold">Insights</h3>
					</div>
					<div class="space-y-2">
						{#each comparisonResult.insights as insight}
							<p class="text-sm text-muted-foreground pl-4 border-l-2 border-primary/30">
								{insight}
							</p>
						{/each}
					</div>
				</Card>
			{/if}

			<!-- Style Match -->
			{#if comparisonResult.style_match}
				<Card class="p-6">
					<div class="flex items-center gap-2 mb-4">
						<BarChart3 class="h-5 w-5 text-primary" />
						<h3 class="text-xl font-semibold">Style Match</h3>
					</div>
					<div class="text-center">
						<Badge class="text-lg px-6 py-2">
							{comparisonResult.style_match.replace(/_/g, ' ')}
						</Badge>
					</div>
				</Card>
			{/if}
		</div>
	{/if}

	<!-- How It Works -->
	{#if !comparisonResult}
		<Card class="p-6 bg-muted/30">
			<h3 class="font-semibold mb-3">How Artist Comparison Works</h3>
			<div class="space-y-2 text-sm text-muted-foreground">
				<p>• <strong>Sonic Fingerprint:</strong> Compares tempo, key, energy, instrumentation, and audio features</p>
				<p>• <strong>Lyrical Analysis:</strong> Examines themes, sentiment, complexity, and writing style</p>
				<p>• <strong>Aggregate Scoring:</strong> Analyzes all tracks from each artist to create a profile</p>
				<p>• <strong>A&R Intelligence:</strong> Perfect for discovering talent, planning collaborations, or market positioning</p>
			</div>
		</Card>
	{/if}
</div>

