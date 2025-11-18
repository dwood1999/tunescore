<script lang="ts">
  import { onMount } from 'svelte';
  import { Music, TrendingUp, DollarSign, Sparkles, Check, ArrowRight, Zap } from 'lucide-svelte';
  import Button from '$lib/components/ui/button.svelte';
  import Card from '$lib/components/ui/card.svelte';
  import Input from '$lib/components/ui/input.svelte';
  import Label from '$lib/components/ui/label.svelte';
  import { toastStore } from '$lib/stores/toast';

  let email = '';
  let name = '';
  let useCase = '';
  let referralSource = '';
  let isSubmitting = false;
  let isSuccess = false;
  let waitlistCount = 0;

  onMount(async () => {
    // Fetch current waitlist count
    try {
      const response = await fetch('/api/v1/waitlist/count');
      if (response.ok) {
        const data = await response.json();
        waitlistCount = data.total;
      }
    } catch (error) {
      console.error('Failed to fetch waitlist count:', error);
    }
  });

  async function handleSubmit() {
    if (!email) {
      toastStore.error('Please enter your email address');
      return;
    }

    isSubmitting = true;

    try {
      const response = await fetch('/api/v1/waitlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          name: name || null,
          use_case: useCase || null,
          referral_source: referralSource || null,
        }),
      });

      if (response.ok) {
        isSuccess = true;
        waitlistCount += 1;
        toastStore.success("You're on the list! Check your email for next steps.");
      } else {
        const error = await response.json();
        toastStore.error(error.detail || 'Failed to join waitlist');
      }
    } catch (error) {
      toastStore.error('Network error. Please try again.');
    } finally {
      isSubmitting = false;
    }
  }

  const features = [
    {
      icon: Sparkles,
      title: 'Viral Hook Detection',
      description: 'AI finds your best 15-second clips for TikTok/Reels',
    },
    {
      icon: TrendingUp,
      title: 'Breakout Prediction',
      description: 'Know which tracks will blow up (7/14/28-day forecasts)',
    },
    {
      icon: DollarSign,
      title: 'Catalog Valuation',
      description: 'DCF model estimates your catalog\'s worth',
    },
    {
      icon: Zap,
      title: 'AI Pitch Generation',
      description: 'Professional marketing copy for $0.0017',
    },
    {
      icon: Music,
      title: 'Sonic Genome Analysis',
      description: 'Deep audio DNA (stems, harmonics, healing frequencies)',
    },
    {
      icon: TrendingUp,
      title: 'Multi-Platform Intelligence',
      description: 'Spotify + YouTube + Instagram tracking',
    },
  ];

  const competitors = [
    { name: 'DistroKid', cost: '$23', what: 'Distribution only' },
    { name: 'Chartmetric', cost: '$500', what: 'Analytics (no predictions)' },
    { name: 'SubmitHub', cost: '$50-200', what: 'Gambling on playlists' },
    { name: 'Playlist Push', cost: '$300-2000', what: 'One campaign' },
    { name: 'TuneScore Pro', cost: '$19', what: 'Everything above + predictions', highlight: true },
  ];

  const pricingTiers = [
    {
      name: 'Free',
      price: '$0',
      description: 'Get started with basic analysis',
      features: [
        'Upload 3 tracks',
        'Basic Sonic Genome report',
        'Lyrical sentiment arc',
        'Spotify/YouTube sync',
        'RIYL recommendations',
      ],
    },
    {
      name: 'Pro',
      price: '$19',
      period: '/month',
      description: 'Everything you need to succeed',
      features: [
        'Unlimited track uploads',
        'Viral hook detection',
        'AI pitch generation',
        'Breakout predictions',
        'Multi-platform dashboard',
        'Historical trend tracking',
        'Export reports (PDF/CSV)',
      ],
      highlight: true,
    },
    {
      name: 'Premium',
      price: '$49',
      period: '/month',
      description: 'Enterprise features + API access',
      features: [
        'Everything in Pro',
        'Catalog valuation',
        'Sync licensing matching',
        'A&R attention score',
        'API access',
        'White-label reports',
        'Dedicated account manager',
      ],
    },
  ];

  const faqs = [
    {
      question: 'How is this different from Chartmetric/Soundcharts?',
      answer: 'They show you what happened. We predict what happens next.',
    },
    {
      question: 'Do I need to switch from DistroKid?',
      answer: 'No! TuneScore sits on top of your existing tools.',
    },
    {
      question: 'What AI models do you use?',
      answer:
        '95% free local models (Whisper, VADER, Hugging Face). Premium features use Claude Haiku 4.5 at $0.0017/pitch (75% cheaper than competitors).',
    },
    {
      question: 'When will I get beta access?',
      answer:
        'We\'re onboarding beta testers in waves. Early signups get priority access. You\'ll receive an email when it\'s your turn.',
    },
    {
      question: 'Is my data safe?',
      answer:
        'Yes. We use enterprise-grade security, never sell your data, and you can delete your account anytime.',
    },
  ];
</script>

<svelte:head>
  <title>Join the Waitlist | TuneScore - Predict Your Music's Future</title>
  <meta
    name="description"
    content="Join the TuneScore beta and get early access to AI-powered music intelligence. Predict breakouts, generate pitch copy, and value your catalog."
  />
</svelte:head>

<div class="min-h-screen bg-background">
  <!-- Hero Section -->
  <section class="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden bg-richBlack dark">
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

    <div class="relative container mx-auto max-w-6xl">
      <div class="text-center mb-12">
        <div class="inline-flex items-center gap-2 bg-sage/20 text-sage px-4 py-2 rounded-full text-sm font-semibold mb-6 animate-pulse">
          <Sparkles class="w-4 h-4" />
          {waitlistCount > 0 ? `${waitlistCount} artists already joined` : 'Be the first to join'}
        </div>

        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6 font-serif">
          Predict Your Music's Future<br />Before You Release It
        </h1>

        <p class="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
          AI-powered intelligence that tells you which tracks will blow up, generates professional pitch
          copy in 1 second, and values your entire catalog—all for less than one SubmitHub campaign.
        </p>

        <!-- Waitlist Form -->
        {#if !isSuccess}
          <Card class="max-w-2xl mx-auto p-8 bg-white/10 border-white/20 backdrop-blur-sm">
            <form on:submit|preventDefault={handleSubmit} class="space-y-4">
              <div class="grid md:grid-cols-2 gap-4">
                <div class="text-left">
                  <Label for="email" class="text-white">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    bind:value={email}
                    placeholder="your@email.com"
                    required
                    class="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  />
                </div>
                <div class="text-left">
                  <Label for="name" class="text-white">Name (optional)</Label>
                  <Input
                    id="name"
                    type="text"
                    bind:value={name}
                    placeholder="Your name"
                    class="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  />
                </div>
              </div>

              <div class="text-left">
                <Label for="useCase" class="text-white">I am a... (optional)</Label>
                <select
                  id="useCase"
                  bind:value={useCase}
                  class="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-md text-white"
                >
                  <option value="">Select one</option>
                  <option value="creator">Creator (Artist/Producer)</option>
                  <option value="developer">Developer (A&R/Manager)</option>
                  <option value="monetizer">Monetizer (Executive/Label)</option>
                </select>
              </div>

              <div class="text-left">
                <Label for="referralSource" class="text-white">How did you hear about us? (optional)</Label>
                <Input
                  id="referralSource"
                  type="text"
                  bind:value={referralSource}
                  placeholder="Reddit, Twitter, friend, etc."
                  class="bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                />
              </div>

              <Button
                type="submit"
                size="lg"
                disabled={isSubmitting}
                class="w-full group relative overflow-hidden shadow-xl shadow-sage/20 hover:shadow-2xl hover:shadow-sage/30 transition-all duration-300"
              >
                <span class="relative z-10 flex items-center justify-center gap-2">
                  {isSubmitting ? 'Joining...' : 'Join Waitlist - Free Beta Access'}
                  <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
              </Button>
            </form>
          </Card>
        {:else}
          <Card class="max-w-2xl mx-auto p-8 bg-sage/20 border-sage/40 backdrop-blur-sm">
            <div class="text-center">
              <div class="w-16 h-16 bg-sage rounded-full flex items-center justify-center mx-auto mb-4">
                <Check class="w-8 h-8 text-richBlack" />
              </div>
              <h2 class="text-2xl font-bold text-white mb-2">You're on the list!</h2>
              <p class="text-gray-300 mb-4">
                Check your email for next steps. We'll notify you when it's your turn for beta access.
              </p>
              <p class="text-sm text-gray-400">
                Position in queue: #{waitlistCount}
              </p>
            </div>
          </Card>
        {/if}

        <p class="text-sm text-gray-400 mt-4">
          Less than 1 SubmitHub campaign. Forever.
        </p>
      </div>
    </div>
  </section>

  <!-- Problem Section -->
  <section class="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
    <div class="container mx-auto max-w-6xl text-center">
      <h2 class="text-3xl md:text-4xl font-bold mb-6">The Problem</h2>
      <p class="text-xl text-muted-foreground mb-12 max-w-3xl mx-auto">
        You're spending $50-200/month on SubmitHub gambling...<br />
        $500-2000 on Chartmetric just to see what already happened...<br />
        And still guessing which track to release next.
      </p>

      <!-- Competitor Comparison Table -->
      <Card class="max-w-4xl mx-auto overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b">
                <th class="text-left p-4 font-semibold">Service</th>
                <th class="text-left p-4 font-semibold">Monthly Cost</th>
                <th class="text-left p-4 font-semibold">What You Get</th>
              </tr>
            </thead>
            <tbody>
              {#each competitors as competitor}
                <tr
                  class="border-b last:border-b-0 {competitor.highlight
                    ? 'bg-sage/10 font-semibold'
                    : ''}"
                >
                  <td class="p-4">{competitor.name}</td>
                  <td class="p-4">{competitor.cost}</td>
                  <td class="p-4">{competitor.what}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  </section>

  <!-- Features Section -->
  <section class="py-20 px-4 sm:px-6 lg:px-8">
    <div class="container mx-auto max-w-7xl">
      <div class="text-center mb-12">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">What Makes TuneScore Different</h2>
        <p class="text-xl text-muted-foreground max-w-2xl mx-auto">
          We don't just show you what's happening—we tell you what happens next and what to do about it.
        </p>
      </div>

      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {#each features as feature}
          <Card class="p-6 hover:shadow-lg transition-shadow">
            <svelte:component this={feature.icon} class="h-12 w-12 text-primary mb-4" />
            <h3 class="text-xl font-semibold mb-2">{feature.title}</h3>
            <p class="text-muted-foreground">{feature.description}</p>
          </Card>
        {/each}
      </div>
    </div>
  </section>

  <!-- Pricing Section -->
  <section class="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
    <div class="container mx-auto max-w-7xl">
      <div class="text-center mb-12">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
        <p class="text-xl text-muted-foreground">
          Start free, upgrade when you're ready
        </p>
      </div>

      <div class="grid md:grid-cols-3 gap-8">
        {#each pricingTiers as tier}
          <Card
            class="p-8 {tier.highlight
              ? 'border-sage border-2 shadow-xl shadow-sage/20'
              : ''} relative"
          >
            {#if tier.highlight}
              <div
                class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-sage text-richBlack px-4 py-1 rounded-full text-sm font-semibold"
              >
                Most Popular
              </div>
            {/if}

            <div class="text-center mb-6">
              <h3 class="text-2xl font-bold mb-2">{tier.name}</h3>
              <div class="flex items-baseline justify-center gap-1 mb-2">
                <span class="text-4xl font-bold">{tier.price}</span>
                {#if tier.period}
                  <span class="text-muted-foreground">{tier.period}</span>
                {/if}
              </div>
              <p class="text-sm text-muted-foreground">{tier.description}</p>
            </div>

            <ul class="space-y-3 mb-6">
              {#each tier.features as feature}
                <li class="flex items-start gap-2">
                  <Check class="w-5 h-5 text-sage flex-shrink-0 mt-0.5" />
                  <span class="text-sm">{feature}</span>
                </li>
              {/each}
            </ul>

            <Button
              href="#waitlist"
              variant={tier.highlight ? 'default' : 'outline'}
              class="w-full"
              on:click={() => {
                document.querySelector('section')?.scrollIntoView({ behavior: 'smooth' });
              }}
            >
              Join Waitlist
            </Button>
          </Card>
        {/each}
      </div>

      <p class="text-center text-sm text-muted-foreground mt-8">
        Pay annually and get 2 months free. Early adopters lock in special pricing forever.
      </p>
    </div>
  </section>

  <!-- FAQ Section -->
  <section class="py-20 px-4 sm:px-6 lg:px-8">
    <div class="container mx-auto max-w-3xl">
      <h2 class="text-3xl md:text-4xl font-bold mb-12 text-center">Frequently Asked Questions</h2>

      <div class="space-y-6">
        {#each faqs as faq}
          <Card class="p-6">
            <h3 class="text-lg font-semibold mb-2">{faq.question}</h3>
            <p class="text-muted-foreground">{faq.answer}</p>
          </Card>
        {/each}
      </div>
    </div>
  </section>

  <!-- Final CTA -->
  <section class="py-20 px-4 sm:px-6 lg:px-8 bg-richBlack dark text-center">
    <div class="container mx-auto max-w-4xl">
      <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">
        Ready to Predict Your Music's Future?
      </h2>
      <p class="text-xl text-gray-300 mb-8">
        Join {waitlistCount > 0 ? `${waitlistCount} artists` : 'artists'} who are already on the waitlist
      </p>
      <Button
        size="lg"
        href="#waitlist"
        class="group relative overflow-hidden shadow-xl shadow-sage/20 hover:shadow-2xl hover:shadow-sage/30 transition-all duration-300"
        on:click={() => {
          document.querySelector('section')?.scrollIntoView({ behavior: 'smooth' });
        }}
      >
        <span class="relative z-10 flex items-center gap-2">
          Join Waitlist Now
          <ArrowRight class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </span>
      </Button>
    </div>
  </section>
</div>

<style>
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

