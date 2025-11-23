<script lang="ts">
	import { Activity, TrendingUp, Music, BarChart3 } from 'lucide-svelte';
	import Card from '$lib/components/ui/card.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';
    import { onMount } from 'svelte';

    let loading = true;
    let trends: any = null;

    onMount(async () => {
        // In a real app, we would fetch trends from /api/v1/industry-pulse/charts or similar
        // For now, since we have no data source, we show empty state
        loading = false;
    });
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Developer Hub' }, { label: 'Trend Analysis' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-blue-100 rounded-lg">
					<Activity class="w-6 h-6 text-blue-600" />
				</div>
				<h1 class="text-3xl font-bold">Trend Analysis</h1>
			</div>
			<p class="text-muted-foreground">
				Market trend analysis and predictions for strategic releases
			</p>
		</div>
	</div>

    {#if loading}
        <div class="flex justify-center p-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
    {:else if !trends}
        <Card class="p-12 text-center">
            <div class="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Activity class="w-8 h-8 text-gray-400" />
            </div>
            <h3 class="text-lg font-semibold mb-2">No Trend Data Available</h3>
            <p class="text-gray-500 mb-6 max-w-md mx-auto">
                We are currently gathering market data. Check back later for global trend analysis.
            </p>
        </Card>
    {:else}
	<div class="grid md:grid-cols-3 gap-6">
		<MetricCard title="Trending Genres" value={trends.topGenres.length} icon={Music} />
		<MetricCard title="Top Genre Growth" value={`+${trends.topGenres[0].growth}%`} icon={TrendingUp} />
		<MetricCard title="Optimal BPM" value="110-120" icon={BarChart3} />
	</div>

	<InsightCard
		type="success"
		title="📈 What's Working Now"
		message={`${trends.topGenres[0].genre} is trending up ${trends.topGenres[0].growth}%. Tracks in the 110-120 BPM range are getting 3x more playlist adds. Lyrical themes around nostalgia and late-night vibes are resonating.`}
	/>

	<Card class="p-6">
		<h3 class="text-lg font-semibold mb-4">Top Trending Genres</h3>
		<div class="space-y-4">
			{#each trends.topGenres as trend}
				<div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
					<div>
						<div class="font-medium">{trend.genre}</div>
						<div class="text-sm text-gray-500">{trend.tracks} tracks analyzed</div>
					</div>
					<div class="text-green-600 font-semibold">+{trend.growth}%</div>
				</div>
			{/each}
		</div>
	</Card>
    {/if}
</div>

