<script lang="ts">
	let { news } = $props<{ news: any[] }>();
	
	const categoryColors: Record<string, string> = {
		'M&A': 'bg-purple-900/50 text-purple-200 border-purple-700',
		'Signings': 'bg-blue-900/50 text-blue-200 border-blue-700',
		'Platform': 'bg-green-900/50 text-green-200 border-green-700',
		'Legal': 'bg-red-900/50 text-red-200 border-red-700',
		'Tech': 'bg-yellow-900/50 text-yellow-200 border-yellow-700',
		'Market': 'bg-indigo-900/50 text-indigo-200 border-indigo-700'
	};
	
	function getCategoryColor(category: string): string {
		return categoryColors[category] || 'bg-gray-700 text-gray-300 border-gray-600';
	}
	
	function formatTimeAgo(dateStr: string): string {
		const date = new Date(dateStr);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
		const diffDays = Math.floor(diffHours / 24);
		
		if (diffHours < 1) return 'Just now';
		if (diffHours < 24) return `${diffHours}h ago`;
		if (diffDays === 1) return '1d ago';
		return `${diffDays}d ago`;
	}
</script>

<div class="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden h-full backdrop-blur-sm flex flex-col">
	<div class="p-6 border-b border-gray-700 bg-gray-800/80">
		<h2 class="text-xl font-bold text-white flex items-center">
			<span class="mr-2">📰</span> Industry News
		</h2>
	</div>

	{#if news.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No news available yet.</p>
		</div>
	{:else}
		<div class="divide-y divide-gray-700/50 overflow-y-auto max-h-[600px] scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent">
			{#each news as article}
				<article class="p-5 hover:bg-white/5 transition-colors group">
					<div class="flex items-start justify-between mb-2">
						<div class="flex-1 pr-4">
							<div class="flex items-center space-x-2 mb-2">
								<span class="text-xs font-medium text-blue-400 uppercase tracking-wider">
									{article.source}
								</span>
								<span class="text-gray-600 text-xs">•</span>
								<span class="text-xs text-gray-500 whitespace-nowrap">
									{formatTimeAgo(article.published_at)}
								</span>
							</div>
							<h3 class="text-base font-semibold text-gray-100 mb-2 leading-snug group-hover:text-blue-400 transition-colors">
								<a 
									href={article.url} 
									target="_blank" 
									rel="noopener noreferrer"
								>
									{article.title}
								</a>
							</h3>
						</div>
						
						{#if article.category}
							<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border {getCategoryColor(article.category)}">
								{article.category}
							</span>
						{/if}
					</div>
					
					{#if article.summary}
						<p class="text-sm text-gray-400 mb-3 leading-relaxed line-clamp-2">
							{article.summary}
						</p>
					{/if}
					
					{#if article.impact_score}
						<div class="flex items-center space-x-3 text-[10px] text-gray-500 bg-gray-900/30 py-1.5 px-2 rounded-md w-fit">
							<span class="opacity-60 uppercase tracking-wide mr-1">Impact:</span>
							<span title="Creator Impact" class="flex items-center text-gray-400"><span class="mr-1">🎨</span> {article.impact_score.creator}</span>
							<span title="Developer Impact" class="flex items-center text-gray-400"><span class="mr-1">🔍</span> {article.impact_score.developer}</span>
							<span title="Monetizer Impact" class="flex items-center text-gray-400"><span class="mr-1">💼</span> {article.impact_score.monetizer}</span>
						</div>
					{/if}
				</article>
			{/each}
		</div>
	{/if}
</div>
