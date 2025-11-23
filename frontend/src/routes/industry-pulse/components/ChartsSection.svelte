<script lang="ts">
	let { charts } = $props<{ charts: any[] }>();
	
	function getMovementIcon(movement: number | null): string {
		if (!movement) return '●';
		return movement > 0 ? '▲' : movement < 0 ? '▼' : '●';
	}
	
	function getMovementColor(movement: number | null): string {
		if (!movement) return 'text-gray-400';
		return movement > 0 ? 'text-green-400' : movement < 0 ? 'text-red-400' : 'text-gray-400';
	}
	
	function getYouTubeSearchUrl(trackTitle: string, artist: string): string {
		const query = encodeURIComponent(`${trackTitle} ${artist}`);
		return `https://www.youtube.com/results?search_query=${query}`;
	}
	
	function getSpotifySearchUrl(trackTitle: string, artist: string): string {
		const query = encodeURIComponent(`${trackTitle} ${artist}`);
		return `https://open.spotify.com/search/${query}`;
	}
</script>

<div class="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden h-full backdrop-blur-sm">
	<div class="p-6 border-b border-gray-700 bg-gray-800/80">
		<div class="flex items-center justify-between">
			<h2 class="text-xl font-bold text-white flex items-center">
				<span class="mr-2">🔥</span> Global Charts
			</h2>
			<span class="text-xs text-gray-400 bg-gray-700 px-2 py-1 rounded-full">Spotify Top 50</span>
		</div>
	</div>

	{#if charts.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No chart data available yet.</p>
			<p class="text-sm mt-2 opacity-70">Charts update daily.</p>
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full">
				<thead class="bg-gray-900/50 border-b border-gray-700">
					<tr>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider w-16">Rank</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Track</th>
						<th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider w-24">Move</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-700/50">
					{#each charts as chart, idx}
						<tr class="hover:bg-white/5 transition-colors group">
							<td class="px-4 py-3 whitespace-nowrap">
								<div class="text-sm font-bold text-gray-300 group-hover:text-white">
									#{chart.position}
								</div>
							</td>
							<td class="px-4 py-3">
								<div class="flex flex-col">
									<span class="text-sm font-medium text-gray-200 group-hover:text-white truncate max-w-[180px]">{chart.track_title}</span>
									<span class="text-xs text-gray-500 truncate max-w-[180px]">{chart.artist}</span>
								</div>
							</td>
							<td class="px-4 py-3 whitespace-nowrap text-right">
								<span class="inline-flex items-center text-sm font-medium {getMovementColor(chart.movement)}">
									<span class="mr-1 text-[10px]">{getMovementIcon(chart.movement)}</span>
									{chart.movement ? Math.abs(chart.movement) : '—'}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
