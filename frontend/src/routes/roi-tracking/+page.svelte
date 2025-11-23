<script lang="ts">
	import { TrendingUp, DollarSign, Target, Music2, Youtube, Instagram } from 'lucide-svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';
    import { onMount } from 'svelte';

    let loading = true;
    let campaigns: any[] = [];

    function getRoiColor(roi: number): string {
		if (roi >= 1.5) return 'text-green-600';
		if (roi >= 0.8) return 'text-blue-600';
		return 'text-red-600';
	}

	function getRoiBg(roi: number): string {
		if (roi >= 1.5) return 'bg-green-50 border-green-200';
		if (roi >= 0.8) return 'bg-blue-50 border-blue-200';
		return 'bg-red-50 border-red-200';
	}

    onMount(async () => {
        // Fetch logic here
        loading = false;
    });
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Monetizer Intelligence' }, { label: 'ROI Tracking' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-emerald-100 rounded-lg">
					<DollarSign class="w-6 h-6 text-emerald-600" />
				</div>
				<h1 class="text-3xl font-bold">ROI Tracking</h1>
			</div>
			<p class="text-muted-foreground">
				Campaign and marketing ROI analysis across all platforms
			</p>
		</div>
		<Button href="/integrations">
			Add Campaign
		</Button>
	</div>

    {#if loading}
         <div class="flex justify-center p-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
    {:else if campaigns.length === 0}
        <Card class="p-12 text-center">
            <div class="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <DollarSign class="w-8 h-8 text-gray-400" />
            </div>
            <h3 class="text-lg font-semibold mb-2">No Campaigns Found</h3>
            <p class="text-gray-500 mb-6 max-w-md mx-auto">
                Track your marketing spend and ROI. Add your first campaign to get started.
            </p>
            <Button href="/integrations">Create Campaign</Button>
        </Card>
    {:else}
	<div class="grid md:grid-cols-4 gap-6">
		<MetricCard
			title="Total Spent"
			value={`$${campaigns.reduce((sum, c) => sum + c.spent, 0).toLocaleString()}`}
			icon={DollarSign}
		/>
		<MetricCard
			title="Total Streams"
			value={campaigns.reduce((sum, c) => sum + c.streams, 0).toLocaleString()}
			icon={TrendingUp}
		/>
		<MetricCard
			title="New Followers"
			value={campaigns.reduce((sum, c) => sum + c.followers, 0).toLocaleString()}
			icon={Target}
		/>
		<MetricCard
			title="Avg ROI"
			value={`${(campaigns.reduce((sum, c) => sum + c.roi, 0) / campaigns.length).toFixed(1)}x`}
			icon={TrendingUp}
		/>
	</div>

	<InsightCard
		type="success"
		title="💰 Best Performing Campaign"
		message={`${campaigns.sort((a, b) => b.roi - a.roi)[0].name} achieved ${campaigns.sort((a, b) => b.roi - a.roi)[0].roi}x ROI - consider repeating this strategy.`}
	/>

	<Card class="p-6">
		<h3 class="text-lg font-semibold mb-4">Campaign Performance</h3>
		<div class="space-y-4">
			{#each campaigns as campaign}
				<Card class="p-4 {getRoiBg(campaign.roi)} border-2">
					<div class="flex items-start justify-between mb-3">
						<div class="flex-1">
							<h4 class="font-semibold mb-1">{campaign.name}</h4>
							<Badge variant="secondary">{campaign.platform}</Badge>
						</div>
						<div class="text-right">
							<div class="text-2xl font-bold {getRoiColor(campaign.roi)}">{campaign.roi.toFixed(1)}x</div>
							<div class="text-xs text-gray-500">ROI</div>
						</div>
					</div>
					<div class="grid grid-cols-3 gap-4 text-sm">
						<div>
							<div class="text-gray-600">Spent</div>
							<div class="font-semibold">${campaign.spent}</div>
						</div>
						<div>
							<div class="text-gray-600">Streams</div>
							<div class="font-semibold">{campaign.streams.toLocaleString()}</div>
						</div>
						<div>
							<div class="text-gray-600">Followers</div>
							<div class="font-semibold">{campaign.followers}</div>
						</div>
					</div>
				</Card>
			{/each}
		</div>
	</Card>

	<Card class="p-6 bg-gray-50">
		<h3 class="font-semibold mb-3">💡 How to Use ROI Tracking</h3>
		<div class="text-sm text-gray-700 space-y-2">
			<p><strong>ROI above 1.5x:</strong> Excellent return - repeat and scale this strategy</p>
			<p><strong>ROI 0.8-1.5x:</strong> Positive return - optimize and continue</p>
			<p><strong>ROI below 0.8x:</strong> Underperforming - pause and analyze what went wrong</p>
		</div>
	</Card>
    {/if}
</div>

