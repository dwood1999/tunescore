<script lang="ts">
	import { Users, MapPin, TrendingUp, Music2, Youtube, Instagram } from 'lucide-svelte';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';
    import { onMount } from 'svelte';

    let loading = true;
    let error: string | null = null;
    let audienceData: any = null;

    // In a real implementation, we would fetch this from the user's profile or selected artist
    const channelId: string | null = null; 

    onMount(async () => {
        if (!channelId) {
            loading = false;
            return;
        }

        try {
            // Fetch logic here would go here
            // const res = await fetch(\`/api/v1/integrations/youtube-analytics/channel/\${channelId}/demographics\`);
            // audienceData = await res.json();
        } catch (e) {
            error = "Failed to load audience data";
        } finally {
            loading = false;
        }
    });
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Creator Workspace' }, { label: 'Audience DNA' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-green-100 rounded-lg">
					<Users class="w-6 h-6 text-green-600" />
				</div>
				<h1 class="text-3xl font-bold">Audience DNA</h1>
			</div>
			<p class="text-muted-foreground">
				Deep dive into your audience demographics, location, and platform preferences
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
    {:else if !channelId || !audienceData}
        <Card class="p-12 text-center">
            <div class="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Users class="w-8 h-8 text-gray-400" />
            </div>
            <h3 class="text-lg font-semibold mb-2">No Audience Data Available</h3>
            <p class="text-gray-500 mb-6 max-w-md mx-auto">
                Connect your YouTube, Spotify, or social media accounts to unlock audience insights and demographic data.
            </p>
            <Button href="/integrations">Connect Integrations</Button>
        </Card>
    {:else}
	<!-- Stats Overview -->
	<div class="grid md:grid-cols-3 gap-6">
		<MetricCard
			title="Total Listeners"
			value={audienceData.totalListeners.toLocaleString()}
			change={audienceData.monthlyGrowth}
			changeLabel="vs last month"
			icon={Users}
		/>
		<MetricCard
			title="Top Market"
			value={audienceData.topCities[0].city}
			change={audienceData.topCities[0].growth}
			changeLabel="growth"
			icon={MapPin}
		/>
		<MetricCard
			title="Primary Age"
			value={audienceData.demographics.ageRanges[0].range}
			icon={TrendingUp}
		/>
	</div>

	<!-- Top Cities -->
	<Card class="p-6">
		<h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
			<MapPin class="w-5 h-5 text-primary" />
			Top Markets
		</h3>
		<div class="space-y-4">
			{#each audienceData.topCities as city}
				<div class="flex items-center justify-between">
					<div class="flex-1">
						<div class="font-medium">{city.city}</div>
						<div class="text-sm text-gray-500">{city.listeners.toLocaleString()} listeners</div>
					</div>
					<Badge variant={city.growth > 30 ? 'default' : 'secondary'}>
						+{city.growth}% growth
					</Badge>
				</div>
			{/each}
		</div>
	</Card>

	<!-- Platform Distribution -->
	<Card class="p-6">
		<h3 class="text-lg font-semibold mb-4">Platform Distribution</h3>
		<div class="grid md:grid-cols-3 gap-4">
			{#each audienceData.platforms as platform}
				<div class="p-4 bg-gray-50 rounded-lg">
					<div class="flex items-center gap-2 mb-2">
						<svelte:component this={platform.icon} class="w-5 h-5 text-primary" />
						<span class="font-medium">{platform.name}</span>
					</div>
					<div class="text-2xl font-bold">{platform.listeners.toLocaleString()}</div>
					<div class="text-sm text-gray-500">listeners</div>
				</div>
			{/each}
		</div>
	</Card>

	<!-- Actionable Insights -->
	<InsightCard
		type="success"
		title="🎯 Marketing Recommendations"
		message="Focus tour routing and ad spend on top performing markets where you're seeing the fastest growth."
		actionLabel="View Integrations"
		actionHref="/integrations"
	/>
    {/if}
</div>

