<script lang="ts">
	import { onMount } from 'svelte';
	import DailyDigest from './components/DailyDigest.svelte';
	import ChartsSection from './components/ChartsSection.svelte';
	import NewsSection from './components/NewsSection.svelte';
	import ReleasesSection from './components/ReleasesSection.svelte';
	
	let { data } = $props();
	let activeTab = $state('charts');
	
	const tabs = [
		{ id: 'charts', label: 'Charts', icon: '🔥' },
		{ id: 'news', label: 'News', icon: '📰' },
		{ id: 'releases', label: 'Releases', icon: '🎵' }
	];
</script>

<svelte:head>
	<title>Industry Pulse - TuneScore</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<div class="container mx-auto px-4 py-8 max-w-7xl">
		<!-- Header -->
		<div class="mb-8">
			<h1 class="text-4xl font-bold text-gray-900 mb-2">
				Industry Pulse
			</h1>
			<p class="text-lg text-gray-600">
				Real-time music industry intelligence - Bloomberg Terminal for Music
			</p>
		</div>

		<!-- Daily Digest -->
		{#if data.digest}
			<DailyDigest digest={data.digest} />
		{/if}

		<!-- Tab Navigation -->
		<div class="bg-white rounded-lg shadow-sm mb-6 p-2">
			<nav class="flex space-x-2" aria-label="Industry Pulse Sections">
				{#each tabs as tab}
					<button
						onclick={() => activeTab = tab.id}
						class="flex-1 px-6 py-3 text-sm font-medium rounded-md transition-colors
							{activeTab === tab.id
								? 'bg-blue-600 text-white shadow-sm'
								: 'text-gray-700 hover:bg-gray-100'}"
					>
						<span class="mr-2">{tab.icon}</span>
						{tab.label}
					</button>
				{/each}
			</nav>
		</div>

		<!-- Tab Content -->
		<div class="transition-all duration-300">
			{#if activeTab === 'charts'}
				<ChartsSection charts={data.charts} />
			{:else if activeTab === 'news'}
				<NewsSection news={data.news} />
			{:else if activeTab === 'releases'}
				<ReleasesSection releases={data.releases} />
			{/if}
		</div>
	</div>
</div>

<style>
	/* Add smooth transitions */
	:global(body) {
		transition: background-color 0.3s ease;
	}
</style>

