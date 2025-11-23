<script lang="ts">
  import { onMount } from 'svelte';
  import { Music, TrendingUp, BarChart3, Search, Zap, Sparkles } from 'lucide-svelte';
  import Button from '$lib/components/ui/button.svelte';
  import Badge from '$lib/components/ui/badge.svelte';
  import Card from '$lib/components/ui/card.svelte';

  const workspaces = [
    {
      id: 'creator',
      title: 'Creator Workspace',
      description: 'Sonic & Lyrical Genome, RIYL recommendations, Hook Lab analysis for artists.',
      features: ['Hook Lab', 'RIYL Discovery', 'Audience DNA', 'Upload & Analyze'],
      href: '/dashboard',
      color: 'from-blue-500 to-purple-500'
    },
    {
      id: 'developer',
      title: 'Developer (A&R) Hub',
      description: 'Talent Discovery, Breakout Score, Collaboration Lab for A&R managers.',
      features: ['Talent Discovery', 'Breakout Scores', 'Artist Comparison', 'Trend Analysis'],
      href: '/talent-discovery',
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'monetizer',
      title: 'Monetizer Intelligence',
      description: 'Catalog Valuation, Global Resonance, Sync Licensing for executives.',
      features: ['Catalog Valuation', 'Global Resonance', 'Sync Licensing', 'ROI Tracking'],
      href: '/catalog',
      color: 'from-emerald-500 to-teal-500'
    },
  ];
</script>

<div class="min-h-screen">
  <!-- Hero Section -->
  <section
    aria-labelledby="hero-heading"
    class="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden bg-richBlack dark"
  >
    <!-- Animated background gradient -->
    <div
      class="absolute inset-0 bg-gradient-to-br from-richBlack via-richBlack to-deepBronze/30"
      aria-hidden="true"
    ></div>

    <!-- Animated grid pattern -->
    <div class="absolute inset-0 opacity-10" aria-hidden="true">
      <div
        class="absolute inset-0 animate-pulse"
        style="background-image: radial-gradient(circle at 2px 2px, rgba(209, 202, 152, 0.2) 1px, transparent 0); background-size: 40px 40px;"
      ></div>
    </div>

    <!-- Floating accent elements -->
    <div
      class="absolute top-20 right-10 w-64 h-64 bg-sage rounded-full blur-3xl opacity-10"
      style="animation: float 6s ease-in-out infinite;"
      aria-hidden="true"
    ></div>
    <div
      class="absolute bottom-20 left-10 w-96 h-96 bg-deepBronze rounded-full blur-3xl opacity-8"
      style="animation: float 8s ease-in-out infinite; animation-delay: 1s;"
      aria-hidden="true"
    ></div>

    <div class="relative container mx-auto max-w-6xl">
      <div class="max-w-5xl">
        <div class="mb-6">
          <Badge
            variant="secondary"
            class="animate-pulse shadow-lg shadow-sage/20 uppercase tracking-[0.3em] text-xs"
          >
            <Sparkles class="w-3 h-3 mr-2 inline" aria-hidden="true" />
            Bloomberg Terminal for Music Industry
          </Badge>
        </div>

        <h1
          id="hero-heading"
          class="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-white leading-tight mb-6 font-serif"
        >
          Transform music discovery with AI-powered intelligence
        </h1>

        <div
          class="inline-flex flex-wrap items-center gap-3 bg-white/10 border border-white/20 rounded-full px-6 py-2 text-sm uppercase tracking-wide text-white/90 mb-6"
        >
          <span class="font-semibold text-sage">Only platform</span>
          <span class="text-white/70">purpose-built for artists • A&R • executives</span>
        </div>

        <p class="text-xl md:text-2xl text-gray-300 mb-6 leading-relaxed max-w-3xl">
          TuneScore orchestrates heavy AI intelligence across sonic features, lyrical sentiment, market
          data, and streaming insights — returning a single source of truth for music industry decisions.
        </p>

        <div class="grid gap-4 sm:grid-cols-3 mb-8">
          {#each workspaces as workspace (workspace.id)}
            <a
              href={workspace.href}
              class="bg-white/10 border border-white/10 hover:border-sage/50 rounded-xl p-5 text-sm text-gray-100 flex flex-col gap-3 transition-all hover:bg-white/15 hover:scale-105 group"
            >
              <span class="bg-sage/20 text-sage px-3 py-1 rounded-full text-xs font-semibold w-fit group-hover:bg-sage/30"
                >{workspace.title}</span
              >
              <span class="text-white/90">{workspace.description}</span>
              <div class="mt-2 flex flex-wrap gap-1">
                {#each workspace.features.slice(0, 2) as feature}
                  <span class="text-xs text-white/60 bg-white/5 px-2 py-1 rounded">• {feature}</span>
                {/each}
              </div>
              <span class="text-sage text-xs font-semibold mt-auto group-hover:underline">
                Explore →
              </span>
            </a>
          {/each}
        </div>

        <p class="text-lg text-gray-200 mb-10 leading-relaxed max-w-3xl">
          Comprehensive audio analysis. Predictive breakout scores. Semantic RIYL recommendations. TuneScore
          is the intelligence infrastructure powering the music industry's next generation.
        </p>

        <div class="flex flex-col sm:flex-row gap-4">
          <Button
            size="lg"
            href="/upload"
            class="group relative overflow-hidden shadow-xl shadow-sage/20 hover:shadow-2xl hover:shadow-sage/30 transition-all duration-300"
          >
            <span class="relative z-10 flex items-center gap-2">
              <Zap class="w-4 h-4 group-hover:animate-pulse" />
              Upload Your Track
            </span>
            <div
              class="absolute inset-0 bg-gradient-to-r from-sage to-deepBronze opacity-0 group-hover:opacity-20 transition-opacity duration-300"
            ></div>
          </Button>
          <Button
            size="lg"
            variant="outline"
            href="/dashboard"
            class="border-white/20 text-white hover:bg-white/10 hover:border-sage/50 transition-all duration-300 group"
          >
            View Dashboard
          </Button>
        </div>
      </div>
    </div>
  </section>

  <!-- Features Section -->
  <section class="py-20 px-4 sm:px-6 lg:px-8 bg-background">
    <div class="container mx-auto max-w-7xl">
      <div class="text-center mb-12">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Powerful Features for Every Musician</h2>
        <p class="text-xl text-muted-foreground max-w-2xl mx-auto">
          From independent artists to major labels, TuneScore delivers the insights you need to make
          data-driven decisions.
        </p>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        <Card class="p-6 hover:shadow-lg transition-shadow">
          <BarChart3 class="h-12 w-12 text-primary mb-4" />
          <h3 class="text-xl font-semibold mb-2">Sonic & Lyrical Genome</h3>
          <p class="text-muted-foreground">
            Comprehensive audio and lyrics analysis with tempo, key, energy, sentiment arc, hook detection,
            and more.
          </p>
        </Card>

        <Card class="p-6 hover:shadow-lg transition-shadow">
          <TrendingUp class="h-12 w-12 text-primary mb-4" />
          <h3 class="text-xl font-semibold mb-2">A&R Intelligence</h3>
          <p class="text-muted-foreground">
            Predictive breakout scores, talent discovery, career trajectory forecasting, and market
            positioning analysis.
          </p>
        </Card>

        <Card class="p-6 hover:shadow-lg transition-shadow">
          <Search class="h-12 w-12 text-primary mb-4" />
          <h3 class="text-xl font-semibold mb-2">RIYL Recommendations</h3>
          <p class="text-muted-foreground">
            Semantic search and "Recommended If You Like" powered by AI embeddings and cosine similarity
            matching.
          </p>
        </Card>
      </div>
    </div>
  </section>
</div>

<style>
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes float {
    0%,
    100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(20px);
    }
  }

  /* Respect prefers-reduced-motion */
  @media (prefers-reduced-motion: reduce) {
    * {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
</style>


