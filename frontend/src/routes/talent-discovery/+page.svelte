<script lang="ts">
	import { onMount } from 'svelte';
	import { Users, TrendingUp, Filter, Star, ArrowRight } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';

	let tracks = $state<any[]>([]);
	let loading = $state(true);
	let minBreakoutScore = $state(6.0);
	let selectedGenre = $state<string>('all');
	let sortBy = $state<'breakout' | 'tunescore' | 'recent'>('breakout');

	onMount(async () => {
		try {
			tracks = await api.tracks.list();
		} catch (e) {
			console.error('Failed to load tracks:', e);
		} finally {
			loading = false;
		}
	});

	const filteredTracks = $derived(
		(tracks || [])
			.filter(t => {
				const breakoutScore = t.breakout_score?.overall_score || 0;
				const genreMatch = selectedGenre === 'all' || t.genre?.toLowerCase().includes(selectedGenre.toLowerCase());
				return breakoutScore >= minBreakoutScore && genreMatch;
			})
			.sort((a, b) => {
				if (sortBy === 'breakout') {
					return (b.breakout_score?.overall_score || 0) - (a.breakout_score?.overall_score || 0);
				} else if (sortBy === 'tunescore') {
					return (b.tunescore?.overall_score || 0) - (a.tunescore?.overall_score || 0);
				} else {
					return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
				}
			})
	);

	const risingArtists = $derived(filteredTracks ? filteredTracks.filter(t => (t.breakout_score?.overall_score || 0) >= 8) : []);
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Developer Hub' }, { label: 'Talent Discovery' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-purple-100 rounded-lg">
					<Users class="w-6 h-6 text-purple-600" />
				</div>
				<h1 class="text-3xl font-bold">Talent Discovery</h1>
			</div>
			<p class="text-muted-foreground">
				A&R-focused talent scouting and breakout prediction
			</p>
		</div>
	</div>

	{#if loading}
		<div class="animate-pulse space-y-6">
			<div class="grid md:grid-cols-3 gap-6">
				{#each Array(3) as _}
					<Card class="p-6">
						<div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
						<div class="h-8 bg-gray-200 rounded w-1/2"></div>
					</Card>
				{/each}
			</div>
		</div>
	{:else}
		<div class="grid md:grid-cols-3 gap-6">
			<MetricCard
				title="Total Artists"
				value={tracks.length}
				icon={Users}
			/>
			<MetricCard
				title="Rising Stars"
				value={risingArtists.length}
				icon={TrendingUp}
			/>
			<MetricCard
				title="Avg Breakout Score"
				value={(filteredTracks.reduce((sum, t) => sum + (t.breakout_score?.overall_score || 0), 0) / (filteredTracks.length || 1)).toFixed(1)}
				icon={Star}
			/>
		</div>

		{#if risingArtists.length > 0}
			<InsightCard
				type="success"
				title="⭐ Rising Stars Detected"
				message={`Found ${risingArtists.length} artists with breakout potential (8.0+). These are your top prospects for signing.`}
			/>
		{/if}

		<!-- Filters -->
		<Card class="p-4">
			<div class="flex flex-wrap items-center gap-4">
				<div class="flex items-center gap-2">
					<Filter class="w-4 h-4 text-gray-500" />
					<label class="text-sm font-medium">Min Breakout Score:</label>
					<input
						type="range"
						min="0"
						max="10"
						step="0.5"
						bind:value={minBreakoutScore}
						class="w-32"
					/>
					<span class="text-sm font-semibold w-8">{minBreakoutScore.toFixed(1)}</span>
				</div>

				<div class="flex items-center gap-2">
					<span class="text-sm font-medium">Sort:</span>
					<Button
						variant={sortBy === 'breakout' ? 'default' : 'outline'}
						size="sm"
						onclick={() => { sortBy = 'breakout'; }}
					>
						Breakout Score
					</Button>
					<Button
						variant={sortBy === 'tunescore' ? 'default' : 'outline'}
						size="sm"
						onclick={() => { sortBy = 'tunescore'; }}
					>
						TuneScore
					</Button>
				</div>
			</div>
		</Card>

		<!-- Talent Grid -->
		<div class="grid md:grid-cols-2 gap-6">
			{#each filteredTracks as track}
				<Card class="p-6 hover:shadow-lg transition-all border-2 hover:border-primary/50">
					<div class="flex items-start justify-between mb-4">
						<div class="flex-1">
							<h3 class="text-lg font-bold mb-1">{track.title || 'Untitled'}</h3>
							<p class="text-sm text-muted-foreground">{track.artist_name || 'Unknown Artist'}</p>
							{#if track.genre}
								<Badge variant="secondary" class="mt-2">{track.genre}</Badge>
							{/if}
						</div>
						{#if track.breakout_score?.overall_score}
							<div class="text-right">
								<div class="text-3xl font-bold text-primary">
									{track.breakout_score.overall_score.toFixed(1)}
								</div>
								<div class="text-xs text-gray-500">Breakout Score</div>
							</div>
						{/if}
					</div>

					<div class="flex gap-2">
						<Button href={`/tracks/${track.id}`} variant="outline" size="sm" class="flex-1">
							<ArrowRight class="w-4 h-4 mr-1" />
							View Analysis
						</Button>
					</div>
				</Card>
			{/each}
		</div>

		{#if filteredTracks.length === 0}
			<InsightCard
				type="info"
				message="No artists match your current filters. Try adjusting the minimum breakout score."
			/>
		{/if}
	{/if}
</div>

