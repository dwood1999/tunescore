<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import '../app.css';
  import { authStore } from '$lib/stores/auth';
  import ToastContainer from '$lib/components/ToastContainer.svelte';
  import WorkspaceLayout from '$lib/components/WorkspaceLayout.svelte';
  import Navigation from '$lib/components/Navigation.svelte';

  // Initialize auth store on mount
  onMount(async () => {
    await authStore.initialize();
  });

  // Determine if we should use the old navigation (for login/waitlist pages)
  const useSimpleNav = $derived(
    $page.url.pathname === '/login' || 
    $page.url.pathname === '/waitlist' ||
    $page.url.pathname === '/'
  );
</script>

<svelte:head>
  <title>TuneScore - Bloomberg Terminal for Music Industry</title>
  <meta name="description" content="AI-powered intelligence platform for the music industry" />
</svelte:head>

{#if useSimpleNav}
  <!-- Simple Navigation for public pages -->
  <div class="min-h-screen bg-gray-50">
    <Navigation />
    <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <slot />
    </main>
  </div>
{:else}
  <!-- Workspace Layout for app pages -->
  <WorkspaceLayout>
    <slot />
  </WorkspaceLayout>
{/if}

<!-- Global Toast Container -->
<ToastContainer />


