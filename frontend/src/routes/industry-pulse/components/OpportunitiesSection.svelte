<script lang="ts">
	let { opportunities = [], takeaway = "" } = $props<{ opportunities: any[], takeaway: string }>();
	
	const categoryIcons: Record<string, string> = {
		'sync': '🎬',
		'grant': '🏆',
		'tool': '🛠️',
		'marketing': '📈'
	};
	
	const categoryColors: Record<string, string> = {
		'sync': 'bg-purple-900/30 border-purple-700 text-purple-200',
		'grant': 'bg-yellow-900/30 border-yellow-700 text-yellow-200',
		'tool': 'bg-blue-900/30 border-blue-700 text-blue-200',
		'marketing': 'bg-green-900/30 border-green-700 text-green-200'
	};
	
	function getCategoryIcon(category: string): string {
		return categoryIcons[category] || '💡';
	}
	
	function getCategoryColor(category: string): string {
		return categoryColors[category] || 'bg-gray-800 border-gray-700 text-gray-300';
	}
</script>

<div class="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden backdrop-blur-sm">
	<div class="p-6 border-b border-gray-700 bg-gray-800/80">
		<h2 class="text-xl font-bold text-white flex items-center">
			<span class="mr-2">💡</span> Indie Opportunities
		</h2>
		<p class="text-sm text-gray-400 mt-1">Actionable items for self-publishing artists</p>
	</div>

	{#if takeaway}
		<div class="p-4 bg-gradient-to-r from-blue-900/40 to-purple-900/40 border-b border-gray-700">
			<div class="flex items-start">
				<span class="text-2xl mr-3">🎯</span>
				<div>
					<div class="text-xs font-semibold text-blue-300 uppercase tracking-wider mb-1">Today's Takeaway</div>
					<p class="text-sm text-gray-200 leading-relaxed">{takeaway}</p>
				</div>
			</div>
		</div>
	{/if}

	{#if opportunities.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No opportunities available yet.</p>
			<p class="text-sm mt-2 opacity-70">Check back daily for new opportunities.</p>
		</div>
	{:else}
		<div class="grid md:grid-cols-2 gap-4 p-6">
			{#each opportunities as opp}
				<div class="border {getCategoryColor(opp.category)} rounded-lg p-4 hover:bg-white/5 transition-all group">
					<div class="flex items-start mb-2">
						<span class="text-2xl mr-3">{getCategoryIcon(opp.category)}</span>
						<div class="flex-1">
							<h3 class="font-semibold text-gray-100 group-hover:text-white transition-colors">
								{opp.title}
							</h3>
							<span class="inline-block text-[10px] uppercase tracking-wider opacity-60 mt-1">
								{opp.category}
							</span>
						</div>
					</div>
					<p class="text-sm text-gray-400 leading-relaxed ml-11">
						{opp.description}
					</p>
				</div>
			{/each}
		</div>
	{/if}
</div>

