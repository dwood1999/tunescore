<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto, replaceState } from '$app/navigation';
  import { authStore, isAuthenticated, returnUrlStore } from '$lib/stores/auth';
  import { toastStore } from '$lib/stores/toast';
  import Button from '$lib/components/ui/button.svelte';
  import Input from '$lib/components/ui/input.svelte';
  import Label from '$lib/components/ui/label.svelte';
  import { isValidEmail } from '$lib/utils';

  // Test credentials for MVP development
  const TEST_CREDENTIALS = {
    email: 'dwood@nuper.com',
    password: '49Niners!',
  };

  const mode = $derived($page.url.searchParams.get('mode') === 'register' ? 'register' : 'login');

  let email = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let showPassword = $state(false);
  let showConfirmPassword = $state(false);
  let isLoading = $state(false);
  let rememberMe = $state(false);
  let error = $state('');

  // Validation
  const emailError = $derived(email && !isValidEmail(email) ? 'Please enter a valid email' : '');
  const passwordError = $derived(
    password && password.length < 8 ? 'Password must be at least 8 characters' : ''
  );
  const confirmPasswordError = $derived(
    mode === 'register' && confirmPassword && confirmPassword !== password
      ? 'Passwords do not match'
      : ''
  );

  const isFormValid = $derived(
    !!email &&
      !!password &&
      !emailError &&
      !passwordError &&
      (mode === 'login' || (!!confirmPassword && !confirmPasswordError))
  );

  // Check auth state on mount - redirect if already logged in
  onMount(async () => {
    // Check for return URL in query params
    const urlParams = new URLSearchParams($page.url.search);
    const returnUrlParam = urlParams.get('returnUrl');
    if (returnUrlParam) {
      returnUrlStore.set(returnUrlParam);
    }

    // Ensure auth store is initialized
    await authStore.initialize();

    if ($isAuthenticated) {
      toastStore.success('Already signed in');
      returnUrlStore.redirectAfterAuth();
    }
  });

  // Watch for auth state changes
  $effect(() => {
    if (typeof window !== 'undefined' && $isAuthenticated) {
      toastStore.success('Successfully signed in');
      returnUrlStore.redirectAfterAuth();
    }
  });

  async function handleSubmit() {
    error = '';
    if (!isFormValid) return;

    isLoading = true;
    try {
      if (mode === 'login') {
        const result = await authStore.login({
          email: email.trim().toLowerCase(),
          password,
        });

        if (result.success) {
          toastStore.success('Successfully signed in');
          returnUrlStore.redirectAfterAuth();
        } else {
          error = result.error || 'Login failed';
          toastStore.error(error);
        }
      } else {
        const result = await authStore.register({
          email: email.trim().toLowerCase(),
          password,
        });

        if (result.success) {
          toastStore.success('Registration successful! Redirecting...');
          returnUrlStore.redirectAfterAuth();
        } else {
          error = result.error || 'Registration failed';
          toastStore.error(error);
        }
      }
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'An error occurred';
      error = errorMessage;
      toastStore.error(errorMessage);
    } finally {
      isLoading = false;
    }
  }

  function toggleMode() {
    email = '';
    password = '';
    confirmPassword = '';
    error = '';
    const newMode = mode === 'login' ? 'register' : 'login';
    const url = new URL($page.url);
    if (newMode === 'register') {
      url.searchParams.set('mode', 'register');
    } else {
      url.searchParams.delete('mode');
    }
    replaceState(url.toString(), {});
  }

  function fillTestCredentials() {
    email = TEST_CREDENTIALS.email;
    password = TEST_CREDENTIALS.password;
  }
</script>

<svelte:head>
  <title>{mode === 'login' ? 'Sign In' : 'Sign Up'} - TuneScore</title>
  <meta
    name="description"
    content={mode === 'login'
      ? 'Sign in to your TuneScore account'
      : 'Create your free TuneScore account'}
  />
</svelte:head>

<div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
  <div class="sm:mx-auto sm:w-full sm:max-w-md">
    <!-- Logo -->
    <div class="flex justify-center">
      <a href="/" class="flex items-center">
        <div class="w-12 h-12 bg-primary rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-xl">T</span>
        </div>
        <span class="ml-3 text-2xl font-bold text-gray-900">TuneScore</span>
      </a>
    </div>
  </div>

  <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
    <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">
          {mode === 'login' ? 'Welcome back' : 'Create your account'}
        </h1>
        <p class="text-gray-600">
          {mode === 'login'
            ? 'Sign in to access your music intelligence platform'
            : 'Start analyzing your tracks with AI-powered insights'}
        </p>
      </div>

      <!-- Mode Toggle -->
      <div class="flex rounded-lg bg-gray-100 p-1 mb-6">
        <button
          type="button"
          class="flex-1 rounded-md py-2 px-4 text-sm font-medium transition-all duration-200 {mode ===
          'login'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-500 hover:text-gray-700'}"
          onclick={() => mode === 'register' && toggleMode()}
        >
          Sign In
        </button>
        <button
          type="button"
          class="flex-1 rounded-md py-2 px-4 text-sm font-medium transition-all duration-200 {mode ===
          'register'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-500 hover:text-gray-700'}"
          onclick={() => mode === 'login' && toggleMode()}
        >
          Sign Up
        </button>
      </div>

      <!-- Development Test Credentials Notice -->
      {#if mode === 'login'}
        <div class="mb-4 p-3 rounded-md bg-blue-50 border border-blue-200">
          <div class="flex items-start">
            <svg
              class="h-5 w-5 text-blue-400 mr-2 flex-shrink-0 mt-0.5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clip-rule="evenodd"
              />
            </svg>
            <div class="flex-1">
              <p class="text-sm text-blue-800 mb-2">
                <strong>MVP Testing:</strong> Use test credentials to login
              </p>
              <button
                type="button"
                class="text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded transition-colors"
                onclick={fillTestCredentials}
              >
                Fill Test Credentials
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- Error Message -->
      {#if error}
        <div class="mb-4 p-3 rounded-md bg-red-50 border border-red-200">
          <div class="flex">
            <svg
              class="h-5 w-5 text-red-400 mr-2 flex-shrink-0"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clip-rule="evenodd"
              />
            </svg>
            <p class="text-sm text-red-800">{error}</p>
          </div>
        </div>
      {/if}

      <!-- Form -->
      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
        <!-- Email Field -->
        <div>
          <Label for="email">Email address</Label>
          <Input
            id="email"
            name="email"
            type="email"
            autocomplete="email"
            bind:value={email}
            placeholder="you@example.com"
            required
            class={emailError ? 'border-red-500' : ''}
          />
          {#if emailError}
            <p class="mt-1 text-sm text-red-600">{emailError}</p>
          {/if}
        </div>

        <!-- Password Field -->
        <div>
          <Label for="password">Password</Label>
          <div class="relative">
            <Input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autocomplete={mode === 'login' ? 'current-password' : 'new-password'}
              bind:value={password}
              placeholder={mode === 'login' ? 'Enter your password' : 'At least 8 characters'}
              required
              class={passwordError ? 'border-red-500 pr-10' : 'pr-10'}
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
              onclick={() => (showPassword = !showPassword)}
            >
              {#if showPassword}
                <svg
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                  />
                </svg>
              {:else}
                <svg
                  class="h-5 w-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              {/if}
            </button>
          </div>
          {#if passwordError}
            <p class="mt-1 text-sm text-red-600">{passwordError}</p>
          {/if}
        </div>

        <!-- Confirm Password (Register only) -->
        {#if mode === 'register'}
          <div>
            <Label for="confirmPassword">Confirm Password</Label>
            <div class="relative">
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                autocomplete="new-password"
                bind:value={confirmPassword}
                placeholder="Confirm your password"
                required
                class={confirmPasswordError ? 'border-red-500 pr-10' : 'pr-10'}
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                onclick={() => (showConfirmPassword = !showConfirmPassword)}
              >
                {#if showConfirmPassword}
                  <svg
                    class="h-5 w-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                    />
                  </svg>
                {:else}
                  <svg
                    class="h-5 w-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                {/if}
              </button>
            </div>
            {#if confirmPasswordError}
              <p class="mt-1 text-sm text-red-600">{confirmPasswordError}</p>
            {/if}
          </div>
        {/if}

        <!-- Remember Me (Login only) -->
        {#if mode === 'login'}
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="rememberMe"
                name="rememberMe"
                type="checkbox"
                class="h-4 w-4 text-primary focus:ring-ring border-gray-300 rounded"
                bind:checked={rememberMe}
                disabled={isLoading}
              />
              <label for="rememberMe" class="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>
            <a href="/forgot-password" class="text-sm text-primary hover:text-primary">
              Forgot password?
            </a>
          </div>
        {/if}

        <!-- Submit Button -->
        <Button type="submit" class="w-full" disabled={!isFormValid || isLoading} size="lg">
          {#if isLoading}
            <svg
              class="animate-spin -ml-1 mr-3 h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          {/if}
          {mode === 'login' ? (isLoading ? 'Signing in...' : 'Sign In') : (isLoading ? 'Creating account...' : 'Create Account')}
        </Button>
      </form>

      <!-- Footer -->
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button type="button" class="font-medium text-primary hover:text-primary" onclick={toggleMode}>
            {mode === 'login' ? 'Sign up' : 'Sign in'}
          </button>
        </p>
      </div>
    </div>

    <!-- Terms Footer -->
    <div class="mt-8 text-center">
      <p class="text-sm text-gray-600">
        {mode === 'login' ? 'By signing in, you agree to our ' : 'By creating an account, you agree to our '}
        <a href="/terms" class="text-primary hover:text-primary">Terms of Service</a>
        {' and '}
        <a href="/privacy" class="text-primary hover:text-primary">Privacy Policy</a>
      </p>
    </div>
  </div>
</div>
