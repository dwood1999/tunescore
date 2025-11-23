<script lang="ts">
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
	import DailyDigest from './components/DailyDigest.svelte';
	import ChartsSection from './components/ChartsSection.svelte';
	import NewsSection from './components/NewsSection.svelte';
	import ReleasesSection from './components/ReleasesSection.svelte';
	import OpportunitiesSection from './components/OpportunitiesSection.svelte';
	
	let { data } = $props();
	
	function formatLastUpdated(): string {
		return new Date().toLocaleTimeString('en-US', {
			hour: 'numeric',
			minute: '2-digit',
			hour12: true
		});
	}
</script>

<svelte:head>
	<title>Industry Pulse - TuneScore</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
	<div class="container mx-auto px-4 py-8 max-w-[1600px]">
		<!-- Header -->
		<header class="mb-8 text-center">
			<div class="max-w-4xl mx-auto">
				<h1 class="text-4xl lg:text-5xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
					📊 Industry Pulse
				</h1>
				<p class="text-lg lg:text-xl text-gray-400 mb-4">
					Real-time music industry intelligence
				</p>

				<div class="flex items-center justify-center gap-4 text-sm text-gray-500">
					<span>Updated: {formatLastUpdated()}</span>
				</div>
			</div>
		</header>

		<!-- Main Dashboard Grid -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6" in:fade>
			
			<!-- Executive Summary (Full Width) -->
			{#if data.digest}
				<div class="col-span-1 lg:col-span-3">
					<DailyDigest digest={data.digest} />
				</div>
			{/if}

			<!-- Indie Opportunities (Full Width) -->
			{#if data.digest?.extra_data}
				<div class="col-span-1 lg:col-span-3">
					<OpportunitiesSection 
						opportunities={data.digest.extra_data.opportunities || []} 
						takeaway={data.digest.extra_data.indie_takeaway || ""} 
					/>
				</div>
			{/if}

			<!-- Charts (Left Column) -->
			<div class="col-span-1 h-full">
				<ChartsSection charts={data.charts} />
			</div>

			<!-- News (Right Column - Spans 2) -->
			<div class="col-span-1 lg:col-span-2 h-full">
				<NewsSection news={data.news} />
			</div>

			<!-- Releases (Full Width) -->
			<div class="col-span-1 lg:col-span-3 mt-6">
				<ReleasesSection releases={data.releases} />
			</div>
		</div>
	</div>
</div>

<style>
	:global(body) {
		background-color: #030712; /* gray-950 */
	}
</style>
