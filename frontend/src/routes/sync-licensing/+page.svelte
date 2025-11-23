<script lang="ts">
	import { onMount } from 'svelte';
	import { Music, Tv, Film, Gamepad2, ArrowRight } from 'lucide-svelte';
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

	const syncCategories = [
		{ id: 'tv', label: 'TV Shows', icon: Tv, color: 'blue' },
		{ id: 'film', label: 'Film', icon: Film, color: 'purple' },
		{ id: 'ads', label: 'Advertising', icon: Music, color: 'green' },
		{ id: 'games', label: 'Video Games', icon: Gamepad2, color: 'orange' }
	];
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Monetizer Intelligence' }, { label: 'Sync Licensing' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-purple-100 rounded-lg">
					<Film class="w-6 h-6 text-purple-600" />
				</div>
				<h1 class="text-3xl font-bold">Sync Licensing</h1>
			</div>
			<p class="text-muted-foreground">
				Sync licensing opportunities and pitch generation
			</p>
		</div>
	</div>

	{#if !loading}
		<div class="grid md:grid-cols-4 gap-6">
			<MetricCard title="Total Tracks" value={tracks.length} icon={Music} />
			<MetricCard title="High Potential" value={tracks.filter(t => t.tunescore?.overall_score >= 80).length} icon={Tv} />
			<MetricCard title="Instrumental" value={tracks.filter(t => !t.has_lyrics).length} icon={Film} />
			<MetricCard title="Ready for Sync" value={tracks.filter(t => t.tunescore?.overall_score >= 70).length} icon={Gamepad2} />
		</div>

		<InsightCard
			type="insight"
			title="💡 Sync Licensing Opportunities"
			message="Tracks with high production quality and clear emotional arcs are ideal for sync placement. Focus on instrumental versions and clean edits."
		/>

		<Card class="p-6">
			<h3 class="text-lg font-semibold mb-4">Sync Use Cases</h3>
			<div class="grid md:grid-cols-4 gap-4">
				{#each syncCategories as category}
					<div class="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
						<svelte:component this={category.icon} class="w-8 h-8 text-{category.color}-600 mb-2" />
						<div class="font-medium">{category.label}</div>
						<div class="text-sm text-gray-500 mt-1">View matches</div>
					</div>
				{/each}
			</div>
		</Card>

		<div class="grid md:grid-cols-2 gap-6">
			{#each tracks.slice(0, 6) as track}
				<Card class="p-6 hover:shadow-lg transition-all">
					<div class="flex items-start justify-between mb-4">
						<div class="flex-1">
							<h3 class="text-lg font-bold">{track.title || 'Untitled'}</h3>
							<p class="text-sm text-muted-foreground">{track.artist_name || 'Unknown'}</p>
							{#if track.genre}
								<Badge variant="secondary" class="mt-2">{track.genre}</Badge>
							{/if}
						</div>
						{#if track.tunescore?.overall_score}
							<div class="text-2xl font-bold text-primary">
								{Math.round(track.tunescore.overall_score)}
							</div>
						{/if}
					</div>
					<div class="flex gap-2">
						<Button href={`/tracks/${track.id}`} size="sm" variant="outline" class="flex-1">
							Generate Pitch <ArrowRight class="w-4 h-4 ml-2" />
						</Button>
					</div>
				</Card>
			{/each}
		</div>
	{/if}
</div>

