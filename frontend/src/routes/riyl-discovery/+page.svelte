<script lang="ts">
	import { onMount } from 'svelte';
	import { Target, TrendingUp, Users, MapPin, Music, ExternalLink, ArrowRight } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';

	let tracks = $state<any[]>([]);
	let selectedTrackId = $state<number | null>(null);
	let riylResults = $state<any>(null);
	let loading = $state(true);
	let loadingRIYL = $state(false);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			tracks = await api.tracks.list();
			if (tracks.length > 0) {
				selectedTrackId = tracks[0].id;
				await loadRIYL(tracks[0].id);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load tracks';
		} finally {
			loading = false;
		}
	});

	async function loadRIYL(trackId: number) {
		loadingRIYL = true;
		try {
			riylResults = await api.search.riyl(trackId, 10);
		} catch (e) {
			console.error('Failed to load RIYL:', e);
			riylResults = null;
		} finally {
			loadingRIYL = false;
		}
	}

	async function handleTrackSelect(e: Event) {
		const select = e.target as HTMLSelectElement;
		const trackId = parseInt(select.value);
		selectedTrackId = trackId;
		await loadRIYL(trackId);
	}

	const selectedTrack = $derived(
		tracks.find(t => t.id === selectedTrackId)
	);

	function getSimilarityColor(score: number): string {
		if (score >= 0.8) return 'text-green-600';
		if (score >= 0.6) return 'text-blue-600';
		if (score >= 0.4) return 'text-yellow-600';
		return 'text-gray-600';
	}

	function getSimilarityBg(score: number): string {
		if (score >= 0.8) return 'bg-green-50 border-green-200';
		if (score >= 0.6) return 'bg-blue-50 border-blue-200';
		if (score >= 0.4) return 'bg-yellow-50 border-yellow-200';
		return 'bg-gray-50 border-gray-200';
	}
</script>

<div class="space-y-6">
	<!-- Breadcrumb -->
	<BreadcrumbNav items={[{ label: 'Creator Workspace' }, { label: 'RIYL Discovery' }]} />

	<!-- Header -->
	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-blue-100 rounded-lg">
					<Target class="w-6 h-6 text-blue-600" />
				</div>
				<h1 class="text-3xl font-bold">RIYL Discovery</h1>
			</div>
			<p class="text-muted-foreground">
				Find similar artists, understand your audience, and target the right listeners
			</p>
		</div>
		<Button href="/upload">
			<Music class="w-4 h-4 mr-2" />
			Upload Track
		</Button>
	</div>

	{#if loading}
		<!-- Loading State -->
		<div class="animate-pulse space-y-6">
			<Card class="p-6">
				<div class="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
				<div class="h-10 bg-gray-200 rounded w-full"></div>
			</Card>
		</div>
	{:else if error}
		<!-- Error State -->
		<InsightCard type="warning" message={error} />
	{:else if tracks.length === 0}
		<!-- Empty State -->
		<Card class="p-12 text-center">
			<div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-100 mb-6">
				<Target class="h-10 w-10 text-blue-600" />
			</div>
			<h3 class="text-xl font-semibold mb-2">No tracks to analyze</h3>
			<p class="text-muted-foreground mb-6 max-w-md mx-auto">
				Upload your first track to discover similar artists and find your audience.
			</p>
			<Button href="/upload" size="lg">
				<Music class="w-4 h-4 mr-2" />
				Upload Your First Track
			</Button>
		</Card>
	{:else}
		<!-- Track Selector -->
		<Card class="p-6">
			<label for="trackSelect" class="block text-sm font-medium mb-2">Select a track to analyze</label>
			<select
				id="trackSelect"
				bind:value={selectedTrackId}
				onchange={handleTrackSelect}
				class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
			>
				{#each tracks as track}
					<option value={track.id}>
						{track.title || 'Untitled'} - {track.artist_name || 'Unknown Artist'}
					</option>
				{/each}
			</select>
		</Card>

		{#if selectedTrack && !loadingRIYL}
			<!-- Selected Track Info -->
			<Card class="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
				<div class="flex items-start gap-4">
					<div class="p-3 bg-white rounded-lg">
						<Music class="w-8 h-8 text-blue-600" />
					</div>
					<div class="flex-1">
						<h3 class="text-xl font-bold mb-1">{selectedTrack.title || 'Untitled'}</h3>
						<p class="text-gray-600 mb-3">{selectedTrack.artist_name || 'Unknown Artist'}</p>
						{#if selectedTrack.tunescore?.overall_score}
							<Badge variant="default">TuneScore: {Math.round(selectedTrack.tunescore.overall_score)}/100</Badge>
						{/if}
					</div>
					<Button href={`/tracks/${selectedTrack.id}`} variant="outline">
						View Full Analysis
						<ArrowRight class="w-4 h-4 ml-2" />
					</Button>
				</div>
			</Card>
		{/if}

		{#if loadingRIYL}
			<!-- Loading RIYL -->
			<Card class="p-12 text-center">
				<div class="inline-block animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mb-4"></div>
				<p class="text-muted-foreground">Finding similar artists...</p>
			</Card>
		{:else if riylResults && riylResults.length > 0}
			<!-- Results Header -->
			<InsightCard
				type="success"
				title="🎯 Recommended If You Like (RIYL)"
				message={`Found ${riylResults.length} tracks similar to "${selectedTrack?.title || 'your track'}". Use these insights to target the right playlists and audiences.`}
			/>

			<!-- RIYL Results -->
			<div class="grid md:grid-cols-2 gap-6">
				{#each riylResults as result, index}
					<Card class="overflow-hidden hover:shadow-lg transition-all border-2 hover:border-primary/50">
						<div class="p-6">
							<!-- Rank Badge -->
							<div class="flex items-start justify-between mb-4">
								<Badge variant="secondary" class="text-xs">#{index + 1} Match</Badge>
								<div class="text-right">
									<div class="text-2xl font-bold {getSimilarityColor(result.similarity_score)}">
										{Math.round(result.similarity_score * 100)}%
									</div>
									<div class="text-xs text-gray-500">Similar</div>
								</div>
							</div>

							<!-- Track Info -->
							<h3 class="text-lg font-bold mb-1">
								{result.title || 'Untitled Track'}
							</h3>
							<p class="text-sm text-muted-foreground mb-4">
								{result.artist_name || 'Unknown Artist'}
							</p>

							<!-- Similarity Breakdown -->
							{#if result.similarity_breakdown}
								<div class="bg-gray-50 rounded-lg p-4 mb-4 space-y-2">
									<div class="text-xs font-semibold text-gray-700 mb-2">Similarity Factors</div>
									{#if result.similarity_breakdown.sonic}
										<div class="flex justify-between text-xs">
											<span class="text-gray-600">Sonic Match</span>
											<span class="font-semibold">{Math.round(result.similarity_breakdown.sonic * 100)}%</span>
										</div>
									{/if}
									{#if result.similarity_breakdown.lyrical}
										<div class="flex justify-between text-xs">
											<span class="text-gray-600">Lyrical Match</span>
											<span class="font-semibold">{Math.round(result.similarity_breakdown.lyrical * 100)}%</span>
										</div>
									{/if}
									{#if result.similarity_breakdown.style}
										<div class="flex justify-between text-xs">
											<span class="text-gray-600">Style Match</span>
											<span class="font-semibold">{Math.round(result.similarity_breakdown.style * 100)}%</span>
										</div>
									{/if}
								</div>
							{/if}

							<!-- Actions -->
							<div class="flex gap-2">
								<Button href={`/tracks/${result.id}`} variant="outline" size="sm" class="flex-1">
									<ArrowRight class="w-4 h-4 mr-1" />
									View Track
								</Button>
								<Button href={`/compare?track1=${selectedTrackId}&track2=${result.id}`} size="sm" variant="outline">
									Compare
								</Button>
							</div>
						</div>
					</Card>
				{/each}
			</div>

			<!-- Actionable Insights -->
			<div class="grid md:grid-cols-2 gap-6">
				<Card class="p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
					<div class="flex items-start gap-3 mb-4">
						<Users class="w-6 h-6 text-green-600 flex-shrink-0" />
						<div>
							<h3 class="font-semibold text-green-900 mb-1">Target Audience</h3>
							<p class="text-sm text-green-800">
								Listeners who follow these similar artists are your ideal audience. Target their playlists and communities.
							</p>
						</div>
					</div>
					<Button href="/audience-dna" variant="outline" size="sm" class="border-green-600 text-green-700 hover:bg-green-100">
						View Audience DNA
						<ArrowRight class="w-4 h-4 ml-2" />
					</Button>
				</Card>

				<Card class="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200">
					<div class="flex items-start gap-3 mb-4">
						<TrendingUp class="w-6 h-6 text-purple-600 flex-shrink-0" />
						<div>
							<h3 class="font-semibold text-purple-900 mb-1">Collaboration Potential</h3>
							<p class="text-sm text-purple-800">
								Artists with high similarity scores make excellent collaboration partners. Your styles complement each other.
							</p>
						</div>
					</div>
					<Button href="/collaboration-lab" variant="outline" size="sm" class="border-purple-600 text-purple-700 hover:bg-purple-100">
						Find Collaborators
						<ArrowRight class="w-4 h-4 ml-2" />
					</Button>
				</Card>
			</div>

			<!-- How to Use RIYL -->
			<Card class="p-6 bg-gray-50 border-2 border-gray-200">
				<h3 class="font-semibold mb-3">💡 How to Use RIYL Insights</h3>
				<div class="grid md:grid-cols-2 gap-4 text-sm text-gray-700">
					<div>
						<h4 class="font-semibold mb-2">For Marketing:</h4>
						<ul class="space-y-1 list-disc list-inside">
							<li>Pitch to playlists featuring similar artists</li>
							<li>Target ads to fans of these artists</li>
							<li>Use as comparisons in EPK/press releases</li>
							<li>Research their audience demographics</li>
						</ul>
					</div>
					<div>
						<h4 class="font-semibold mb-2">For Growth:</h4>
						<ul class="space-y-1 list-disc list-inside">
							<li>Tour in cities where these artists perform</li>
							<li>Collaborate with artists with 60-80% match</li>
							<li>Study their successful release strategies</li>
							<li>Engage with their fan communities</li>
						</ul>
					</div>
				</div>
			</Card>
		{:else if !loadingRIYL}
			<!-- No Results -->
			<InsightCard
				type="info"
				message="No similar tracks found. Try analyzing more tracks to build a better recommendation engine."
				actionLabel="Upload More Tracks"
				actionHref="/upload"
			/>
		{/if}
	{/if}
</div>

