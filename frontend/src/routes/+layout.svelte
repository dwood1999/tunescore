<script lang="ts">
  import { onMount } from 'svelte';
  import '../app.css';
  import { authStore } from '$lib/stores/auth';
  import ToastContainer from '$lib/components/ToastContainer.svelte';
  import Navigation from '$lib/components/Navigation.svelte';

  // Initialize auth store on mount
  onMount(async () => {
    await authStore.initialize();
  });
</script>

<svelte:head>
  <title>TuneScore - Bloomberg Terminal for Music Industry</title>
  <meta name="description" content="AI-powered intelligence platform for the music industry" />
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Navigation -->
  <Navigation />

  <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
    <slot />
  </main>
</div>

<!-- Global Toast Container -->
<ToastContainer />


