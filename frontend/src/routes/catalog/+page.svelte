<script lang="ts">
	import { onMount } from 'svelte';
	import { 
		DollarSign, TrendingUp, Music, Users, Award, 
		RefreshCw, ArrowLeft, Sparkles, Target, BarChart3,
		FileText, Check, X
	} from 'lucide-svelte';
	import Badge from '$lib/components/ui/badge.svelte';
	import Button from '$lib/components/ui/button.svelte';

	let valuation = $state<any>(null);
	let topCollaborators = $state<any[]>([]);
	let trackCredits = $state<any[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let calculatingValuation = $state(false);

	// Collaboration finder
	let collaboratorA = $state('');
	let collaboratorB = $state('');
	let synergy = $state<any>(null);
	let analyzingSynergy = $state(false);

	onMount(async () => {
		try {
			const [valuationRes, collaboratorsRes, creditsRes] = await Promise.allSettled([
				fetch('/api/v1/catalog/valuation'),
				fetch('/api/v1/catalog/top-collaborators?limit=10'),
				fetch('/api/v1/catalog/credits?limit=20')
			]);

			if (valuationRes.status === 'fulfilled' && valuationRes.value.ok) {
				valuation = await valuationRes.value.json();
			}

			if (collaboratorsRes.status === 'fulfilled' && collaboratorsRes.value.ok) {
				topCollaborators = await collaboratorsRes.value.json();
			}

			if (creditsRes.status === 'fulfilled' && creditsRes.value.ok) {
				trackCredits = await creditsRes.value.json();
			}

		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load catalog data';
		} finally {
			loading = false;
		}
	});

	async function calculateValuation() {
		calculatingValuation = true;
		try {
			const response = await fetch('/api/v1/catalog/calculate-valuation', {
				method: 'POST',
			});
			
			if (!response.ok) {
				throw new Error('Failed to calculate valuation');
			}
			
			valuation = await response.json();
		} catch (e) {
			console.error('Failed to calculate valuation:', e);
			alert('Failed to calculate valuation.');
		} finally {
			calculatingValuation = false;
		}
	}

	async function analyzeSynergy() {
		if (!collaboratorA || !collaboratorB) {
			alert('Please enter both collaborator names');
			return;
		}

		analyzingSynergy = true;
		try {
			const response = await fetch(
				`/api/v1/catalog/analyze-collaboration?collaborator_a=${encodeURIComponent(collaboratorA)}&collaborator_b=${encodeURIComponent(collaboratorB)}`
			);
			
			if (!response.ok) {
				throw new Error('Failed to analyze collaboration');
			}
			
			synergy = await response.json();
		} catch (e) {
			console.error('Failed to analyze synergy:', e);
			alert('Failed to analyze collaboration.');
		} finally {
			analyzingSynergy = false;
		}
	}

	function formatCurrency(value: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(value);
	}

	function getSynergyColor(score: number): string {
		if (score >= 80) return 'text-green-600 bg-green-50 border-green-200';
		if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200';
		if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
		return 'text-orange-600 bg-orange-50 border-orange-200';
	}
</script>

<div class="container mx-auto px-4 py-8 max-w-7xl">
	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
			<p class="mt-4 text-muted-foreground">Loading catalog intelligence...</p>
		</div>
	{:else if error}
		<div class="text-center py-12">
			<p class="text-destructive mb-4">{error}</p>
			<a href="/dashboard" class="text-primary underline">← Back to Dashboard</a>
		</div>
	{:else}
		<!-- Header -->
		<div class="mb-8">
			<a href="/dashboard" class="text-primary hover:underline mb-4 inline-flex items-center gap-2">
				<ArrowLeft class="h-4 w-4" />
				Back to Dashboard
			</a>
			
			<h1 class="text-4xl font-bold mt-4">Catalog Intelligence</h1>
			<p class="text-lg text-muted-foreground mt-2">
				DCF-based valuation, credit tracking, and collaboration insights
			</p>
		</div>

		<!-- Catalog Valuation (Hero Card) -->
		<div class="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl p-8 mb-8 text-white shadow-xl">
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-2">
					<DollarSign class="h-6 w-6" />
					<h2 class="text-2xl font-bold">Estimated Catalog Value</h2>
				</div>
				<Button
					variant="secondary"
					size="sm"
					onclick={calculateValuation}
					disabled={calculatingValuation}
					class="bg-white/20 hover:bg-white/30 text-white border-white/30"
				>
					<RefreshCw class="h-4 w-4 mr-2 {calculatingValuation ? 'animate-spin' : ''}" />
					{calculatingValuation ? 'Calculating...' : 'Recalculate'}
				</Button>
			</div>

			{#if valuation}
				<div class="grid md:grid-cols-4 gap-6">
					<div>
						<div class="text-7xl font-bold mb-2">
							{formatCurrency(valuation.estimated_value || 0)}
						</div>
						<div class="text-lg opacity-90 mb-4">
							Estimated Worth
						</div>
						<div class="text-sm opacity-75">
							Based on {formatCurrency(valuation.annual_revenue || 0)} annual revenue × {valuation.valuation_multiple?.toFixed(1)}x multiple
						</div>
					</div>

					<div class="md:col-span-3 grid grid-cols-3 gap-4">
						<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
							<div class="text-sm opacity-75 mb-1">Streaming Revenue</div>
							<div class="text-2xl font-bold">
								{formatCurrency(valuation.revenue_breakdown?.streaming || 0)}
							</div>
							<div class="text-xs opacity-60 mt-1">per year</div>
						</div>

						<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
							<div class="text-sm opacity-75 mb-1">Sync Revenue</div>
							<div class="text-2xl font-bold">
								{formatCurrency(valuation.revenue_breakdown?.sync || 0)}
							</div>
							<div class="text-xs opacity-60 mt-1">per year</div>
						</div>

						<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
							<div class="text-sm opacity-75 mb-1">Performance Revenue</div>
							<div class="text-2xl font-bold">
								{formatCurrency(valuation.revenue_breakdown?.performance || 0)}
							</div>
							<div class="text-xs opacity-60 mt-1">per year</div>
						</div>
					</div>
				</div>

				<!-- Valuation Factors -->
				{#if valuation.valuation_factors}
					<div class="mt-6 pt-6 border-t border-white/20">
						<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
							<div class="text-center">
								<div class="text-3xl font-bold mb-1">
									{valuation.valuation_factors.total_tracks || 0}
								</div>
								<div class="text-sm opacity-75">Total Tracks</div>
							</div>
							<div class="text-center">
								<div class="text-3xl font-bold mb-1">
									{valuation.valuation_factors.hit_tracks || 0}
								</div>
								<div class="text-sm opacity-75">Hit Tracks</div>
							</div>
							<div class="text-center">
								<div class="text-3xl font-bold mb-1">
									{valuation.valuation_factors.avg_tunescore?.toFixed(0) || 'N/A'}
								</div>
								<div class="text-sm opacity-75">Avg TuneScore</div>
							</div>
							<div class="text-center">
								<div class="text-3xl font-bold mb-1">
									{valuation.confidence ? (valuation.confidence * 100).toFixed(0) : 'N/A'}%
								</div>
								<div class="text-sm opacity-75">Confidence</div>
							</div>
						</div>
					</div>
				{/if}
			{:else}
				<div class="text-center py-8">
					<DollarSign class="h-16 w-16 mx-auto mb-4 opacity-50" />
					<p class="text-xl mb-4">No valuation calculated yet</p>
					<Button
						variant="secondary"
						size="lg"
						onclick={calculateValuation}
						disabled={calculatingValuation}
						class="bg-white/20 hover:bg-white/30 text-white border-white/30"
					>
						<Sparkles class="h-4 w-4 mr-2" />
						Calculate Catalog Value
					</Button>
				</div>
			{/if}
		</div>

		<!-- Top Collaborators -->
		<div class="border rounded-lg p-6 mb-8 bg-white dark:bg-gray-900">
			<div class="flex items-center gap-2 mb-4">
				<Users class="h-5 w-5 text-primary" />
				<h2 class="text-xl font-semibold">Top Collaborators</h2>
				<Badge variant="secondary" class="ml-auto">
					{topCollaborators.length} collaborators
				</Badge>
			</div>

			{#if topCollaborators.length > 0}
				<div class="space-y-3">
					{#each topCollaborators as collab}
						<div class="flex items-center justify-between p-4 hover:bg-secondary/50 rounded-lg transition-colors border">
							<div class="flex-1">
								<div class="font-semibold text-lg mb-1">{collab.name}</div>
								<div class="flex items-center gap-4 text-sm text-muted-foreground">
									<span>{collab.role || 'Collaborator'}</span>
									<span class="flex items-center gap-1">
										<Music class="h-3 w-3" />
										{collab.total_tracks || 0} tracks
									</span>
									{#if collab.avg_tunescore}
										<span class="flex items-center gap-1">
											<Award class="h-3 w-3" />
											Avg Score: {collab.avg_tunescore.toFixed(0)}
										</span>
									{/if}
								</div>
								{#if collab.genres && collab.genres.length > 0}
									<div class="flex gap-1 mt-2">
										{#each collab.genres.slice(0, 3) as genre}
											<Badge variant="outline" class="text-xs">{genre}</Badge>
										{/each}
									</div>
								{/if}
							</div>
							{#if collab.synergy_score !== undefined}
								<div class="text-right ml-4">
									<div class="text-3xl font-bold text-primary mb-1">
										{collab.synergy_score}
									</div>
									<div class="text-xs text-muted-foreground">Synergy Score</div>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<div class="text-center py-8 text-muted-foreground">
					<Users class="h-12 w-12 mx-auto mb-3 opacity-30" />
					<p>No collaborators tracked yet</p>
				</div>
			{/if}
		</div>

		<!-- Collaboration Finder -->
		<div class="border rounded-lg p-6 mb-8 bg-gradient-to-br from-violet-50 to-fuchsia-50 dark:from-violet-950/20 dark:to-fuchsia-950/20">
			<div class="flex items-center gap-2 mb-4">
				<Sparkles class="h-5 w-5 text-violet-600" />
				<h2 class="text-xl font-semibold">Collaboration Synergy Analyzer</h2>
			</div>
			
			<p class="text-sm text-muted-foreground mb-6">
				Predict the success potential of collaborations before they happen
			</p>

			<div class="grid md:grid-cols-2 gap-4 mb-4">
				<div>
					<label class="text-sm font-medium mb-2 block">Collaborator A</label>
					<input
						type="text"
						bind:value={collaboratorA}
						placeholder="e.g., Max Martin"
						class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
					/>
				</div>
				<div>
					<label class="text-sm font-medium mb-2 block">Collaborator B</label>
					<input
						type="text"
						bind:value={collaboratorB}
						placeholder="e.g., Taylor Swift"
						class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
					/>
				</div>
			</div>

			<Button
				variant="default"
				onclick={analyzeSynergy}
				disabled={analyzingSynergy || !collaboratorA || !collaboratorB}
				class="w-full md:w-auto"
			>
				<Target class="h-4 w-4 mr-2" />
				{analyzingSynergy ? 'Analyzing...' : 'Analyze Synergy'}
			</Button>

			<!-- Synergy Results -->
			{#if synergy}
				<div class="mt-6 p-6 border-2 rounded-xl {getSynergyColor(synergy.synergy_score)}">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-semibold">Collaboration Potential</h3>
						<div class="text-4xl font-bold">
							{synergy.synergy_score}/100
						</div>
					</div>

					<div class="grid md:grid-cols-3 gap-4 mb-4">
						<div>
							<div class="text-sm text-muted-foreground">Average TuneScore</div>
							<div class="text-2xl font-bold">{synergy.avg_tunescore?.toFixed(0)}</div>
						</div>
						<div>
							<div class="text-sm text-muted-foreground">Success Rate</div>
							<div class="text-2xl font-bold">{(synergy.success_rate * 100).toFixed(0)}%</div>
						</div>
						<div>
							<div class="text-sm text-muted-foreground">Past Tracks Together</div>
							<div class="text-2xl font-bold">{synergy.past_tracks_together || 0}</div>
						</div>
					</div>

					{#if synergy.genre_overlap && synergy.genre_overlap.length > 0}
						<div class="mb-4">
							<div class="text-sm text-muted-foreground mb-2">Genre Overlap:</div>
							<div class="flex flex-wrap gap-2">
								{#each synergy.genre_overlap as genre}
									<Badge>{genre}</Badge>
								{/each}
							</div>
						</div>
					{/if}

					<div class="p-4 bg-white dark:bg-gray-900 rounded-lg border">
						<div class="flex items-start gap-2">
							{#if synergy.synergy_score >= 75}
								<Check class="h-5 w-5 text-green-600 mt-0.5" />
								<div>
									<div class="font-semibold text-green-700 dark:text-green-400">
										{synergy.recommendation}
									</div>
									<p class="text-sm text-muted-foreground mt-1">
										This collaboration shows strong potential for commercial success
									</p>
								</div>
							{:else if synergy.synergy_score >= 50}
								<Target class="h-5 w-5 text-blue-600 mt-0.5" />
								<div>
									<div class="font-semibold text-blue-700 dark:text-blue-400">
										{synergy.recommendation}
									</div>
									<p class="text-sm text-muted-foreground mt-1">
										Moderate potential - consider genre fit and creative chemistry
									</p>
								</div>
							{:else}
								<X class="h-5 w-5 text-orange-600 mt-0.5" />
								<div>
									<div class="font-semibold text-orange-700 dark:text-orange-400">
										{synergy.recommendation}
									</div>
									<p class="text-sm text-muted-foreground mt-1">
										Historical data suggests lower probability of commercial success
									</p>
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Recent Credits -->
		<div class="border rounded-lg p-6 bg-white dark:bg-gray-900">
			<div class="flex items-center gap-2 mb-4">
				<FileText class="h-5 w-5 text-primary" />
				<h2 class="text-xl font-semibold">Recent Track Credits</h2>
			</div>

			{#if trackCredits.length > 0}
				<div class="space-y-4">
					{#each trackCredits as credit}
						<div class="border rounded-lg p-4 hover:bg-secondary/30 transition-colors">
							<div class="flex items-start justify-between mb-2">
								<div class="flex-1">
									<h3 class="font-semibold mb-1">{credit.track_title}</h3>
									<p class="text-sm text-muted-foreground">{credit.artist_name}</p>
								</div>
							</div>
							{#if credit.credits && credit.credits.length > 0}
								<div class="flex flex-wrap gap-2 mt-3">
									{#each credit.credits as contributor}
										<span class="inline-flex items-center gap-1 px-2.5 py-1 bg-secondary rounded-full text-xs">
											<Users class="h-3 w-3" />
											{contributor.contributor_name}
											{#if contributor.role}
												<span class="text-muted-foreground">({contributor.role})</span>
											{/if}
										</span>
									{/each}
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{:else}
				<div class="text-center py-8 text-muted-foreground">
					<FileText class="h-12 w-12 mx-auto mb-3 opacity-30" />
					<p>No credits tracked yet</p>
					<p class="text-sm mt-1">Credits will appear as tracks are analyzed</p>
				</div>
			{/if}
		</div>
	{/if}
</div>

