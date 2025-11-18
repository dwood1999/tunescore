<script lang="ts">
	let { releases } = $props<{ releases: any[] }>();
	
	function formatReleaseDate(dateStr: string): string {
		const date = new Date(dateStr);
		return date.toLocaleDateString('en-US', { 
			month: 'short', 
			day: 'numeric',
			year: 'numeric'
		});
	}
	
	function getYouTubeSearchUrl(albumTitle: string, artist: string): string {
		const query = encodeURIComponent(`${albumTitle} ${artist}`);
		return `https://www.youtube.com/results?search_query=${query}`;
	}
	
	function getSpotifySearchUrl(albumTitle: string, artist: string): string {
		const query = encodeURIComponent(`${albumTitle} ${artist}`);
		return `https://open.spotify.com/search/${query}`;
	}
</script>

<div class="bg-white rounded-lg shadow-sm">
	<div class="p-6 border-b border-gray-200">
		<h2 class="text-2xl font-bold text-gray-900">
			🎵 New Releases
		</h2>
		<p class="text-gray-600 mt-1">
			{releases.length > 0 
				? `${releases.length} releases from the past 7 days`
				: 'No releases yet'}
		</p>
	</div>

	{#if releases.length === 0}
		<div class="p-12 text-center text-gray-500">
			<p class="text-lg">No new releases available yet.</p>
			<p class="text-sm mt-2">Releases will be updated automatically every 24 hours.</p>
		</div>
	{:else}
		<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
			{#each releases as release}
				<div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
					{#if release.notable}
						<div class="mb-2">
							<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
								⭐ Notable
							</span>
						</div>
					{/if}
					
					<h3 class="font-semibold text-gray-900 mb-1 text-lg">
						{release.album_title}
					</h3>
					
					<p class="text-gray-700 mb-2">
						{release.artist}
					</p>
					
					<div class="flex items-center justify-between text-sm text-gray-600">
						<span>{formatReleaseDate(release.release_date)}</span>
						{#if release.genre}
							<span class="px-2 py-1 bg-gray-100 rounded text-xs">
								{release.genre}
							</span>
						{/if}
					</div>
					
					{#if release.label}
						<p class="text-xs text-gray-500 mt-2">
							{release.label}
						</p>
					{/if}
					
					<!-- Listen Links -->
					<div class="mt-4 flex items-center space-x-3">
						<a 
							href={getSpotifySearchUrl(release.album_title, release.artist)}
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex items-center px-3 py-1.5 border border-green-600 text-green-600 hover:bg-green-50 rounded-md transition-colors text-sm font-medium"
							title="Listen on Spotify"
						>
							<svg class="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
							</svg>
							Spotify
						</a>
						<a 
							href={getYouTubeSearchUrl(release.album_title, release.artist)}
							target="_blank"
							rel="noopener noreferrer"
							class="inline-flex items-center px-3 py-1.5 border border-red-600 text-red-600 hover:bg-red-50 rounded-md transition-colors text-sm font-medium"
							title="Search on YouTube"
						>
							<svg class="w-4 h-4 mr-1.5" fill="currentColor" viewBox="0 0 24 24">
								<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
							</svg>
							YouTube
						</a>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

