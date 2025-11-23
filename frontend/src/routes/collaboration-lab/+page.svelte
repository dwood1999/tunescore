<script lang="ts">
	import { onMount } from 'svelte';
	import { Briefcase, Users, TrendingUp, ArrowRight } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
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
</script>

<div class="space-y-6">
	<BreadcrumbNav items={[{ label: 'Developer Hub' }, { label: 'Collaboration Lab' }]} />

	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-indigo-100 rounded-lg">
					<Briefcase class="w-6 h-6 text-indigo-600" />
				</div>
				<h1 class="text-3xl font-bold">Collaboration Lab</h1>
			</div>
			<p class="text-muted-foreground">
				Find and evaluate collaboration opportunities with compatible artists
			</p>
		</div>
	</div>

	<InsightCard
		type="insight"
		title="🤝 Find Your Creative Partners"
		message="Collaboration Lab analyzes sonic and lyrical compatibility to find artists whose style complements yours. Look for 60-80% similarity for the best creative tension."
		actionLabel="View RIYL Discovery"
		actionHref="/riyl-discovery"
	/>

	<Card class="p-12 text-center">
		<div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-indigo-100 mb-6">
			<Users class="h-10 w-10 text-indigo-600" />
		</div>
		<h3 class="text-xl font-semibold mb-2">Find Collaborators</h3>
		<p class="text-muted-foreground mb-6 max-w-md mx-auto">
			Use RIYL Discovery to find artists with compatible styles, then reach out for collaborations.
		</p>
		<Button href="/riyl-discovery" size="lg">
			Discover Similar Artists
		</Button>
	</Card>
</div>

