<script lang="ts">
	import { onMount } from 'svelte';
	import { Zap, Play, TrendingUp, ArrowRight, Filter, Download, Copy } from 'lucide-svelte';
	import { api } from '$lib/api/client';
	import Card from '$lib/components/ui/card.svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';
	import BreadcrumbNav from '$lib/components/BreadcrumbNav.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import InsightCard from '$lib/components/InsightCard.svelte';

	let tracks = $state<any[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let minHookScore = $state(0);
	let sortBy = $state<'hook_score' | 'title' | 'date'>('hook_score');
	let comparisonMode = $state(false);
	let selectedTracks = $state<Set<number>>(new Set());

	onMount(async () => {
		try {
			tracks = await api.tracks.list();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load tracks';
		} finally {
			loading = false;
		}
	});

	// Filter and sort tracks
	const filteredTracks = $derived(
		(tracks || [])
			.filter(t => t.analysis?.hook_detection?.hook_score >= minHookScore)
			.sort((a, b) => {
				if (sortBy === 'hook_score') {
					const scoreA = a.analysis?.hook_detection?.hook_score || 0;
					const scoreB = b.analysis?.hook_detection?.hook_score || 0;
					return scoreB - scoreA;
				} else if (sortBy === 'title') {
					return (a.title || '').localeCompare(b.title || '');
				} else {
					return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
				}
			})
	);

	// Calculate stats
	const avgHookScore = $derived(
		filteredTracks && filteredTracks.length > 0
			? Math.round(
					filteredTracks.reduce((sum, t) => sum + (t.analysis?.hook_detection?.hook_score || 0), 0) /
						filteredTracks.length
			  )
			: 0
	);

	const topHookTrack = $derived(
		filteredTracks && filteredTracks.length > 0 ? filteredTracks[0] : null
	);

	const strongHooks = $derived(
		filteredTracks ? filteredTracks.filter(t => (t.analysis?.hook_detection?.hook_score || 0) >= 80).length : 0
	);

	function toggleTrackSelection(trackId: number) {
		const newSet = new Set(selectedTracks);
		if (newSet.has(trackId)) {
			newSet.delete(trackId);
		} else {
			if (newSet.size < 2) {
				newSet.add(trackId);
			}
		}
		selectedTracks = newSet;
	}

	function formatTime(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = Math.floor(seconds % 60);
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	function getHookScoreColor(score: number): string {
		if (score >= 80) return 'text-green-600';
		if (score >= 60) return 'text-blue-600';
		if (score >= 40) return 'text-yellow-600';
		return 'text-red-600';
	}

	function getHookScoreBg(score: number): string {
		if (score >= 80) return 'bg-green-50 border-green-200';
		if (score >= 60) return 'bg-blue-50 border-blue-200';
		if (score >= 40) return 'bg-yellow-50 border-yellow-200';
		return 'bg-red-50 border-red-200';
	}

	async function copyHookTimestamp(track: any) {
		const hookStart = track.analysis?.hook_detection?.best_segment?.start || 0;
		const text = `Hook at ${formatTime(hookStart)} in "${track.title || 'Untitled'}"`;
		await navigator.clipboard.writeText(text);
	}
</script>

<div class="space-y-6">
	<!-- Breadcrumb -->
	<BreadcrumbNav items={[{ label: 'Creator Workspace' }, { label: 'Hook Lab' }]} />

	<!-- Header -->
	<div class="flex items-start justify-between">
		<div>
			<div class="flex items-center gap-3 mb-2">
				<div class="p-2 bg-purple-100 rounded-lg">
					<Zap class="w-6 h-6 text-purple-600" />
				</div>
				<h1 class="text-3xl font-bold">Hook Lab</h1>
			</div>
			<p class="text-muted-foreground">
				Analyze, compare, and optimize your most viral moments
			</p>
		</div>
		<Button href="/upload">
			<Zap class="w-4 h-4 mr-2" />
			Upload Track
		</Button>
	</div>

	{#if loading}
		<!-- Loading State -->
		<div class="grid md:grid-cols-3 gap-6">
			{#each Array(3) as _}
				<Card class="p-6 animate-pulse">
					<div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
					<div class="h-8 bg-gray-200 rounded w-1/2"></div>
				</Card>
			{/each}
		</div>
	{:else if error}
		<!-- Error State -->
		<InsightCard type="warning" message={error} />
	{:else if tracks.length === 0}
		<!-- Empty State -->
		<Card class="p-12 text-center">
			<div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-100 mb-6">
				<Zap class="h-10 w-10 text-purple-600" />
			</div>
			<h3 class="text-xl font-semibold mb-2">No tracks analyzed yet</h3>
			<p class="text-muted-foreground mb-6 max-w-md mx-auto">
				Upload your first track to discover your hooks and viral segments.
			</p>
			<Button href="/upload" size="lg">
				<Zap class="w-4 h-4 mr-2" />
				Upload Your First Track
			</Button>
		</Card>
	{:else}
		<!-- Stats Overview -->
		<div class="grid md:grid-cols-3 gap-6">
			<MetricCard
				title="Tracks Analyzed"
				value={filteredTracks.length}
				icon={Zap}
			/>
			<MetricCard
				title="Avg Hook Score"
				value={avgHookScore}
				icon={TrendingUp}
			/>
			<MetricCard
				title="Strong Hooks (80+)"
				value={strongHooks}
				icon={Zap}
			/>
		</div>

		<!-- Top Hook Insight -->
		{#if topHookTrack}
			<InsightCard
				type="success"
				title="🔥 Top Hook"
				message={`"${topHookTrack.title || 'Untitled'}" has your strongest hook with a score of ${topHookTrack.analysis?.hook_detection?.hook_score || 0}/100`}
				actionLabel="View Track"
				actionHref={`/tracks/${topHookTrack.id}`}
			/>
		{/if}

		<!-- Filters and Controls -->
		<Card class="p-4">
			<div class="flex flex-wrap items-center gap-4">
				<!-- Hook Score Filter -->
				<div class="flex items-center gap-2">
					<Filter class="w-4 h-4 text-gray-500" />
					<label for="minHookScore" class="text-sm font-medium">Min Hook Score:</label>
					<input
						id="minHookScore"
						type="range"
						min="0"
						max="100"
						step="10"
						bind:value={minHookScore}
						class="w-32"
					/>
					<span class="text-sm font-semibold w-8">{minHookScore}</span>
				</div>

				<!-- Sort -->
				<div class="flex items-center gap-2">
					<span class="text-sm font-medium">Sort:</span>
					<Button
						variant={sortBy === 'hook_score' ? 'default' : 'outline'}
						size="sm"
						onclick={() => { sortBy = 'hook_score'; }}
					>
						Hook Score
					</Button>
					<Button
						variant={sortBy === 'title' ? 'default' : 'outline'}
						size="sm"
						onclick={() => { sortBy = 'title'; }}
					>
						Title
					</Button>
					<Button
						variant={sortBy === 'date' ? 'default' : 'outline'}
						size="sm"
						onclick={() => { sortBy = 'date'; }}
					>
						Date
					</Button>
				</div>

				<!-- Comparison Mode -->
				<div class="ml-auto flex items-center gap-2">
					<Button
						variant={comparisonMode ? 'default' : 'outline'}
						size="sm"
						onclick={() => {
							comparisonMode = !comparisonMode;
							if (!comparisonMode) {
								selectedTracks = new Set();
							}
						}}
					>
						{comparisonMode ? 'Exit' : 'Compare Mode'}
					</Button>
				</div>
			</div>
		</Card>

		<!-- Comparison View -->
		{#if comparisonMode && selectedTracks.size === 2}
			<Card class="p-6 bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200">
				<h3 class="text-lg font-semibold mb-4">Hook Battle</h3>
				<div class="grid md:grid-cols-2 gap-4">
					{#each Array.from(selectedTracks) as trackId}
						{@const track = tracks.find(t => t.id === trackId)}
						{#if track}
							<div class="bg-white p-4 rounded-lg">
								<h4 class="font-semibold mb-2">{track.title || 'Untitled'}</h4>
								<div class="text-3xl font-bold {getHookScoreColor(track.analysis?.hook_detection?.hook_score || 0)} mb-2">
									{track.analysis?.hook_detection?.hook_score || 0}
								</div>
								<p class="text-sm text-gray-600 mb-2">
									Hook at {formatTime(track.analysis?.hook_detection?.best_segment?.start || 0)}
								</p>
								<Button href={`/tracks/${track.id}`} size="sm" variant="outline">
									View Details
								</Button>
							</div>
						{/if}
					{/each}
				</div>
			</Card>
		{/if}

		<!-- Tracks Grid -->
		<div class="grid md:grid-cols-2 gap-6">
			{#each filteredTracks as track (track.id)}
				<Card class="overflow-hidden border-2 hover:border-primary/50 transition-all {comparisonMode ? 'cursor-pointer' : ''}">
					<div 
						class="p-6"
						onclick={() => {
							if (comparisonMode) {
								toggleTrackSelection(track.id);
							}
						}}
					>
						{#if comparisonMode}
							<div class="absolute top-4 right-4">
								<input
									type="checkbox"
									checked={selectedTracks.has(track.id)}
									disabled={!selectedTracks.has(track.id) && selectedTracks.size >= 2}
									class="w-5 h-5"
								/>
							</div>
						{/if}

						<!-- Track Info -->
						<div class="flex items-start justify-between mb-4">
							<div class="flex-1">
								<h3 class="text-lg font-bold mb-1">
									{track.title || 'Untitled Track'}
								</h3>
								<p class="text-sm text-muted-foreground">
									{track.artist_name || 'Unknown Artist'}
								</p>
							</div>
							{#if track.analysis?.hook_detection?.hook_score}
								<div class="flex-shrink-0 ml-4">
									<div class="w-16 h-16 rounded-full {getHookScoreBg(track.analysis.hook_detection.hook_score)} border-2 flex flex-col items-center justify-center">
										<div class="text-xl font-bold {getHookScoreColor(track.analysis.hook_detection.hook_score)}">
											{Math.round(track.analysis.hook_detection.hook_score)}
										</div>
										<div class="text-xs text-gray-500">Hook</div>
									</div>
								</div>
							{/if}
						</div>

						<!-- Hook Details -->
						{#if track.analysis?.hook_detection}
							<div class="bg-gray-50 rounded-lg p-4 mb-4">
								<div class="flex items-center justify-between mb-2">
									<span class="text-sm font-medium text-gray-700">Best Hook Segment</span>
									<Badge variant="secondary">
										{formatTime(track.analysis.hook_detection.best_segment?.start || 0)} - 
										{formatTime((track.analysis.hook_detection.best_segment?.start || 0) + 15)}
									</Badge>
								</div>
								{#if track.analysis.hook_detection.factors}
									<div class="space-y-1">
										<div class="flex justify-between text-xs">
											<span class="text-gray-600">Repetition</span>
											<span class="font-semibold">{Math.round(track.analysis.hook_detection.factors.repetition_score * 100)}%</span>
										</div>
										<div class="flex justify-between text-xs">
											<span class="text-gray-600">Energy</span>
											<span class="font-semibold">{Math.round(track.analysis.hook_detection.factors.energy_peak * 100)}%</span>
										</div>
										<div class="flex justify-between text-xs">
											<span class="text-gray-600">Position</span>
											<span class="font-semibold">{Math.round(track.analysis.hook_detection.factors.position_score * 100)}%</span>
										</div>
									</div>
								{/if}
							</div>
						{/if}

						<!-- Actions -->
						<div class="flex gap-2">
							<Button href={`/tracks/${track.id}`} variant="outline" size="sm" class="flex-1">
								<ArrowRight class="w-4 h-4 mr-1" />
								View Full Analysis
							</Button>
							<Button 
								variant="outline" 
								size="sm"
								onclick={(e) => {
									e.stopPropagation();
									copyHookTimestamp(track);
								}}
							>
								<Copy class="w-4 h-4" />
							</Button>
						</div>
					</div>
				</Card>
			{/each}
		</div>

		{#if filteredTracks.length === 0}
			<InsightCard
				type="info"
				message="No tracks match your filter criteria. Try adjusting the minimum hook score."
			/>
		{/if}
	{/if}
</div>

