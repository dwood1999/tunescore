<script lang="ts">
	import { onMount } from 'svelte';
	import { TrendingUp, Clock, Target, ArrowRight } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';

	let tracks = $state<any[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			tracks = await api.tracks.list();
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});

	const sortedTracks = $derived(
		(tracks || []).sort((a, b) => (b.breakout_score?.overall_score || 0) - (a.breakout_score?.overall_score || 0))
	);
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Developer Hub' }, { label: 'Breakout Scores' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-orange-100 rounded-lg">
					<TrendingUp class="w-6 h-6 text-orange-600" />
				</div>
				<h1 class="text-3xl font-bold">Breakout Scores</h1>
			</div>
			<p class="text-muted-foreground">
				Predictive breakout analysis and commercial potential scoring
			</p>
		</div>
	</div>

	{#if !loading}
		<div class="grid md:grid-cols-3 gap-6">
			<MetricCard title="Tracks Analyzed" value={tracks.length} icon={TrendingUp} />
			<MetricCard title="High Potential (8+)" value={tracks.filter(t => (t.breakout_score?.overall_score || 0) >= 8).length} icon={Target} />
			<MetricCard title="Ready to Release" value={tracks.filter(t => (t.breakout_score?.overall_score || 0) >= 7).length} icon={Clock} />
		</div>

		<InsightCard
			type="insight"
			title="💡 What is Breakout Score?"
			message="Breakout Score predicts commercial success by analyzing trend alignment, sonic quality, hook potential, and market positioning. Scores above 8.0 indicate strong breakout potential."
		/>

		<div class="grid md:grid-cols-2 gap-6">
			{#each sortedTracks as track}
				<Card class="p-6 hover:shadow-lg transition-all">
					<div class="flex items-start justify-between mb-4">
						<div class="flex-1">
							<h3 class="text-lg font-bold">{track.title || 'Untitled'}</h3>
							<p class="text-sm text-muted-foreground">{track.artist_name || 'Unknown'}</p>
						</div>
						<div class="text-3xl font-bold text-orange-600">
							{(track.breakout_score?.overall_score || 0).toFixed(1)}
						</div>
					</div>
					<Button href={`/tracks/${track.id}`} size="sm" variant="outline" class="w-full">
						View Details <ArrowRight class="w-4 h-4 ml-2" />
					</Button>
				</Card>
			{/each}
		</div>
	{/if}
</div>

