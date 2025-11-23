<script lang="ts">
	let { releases } = $props<{ releases: any[] }>();
	
	function formatReleaseDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { 
			month: 'short', 
			day: 'numeric'
		});
	}
	
	function getSpotifySearchUrl(albumTitle: string, artist: string): string {
		const query = encodeURIComponent(`${albumTitle} ${artist}`);
		return `https://open.spotify.com/search/${query}`;
	}
	
	function getNotableReason(release: any): string {
		// Check extra_data for notable reasons
		if (release.extra_data?.notable_reason) {
			return release.extra_data.notable_reason;
		}
		
		// Check for first_day_streams
		if (release.first_day_streams && release.first_day_streams > 1000000) {
			return 'Viral Debut';
		}
		
		// Check for indie success indicators
		if (release.label && (release.label.toLowerCase().includes('independent') || release.label.toLowerCase().includes('indie'))) {
			return 'Indie Success';
		}
		
		// Check for genre-specific indicators
		if (release.genre && (release.genre.toLowerCase().includes('bedroom') || release.genre.toLowerCase().includes('lo-fi'))) {
			return 'DIY Breakthrough';
		}
		
		// Default
		return 'Major Artist';
	}
</script>

<div class="bg-gray-800/50 border border-gray-700 rounded-xl overflow-hidden backdrop-blur-sm">
	<div class="p-6 border-b border-gray-700 bg-gray-800/80">
		<h2 class="text-xl font-bold text-white flex items-center">
			<span class="mr-2">🎵</span> New Releases
		</h2>
	</div>

	{#if releases.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No new releases available yet.</p>
		</div>
	{:else}
		<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-4 p-6">
			{#each releases as release}
				<a 
					href={getSpotifySearchUrl(release.album_title, release.artist)}
					target="_blank"
					rel="noopener noreferrer"
					class="group block bg-gray-900/40 border border-gray-700/50 hover:border-gray-600 hover:bg-gray-800 rounded-lg p-4 transition-all"
				>
					<div class="flex justify-between items-start mb-2">
						{#if release.notable}
							<span 
								class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-yellow-900/30 text-yellow-500 border border-yellow-900/50 cursor-help"
								title={getNotableReason(release)}
							>
								⭐ {getNotableReason(release)}
							</span>
						{:else}
							<span></span>
						{/if}
						<span class="text-[10px] text-gray-500">{formatReleaseDate(release.release_date)}</span>
					</div>
					
					<h3 class="font-semibold text-gray-200 mb-1 text-sm truncate group-hover:text-white transition-colors">
						{release.album_title}
					</h3>
					
					<p class="text-gray-400 text-xs truncate mb-3">
						{release.artist}
					</p>
					
					<div class="flex items-center justify-between mt-auto">
						{#if release.genre}
							<span class="px-1.5 py-0.5 bg-gray-800 rounded text-[10px] text-gray-500">
								{release.genre}
							</span>
						{/if}
						<span class="text-[10px] text-green-500 opacity-0 group-hover:opacity-100 transition-opacity flex items-center">
							Play <svg class="w-3 h-3 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
						</span>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
