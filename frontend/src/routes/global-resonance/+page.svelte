<script lang="ts">
	import { Globe, MapPin, TrendingUp, Music2 } from 'lucide-svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';
    import { onMount } from 'svelte';

    let loading = true;
    let error: string | null = null;
    let globalData: any = null;

    const channelId: string | null = null;

    onMount(async () => {
        if (!channelId) {
            loading = false;
            return;
        }
        // Fetch logic here
        loading = false;
    });
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Monetizer Intelligence' }, { label: 'Global Resonance' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-cyan-100 rounded-lg">
					<Globe class="w-6 h-6 text-cyan-600" />
				</div>
				<h1 class="text-3xl font-bold">Global Resonance</h1>
			</div>
			<p class="text-muted-foreground">
				Multi-market performance analysis and cultural resonance scoring
			</p>
		</div>
		<Button href="/integrations">
			Connect Platforms
		</Button>
	</div>

    {#if loading}
         <div class="flex justify-center p-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
    {:else if !channelId || !globalData}
        <Card class="p-12 text-center">
            <div class="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Globe class="w-8 h-8 text-gray-400" />
            </div>
            <h3 class="text-lg font-semibold mb-2">No Global Data Available</h3>
            <p class="text-gray-500 mb-6 max-w-md mx-auto">
                Connect your YouTube or Spotify accounts to see global streaming data and market analysis.
            </p>
            <Button href="/integrations">Connect Integrations</Button>
        </Card>
    {:else}
	<div class="grid md:grid-cols-3 gap-6">
		<MetricCard
			title="Active Markets"
			value={globalData.topMarkets.length}
			icon={Globe}
		/>
		<MetricCard
			title="Top Market"
			value={globalData.topMarkets[0].country}
			change={globalData.topMarkets[0].growth}
			changeLabel="growth"
			icon={MapPin}
		/>
		<MetricCard
			title="Emerging Markets"
			value={globalData.emergingMarkets.length}
			icon={TrendingUp}
		/>
	</div>

	<InsightCard
		type="success"
		title="🌍 Market Opportunity"
		message={`${globalData.emergingMarkets[0].country} showing ${globalData.emergingMarkets[0].growth}% growth - consider targeted marketing campaigns in emerging markets.`}
	/>

	<Card class="p-6">
		<h3 class="text-lg font-semibold mb-4">Top Markets by Streams</h3>
		<div class="space-y-4">
			{#each globalData.topMarkets as market}
				<div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
					<div class="flex items-center gap-3">
						<span class="text-2xl">{market.flag}</span>
						<div>
							<div class="font-medium">{market.country}</div>
							<div class="text-sm text-gray-500">{market.streams.toLocaleString()} streams</div>
						</div>
					</div>
					<Badge variant={market.growth > 30 ? 'default' : 'secondary'}>
						+{market.growth}%
					</Badge>
				</div>
			{/each}
		</div>
	</Card>

	<Card class="p-6 bg-gradient-to-br from-cyan-50 to-blue-50 border-2 border-cyan-200">
		<h3 class="text-lg font-semibold mb-4">🚀 Emerging Markets</h3>
		<div class="grid md:grid-cols-3 gap-4">
			{#each globalData.emergingMarkets as market}
				<div class="bg-white p-4 rounded-lg">
					<span class="text-3xl mb-2 block">{market.flag}</span>
					<div class="font-medium mb-1">{market.country}</div>
					<div class="text-2xl font-bold text-cyan-600">+{market.growth}%</div>
					<div class="text-xs text-gray-500">growth</div>
				</div>
			{/each}
		</div>
	</Card>
    {/if}
</div>

