<script lang="ts">
	let { news } = $props<{ news: any[] }>();
	
	const categoryColors: Record<string, string> = {
		'M&A': 'bg-purple-100 text-purple-800',
		'Signings': 'bg-blue-100 text-blue-800',
		'Platform': 'bg-green-100 text-green-800',
		'Legal': 'bg-red-100 text-red-800',
		'Tech': 'bg-yellow-100 text-yellow-800',
		'Market': 'bg-indigo-100 text-indigo-800'
	};
	
	function getCategoryColor(category: string): string {
		return categoryColors[category] || 'bg-gray-100 text-gray-800';
	}
	
	function formatTimeAgo(dateStr: string): string {
		const date = new Date(dateStr);
		const now = new Date();
		const diffMs = now.getTime() - date.getTime();
		const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
		const diffDays = Math.floor(diffHours / 24);
		
		if (diffHours < 1) return 'Just now';
		if (diffHours < 24) return `${diffHours}h ago`;
		if (diffDays === 1) return '1 day ago';
		return `${diffDays} days ago`;
	}
</script>

<div class="bg-white rounded-lg shadow-sm">
	<div class="p-6 border-b border-gray-200">
		<h2 class="text-2xl font-bold text-gray-900">
			📰 Industry News
		</h2>
		<p class="text-gray-600 mt-1">
			Latest updates from {news.length > 0 ? 'the past 7 days' : 'your sources'}
		</p>
	</div>

	{#if news.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No news articles available yet.</p>
			<p class="text-sm mt-2">News will be updated automatically every 4 hours.</p>
		</div>
	{:else}
		<div class="divide-y divide-gray-200">
			{#each news as article}
				<article class="p-6 hover:bg-gray-50 transition-colors">
					<div class="flex items-start justify-between mb-2">
						<div class="flex-1">
							<h3 class="text-lg font-semibold text-gray-900 mb-2">
								<a 
									href={article.url} 
									target="_blank" 
									rel="noopener noreferrer"
									class="hover:text-blue-600 transition-colors"
								>
									{article.title}
								</a>
							</h3>
						</div>
						<span class="ml-4 text-sm text-gray-500 whitespace-nowrap">
							{formatTimeAgo(article.published_at)}
						</span>
					</div>
					
					{#if article.summary}
						<p class="text-gray-700 mb-3 leading-relaxed">
							{article.summary}
						</p>
					{/if}
					
					<div class="flex items-center justify-between">
						<div class="flex items-center space-x-3">
							<span class="text-sm font-medium text-gray-600">
								{article.source}
							</span>
							
							{#if article.category}
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getCategoryColor(article.category)}">
									{article.category}
								</span>
							{/if}
						</div>
						
						{#if article.impact_score}
							<div class="flex items-center space-x-2 text-xs text-gray-500">
								<span title="Creator Impact">🎨 {article.impact_score.creator}/10</span>
								<span title="Developer Impact">🔍 {article.impact_score.developer}/10</span>
								<span title="Monetizer Impact">💼 {article.impact_score.monetizer}/10</span>
							</div>
						{/if}
					</div>
				</article>
			{/each}
		</div>
	{/if}
</div>

