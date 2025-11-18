<script lang="ts">
  import { onMount } from 'svelte';
  import { Music, Upload, TrendingUp, Star, Award, Zap, Heart, Sparkles, Target } from 'lucide-svelte';
  import { api } from '$lib/api/client';
  import Button from '$lib/components/ui/button.svelte';
  import Card from '$lib/components/ui/card.svelte';
  import Badge from '$lib/components/ui/badge.svelte';
  import { formatRelativeTime } from '$lib/utils';

  let tracks = $state<any[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let sortBy = $state<'score' | 'date' | 'title'>('score');
  let expandedTracks = $state<Set<number>>(new Set());

  onMount(async () => {
    try {
      tracks = await api.tracks.list();
      sortTracks();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load tracks';
      console.error('Failed to load tracks:', e);
    } finally {
      loading = false;
    }
  });

  function sortTracks() {
    if (sortBy === 'score') {
      tracks.sort((a, b) => {
        const scoreA = a.tunescore?.overall_score || 0;
        const scoreB = b.tunescore?.overall_score || 0;
        return scoreB - scoreA;
      });
    } else if (sortBy === 'date') {
      tracks.sort((a, b) => {
        const dateA = new Date(a.created_at).getTime();
        const dateB = new Date(b.created_at).getTime();
        return dateB - dateA;
      });
    } else if (sortBy === 'title') {
      tracks.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    }
  }

  function toggleExpanded(trackId: number, event: MouseEvent) {
    event.preventDefault();
    event.stopPropagation();
    const newSet = new Set(expandedTracks);
    if (newSet.has(trackId)) {
      newSet.delete(trackId);
    } else {
      newSet.add(trackId);
    }
    expandedTracks = newSet;
  }

  function getScoreColor(score: number): string {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  }

  function getScoreBgColor(score: number): string {
    if (score >= 80) return 'bg-green-100 border-green-300';
    if (score >= 60) return 'bg-blue-100 border-blue-300';
    if (score >= 40) return 'bg-yellow-100 border-yellow-300';
    return 'bg-red-100 border-red-300';
  }

  $effect(() => {
    if (tracks.length > 0) {
      sortTracks();
    }
  });
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-3xl font-bold mb-2">Dashboard</h1>
      <p class="text-muted-foreground">View and manage your tracks</p>
    </div>
    <Button href="/upload" size="lg">
      <Upload class="w-4 h-4 mr-2" />
      Upload Track
    </Button>
  </div>

  <!-- Loading State -->
  {#if loading}
    <div class="grid md:grid-cols-3 gap-6">
      {#each Array(3) as _}
        <Card class="p-6 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-1/4"></div>
        </Card>
      {/each}
    </div>
  <!-- Error State -->
  {:else if error}
    <Card class="p-8 text-center">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
        <svg
          class="w-8 h-8 text-red-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Failed to load tracks</h3>
      <p class="text-muted-foreground mb-4">{error}</p>
      <Button onclick={() => window.location.reload()}>Try Again</Button>
    </Card>
  <!-- Empty State -->
  {:else if tracks.length === 0}
    <Card class="p-12 text-center">
      <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
        <Music class="h-10 w-10 text-primary" />
      </div>
      <h3 class="text-xl font-semibold mb-2">No tracks uploaded yet</h3>
      <p class="text-muted-foreground mb-6 max-w-md mx-auto">
        Get started by uploading your first track to unlock powerful AI-powered insights about your music.
      </p>
      <Button href="/upload" size="lg">
        <Upload class="w-4 h-4 mr-2" />
        Upload Your First Track
      </Button>
    </Card>
  <!-- Tracks List -->
  {:else}
    <!-- Stats Summary -->
    <Card class="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-2">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <div>
          <div class="text-3xl font-bold text-primary mb-1">{tracks.length}</div>
          <div class="text-sm text-muted-foreground">Total Tracks</div>
        </div>
        <div>
          <div class="text-3xl font-bold text-primary mb-1">
            {tracks.filter(t => t.tunescore?.overall_score).length}
          </div>
          <div class="text-sm text-muted-foreground">Scored</div>
        </div>
        <div>
          <div class="text-3xl font-bold text-primary mb-1">
            {tracks.filter(t => t.tunescore?.overall_score).length > 0 
              ? Math.round(tracks.filter(t => t.tunescore?.overall_score).reduce((sum, t) => sum + (t.tunescore?.overall_score || 0), 0) / tracks.filter(t => t.tunescore?.overall_score).length)
              : 0}
          </div>
          <div class="text-sm text-muted-foreground">Avg Score</div>
        </div>
        <div>
          <div class="text-3xl font-bold text-primary mb-1">
            {tracks.filter(t => t.tunescore?.overall_score >= 80).length}
          </div>
          <div class="text-sm text-muted-foreground">Excellent (80+)</div>
        </div>
      </div>
    </Card>

    <!-- Sort Controls -->
    <div class="flex items-center gap-4">
      <span class="text-sm text-muted-foreground">Sort by:</span>
      <div class="flex gap-2">
        <Button
          variant={sortBy === 'score' ? 'default' : 'outline'}
          size="sm"
          onclick={() => { sortBy = 'score'; }}
        >
          <Star class="w-4 h-4 mr-1" />
          Score
        </Button>
        <Button
          variant={sortBy === 'date' ? 'default' : 'outline'}
          size="sm"
          onclick={() => { sortBy = 'date'; }}
        >
          Date
        </Button>
        <Button
          variant={sortBy === 'title' ? 'default' : 'outline'}
          size="sm"
          onclick={() => { sortBy = 'title'; }}
        >
          Title
        </Button>
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-6">
      {#each tracks as track (track.id)}
        <Card class="p-0 hover:shadow-lg transition-all border-2 hover:border-primary/50 overflow-hidden">
          <!-- Main Track Info (Clickable to view details) -->
          <a href="/tracks/{track.id}" class="block p-6 group">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-xl font-bold mb-1 group-hover:text-primary transition-colors">
                  {track.title || 'Untitled Track'}
                </h3>
                <p class="text-sm text-muted-foreground mb-3">
                  {track.artist_name || 'Unknown Artist'}
                </p>
                <div class="flex flex-wrap gap-2">
                  {#if track.genre}
                    <Badge variant="secondary">{track.genre}</Badge>
                  {/if}
                  {#if track.tunescore?.grade}
                    <Badge variant="default" class="font-semibold">
                      <Award class="w-3 h-3 mr-1" />
                      Grade {track.tunescore.grade}
                    </Badge>
                  {/if}
                  {#if track.created_at}
                    <Badge variant="outline">{formatRelativeTime(track.created_at)}</Badge>
                  {/if}
                </div>
              </div>
              {#if track.tunescore?.overall_score}
                <div class="flex-shrink-0 ml-6">
                  <div class="w-20 h-20 rounded-full {getScoreBgColor(track.tunescore.overall_score)} border-3 flex flex-col items-center justify-center shadow-md">
                    <div class="text-2xl font-bold {getScoreColor(track.tunescore.overall_score)}">
                      {Math.round(track.tunescore.overall_score)}
                    </div>
                    <div class="text-xs text-muted-foreground">/ 100</div>
                  </div>
                </div>
              {/if}
            </div>

            {#if track.tunescore?.insights}
              <div class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p class="text-sm text-blue-900 font-medium">
                  💡 {track.tunescore.insights[0] || 'Great potential!'}
                </p>
              </div>
            {/if}
          </a>

          <!-- Detailed Metrics (Always visible) -->
          {#if track.tunescore?.components}
            <div class="px-6 pb-4 space-y-3 border-t bg-gray-50/50">
              <div class="pt-4">
                <h4 class="text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-wide">Component Scores</h4>
                
                <!-- Production Quality -->
                <div class="mb-3">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="font-medium flex items-center gap-2">
                      <Sparkles class="w-4 h-4 text-blue-600" />
                      Production Quality
                    </span>
                    <span class="font-bold text-blue-600">
                      {Math.round(track.tunescore.components.production_quality.score)}/{track.tunescore.components.production_quality.max}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-blue-600 h-2 rounded-full transition-all"
                      style="width: {track.tunescore.components.production_quality.percentage}%"
                    ></div>
                  </div>
                </div>

                <!-- Musicality -->
                <div class="mb-3">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="font-medium flex items-center gap-2">
                      <Music class="w-4 h-4 text-purple-600" />
                      Musicality
                    </span>
                    <span class="font-bold text-purple-600">
                      {Math.round(track.tunescore.components.musicality.score)}/{track.tunescore.components.musicality.max}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-purple-600 h-2 rounded-full transition-all"
                      style="width: {track.tunescore.components.musicality.percentage}%"
                    ></div>
                  </div>
                </div>

                <!-- Lyrical Quality -->
                <div class="mb-3">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="font-medium flex items-center gap-2">
                      <Heart class="w-4 h-4 text-pink-600" />
                      Lyrical Quality
                    </span>
                    <span class="font-bold text-pink-600">
                      {Math.round(track.tunescore.components.lyrical_quality.score)}/{track.tunescore.components.lyrical_quality.max}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-pink-600 h-2 rounded-full transition-all"
                      style="width: {track.tunescore.components.lyrical_quality.percentage}%"
                    ></div>
                  </div>
                </div>

                <!-- Hook Potential -->
                <div class="mb-3">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="font-medium flex items-center gap-2">
                      <Zap class="w-4 h-4 text-green-600" />
                      Hook Potential
                    </span>
                    <span class="font-bold text-green-600">
                      {Math.round(track.tunescore.components.hook_potential.score)}/{track.tunescore.components.hook_potential.max}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-green-600 h-2 rounded-full transition-all"
                      style="width: {track.tunescore.components.hook_potential.percentage}%"
                    ></div>
                  </div>
                </div>

                <!-- Commercial Appeal -->
                <div class="mb-3">
                  <div class="flex items-center justify-between text-sm mb-1">
                    <span class="font-medium flex items-center gap-2">
                      <Target class="w-4 h-4 text-orange-600" />
                      Commercial Appeal
                    </span>
                    <span class="font-bold text-orange-600">
                      {Math.round(track.tunescore.components.commercial_appeal.score)}/{track.tunescore.components.commercial_appeal.max}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      class="bg-orange-600 h-2 rounded-full transition-all"
                      style="width: {track.tunescore.components.commercial_appeal.percentage}%"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          {/if}

          <!-- View Details Button -->
          <a href="/tracks/{track.id}" class="block px-6 py-3 bg-gray-100 hover:bg-gray-200 transition-colors border-t">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-gray-700">View Full Analysis</span>
              <TrendingUp class="w-4 h-4 text-gray-500" />
            </div>
          </a>
        </Card>
      {/each}
    </div>
  {/if}
</div>


