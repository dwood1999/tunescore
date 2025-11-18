<script lang="ts">
	let { charts } = $props<{ charts: any[] }>();
	
	function getMovementIcon(movement: number | null): string {
		if (!movement) return '●';
		return movement > 0 ? '▲' : movement < 0 ? '▼' : '●';
	}
	
	function getMovementColor(movement: number | null): string {
		if (!movement) return 'text-gray-400';
		return movement > 0 ? 'text-green-600' : movement < 0 ? 'text-red-600' : 'text-gray-400';
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

<div class="bg-white rounded-lg shadow-sm">
	<div class="p-6 border-b border-gray-200">
		<h2 class="text-2xl font-bold text-gray-900">
			🔥 Global Charts
		</h2>
		<p class="text-gray-600 mt-1">
			{charts.length > 0 
				? `Latest snapshot from ${new Date(charts[0].snapshot_date).toLocaleDateString()}`
				: 'No chart data available'}
		</p>
	</div>

	{#if charts.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No chart data available yet.</p>
			<p class="text-sm mt-2">Charts will be updated automatically every 24 hours.</p>
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full">
				<thead class="bg-gray-50 border-b border-gray-200">
					<tr>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
							Rank
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Track
						</th>
						<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
							Artist
						</th>
						<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
							Movement
						</th>
						<th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-24">
							Listen
						</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each charts as chart, idx}
						<tr class="hover:bg-gray-50 transition-colors">
							<td class="px-6 py-4 whitespace-nowrap">
								<div class="text-sm font-bold text-gray-900">
									#{chart.position}
								</div>
							</td>
							<td class="px-6 py-4">
								<div class="text-sm font-medium text-gray-900">
									{chart.track_title}
								</div>
							</td>
							<td class="px-6 py-4">
								<div class="text-sm text-gray-700">
									{chart.artist}
								</div>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-right">
								<span class="inline-flex items-center text-sm font-medium {getMovementColor(chart.movement)}">
									<span class="mr-1">{getMovementIcon(chart.movement)}</span>
									{chart.movement ? Math.abs(chart.movement) : '—'}
								</span>
							</td>
							<td class="px-6 py-4 whitespace-nowrap text-center">
								<div class="flex items-center justify-center space-x-2">
									<a 
										href={getSpotifySearchUrl(chart.track_title, chart.artist)}
										target="_blank"
										rel="noopener noreferrer"
										class="text-green-600 hover:text-green-700 transition-colors"
										title="Listen on Spotify"
									>
										<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
											<path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
										</svg>
									</a>
									<a 
										href={getYouTubeSearchUrl(chart.track_title, chart.artist)}
										target="_blank"
										rel="noopener noreferrer"
										class="text-red-600 hover:text-red-700 transition-colors"
										title="Search on YouTube"
									>
										<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
											<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
										</svg>
									</a>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

