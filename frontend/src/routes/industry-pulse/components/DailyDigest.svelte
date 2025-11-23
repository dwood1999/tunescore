<script lang="ts">
	let { digest } = $props<{ digest: any }>();
	
	const tiers = [
		{ key: 'creator', label: 'Creators', icon: '🎨', color: 'blue' },
		{ key: 'developer', label: 'A&R', icon: '🔍', color: 'green' },
		{ key: 'monetizer', label: 'Execs', icon: '💼', color: 'purple' }
	];
	
	// Convert markdown-style links [text](url) to HTML
	function renderLinks(text: string): string {
		// Match [text](url) pattern
		return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="underline hover:text-blue-200 transition-colors">$1</a>');
	}
</script>

<div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 mb-8 text-white">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-2xl font-bold">Daily Digest</h2>
		<span class="text-sm opacity-90">
			{new Date(digest.digest_date).toLocaleDateString('en-US', { 
				weekday: 'long', 
				year: 'numeric', 
				month: 'long', 
				day: 'numeric' 
			})}
		</span>
	</div>

	<div class="text-lg mb-6 leading-relaxed opacity-95">
		{@html renderLinks(digest.summary_text)}
	</div>

	{#if digest.key_highlights}
		<div class="grid md:grid-cols-3 gap-4">
			{#each tiers as tier}
				{#if digest.key_highlights[tier.key]?.length > 0}
					<div class="bg-white/10 backdrop-blur-sm rounded-lg p-4">
						<h3 class="font-semibold mb-3 flex items-center">
							<span class="mr-2 text-xl">{tier.icon}</span>
							{tier.label}
						</h3>
						<ul class="space-y-2 text-sm">
							{#each digest.key_highlights[tier.key] as highlight}
								<li class="flex items-start">
									<span class="mr-2">•</span>
									<span class="opacity-90">{@html renderLinks(highlight)}</span>
								</li>
							{/each}
						</ul>
					</div>
				{/if}
			{/each}
		</div>
	{/if}

	{#if digest.cost}
		<div class="mt-4 text-xs opacity-75 text-right">
			AI-generated • Cost: ${digest.cost.toFixed(4)}
		</div>
	{/if}
</div>

