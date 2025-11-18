<script lang="ts">
  import { Upload, Music, FileText, CheckCircle2, AlertCircle } from 'lucide-svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { toastStore } from '$lib/stores/toast';
  import Button from '$lib/components/ui/button.svelte';
  import Card from '$lib/components/ui/card.svelte';
  import Input from '$lib/components/ui/input.svelte';
  import Label from '$lib/components/ui/label.svelte';
  import { formatFileSize } from '$lib/utils';

  let uploading = $state(false);
  let uploadProgress = $state(0);

  let trackTitle = $state('');
  let artistName = $state('');
  let genre = $state('');
  let lyrics = $state('');

  let audioFile: File | null = $state(null);
  let lyricsFile: File | null = $state(null);
  let dragActive = $state(false);
  let audioInputElement = $state<HTMLInputElement | null>(null);
  let lyricsInputElement = $state<HTMLInputElement | null>(null);

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
    dragActive = true;
  }

  function handleDragLeave() {
    dragActive = false;
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragActive = false;
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('audio/') || /\.(mp3|wav|flac|m4a|ogg)$/i.test(file.name)) {
        audioFile = file;
      }
    }
  }

  function triggerAudioFileInput() {
    audioInputElement?.click();
  }

  function triggerLyricsFileInput() {
    lyricsInputElement?.click();
  }

  async function handleUpload() {
    if (!trackTitle || !artistName) {
      toastStore.error('Track title and artist name are required');
      return;
    }

    uploading = true;
    uploadProgress = 0;

    try {
      const formData = new FormData();

      const trackData = {
        title: trackTitle,
        artist_name: artistName,
        genre: genre || null,
        lyrics: lyrics || null,
      };
      formData.append('track_data', JSON.stringify(trackData));

      if (audioFile) {
        formData.append('audio_file', audioFile);
      }

      if (lyricsFile) {
        formData.append('lyrics_file', lyricsFile);
      }

      // Simulate progress (in real app, you'd track actual upload progress)
      const progressInterval = setInterval(() => {
        uploadProgress = Math.min(uploadProgress + 10, 90);
      }, 200);

      const result = await api.tracks.upload(formData);
      clearInterval(progressInterval);
      uploadProgress = 100;

      toastStore.success('Track uploaded successfully! Analysis starting...');

      // Reset form
      trackTitle = '';
      artistName = '';
      genre = '';
      lyrics = '';
      audioFile = null;
      lyricsFile = null;
      uploadProgress = 0;

      // Redirect to track details after a short delay
      const trackId = result?.track?.id;

      if (!trackId) {
        const fallbackMessage =
          typeof result === 'object' && result !== null && 'message' in result && typeof result.message === 'string'
            ? result.message
            : 'Track uploaded but response was incomplete. Please refresh to confirm.';
        toastStore.error(fallbackMessage);
        return;
      }

      setTimeout(() => {
        goto(`/tracks/${trackId}`);
      }, 1500);
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Upload failed';
      toastStore.error(message);
    } finally {
      uploading = false;
      uploadProgress = 0;
    }
  }

  function handleAudioFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    audioFile = target.files?.[0] || null;
  }

  function handleLyricsFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    lyricsFile = target.files?.[0] || null;
    if (lyricsFile) {
      // Read lyrics file content
      const reader = new FileReader();
      reader.onload = (event) => {
        lyrics = event.target?.result as string;
      };
      reader.readAsText(lyricsFile);
    }
  }

  function removeAudioFile() {
    audioFile = null;
  }

  function removeLyricsFile() {
    lyricsFile = null;
  }
</script>

<div class="max-w-3xl mx-auto space-y-6">
  <!-- Header -->
  <div>
    <h1 class="text-3xl font-bold mb-2">Upload Track</h1>
    <p class="text-muted-foreground">
      Upload your track for comprehensive Sonic & Lyrical Genome analysis
    </p>
  </div>

  <form onsubmit={(e) => { e.preventDefault(); handleUpload(); }} class="space-y-6">
    <!-- Track Info Card -->
    <Card class="p-6">
      <h2 class="text-lg font-semibold mb-4">Track Information</h2>
      <div class="space-y-4">
        <div>
          <Label for="title">Track Title *</Label>
          <Input
            id="title"
            type="text"
            bind:value={trackTitle}
            required
            placeholder="Enter track title"
            disabled={uploading}
          />
        </div>

        <div>
          <Label for="artist">Artist Name *</Label>
          <Input
            id="artist"
            type="text"
            bind:value={artistName}
            required
            placeholder="Enter artist name"
            disabled={uploading}
          />
        </div>

        <div>
          <Label for="genre">Genre</Label>
          <Input
            id="genre"
            type="text"
            bind:value={genre}
            placeholder="e.g., Pop, Rock, Hip-Hop, Electronic"
            disabled={uploading}
          />
        </div>
      </div>
    </Card>

    <!-- Audio File Card -->
    <Card class="p-6">
      <h2 class="text-lg font-semibold mb-4">Audio File</h2>
      {#if audioFile}
        <div class="flex items-center justify-between p-4 bg-primary/10 rounded-lg">
          <div class="flex items-center gap-3">
            <Music class="h-8 w-8 text-primary" />
            <div>
              <p class="font-medium">{audioFile.name}</p>
              <p class="text-sm text-muted-foreground">{formatFileSize(audioFile.size)}</p>
            </div>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onclick={removeAudioFile}
            disabled={uploading}
          >
            Remove
          </Button>
        </div>
      {:else}
        <div
          class="relative flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-lg cursor-pointer hover:bg-accent transition-colors overflow-hidden {dragActive
            ? 'bg-accent border-primary'
            : ''}"
          onclick={triggerAudioFileInput}
          ondragover={handleDragOver}
          ondragleave={handleDragLeave}
          ondrop={handleDrop}
          role="button"
          tabindex="0"
          onkeydown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              triggerAudioFileInput();
            }
          }}
        >
          <div class="pointer-events-none flex flex-col items-center justify-center pt-5 pb-6">
            <Upload class="h-10 w-10 mb-3 text-muted-foreground" />
            <p class="mb-2 text-sm font-medium text-foreground">
              Click to upload or drag and drop
            </p>
            <p class="text-xs text-muted-foreground">MP3, WAV, FLAC, M4A, OGG (max 500MB)</p>
          </div>
          <input
            bind:this={audioInputElement}
            id="audio"
            type="file"
            accept=".mp3,.wav,.flac,.m4a,.ogg"
            onchange={handleAudioFileSelect}
            class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
            disabled={uploading}
            aria-label="Select audio file"
          />
        </div>
      {/if}
    </Card>

    <!-- Lyrics Card -->
    <Card class="p-6">
      <h2 class="text-lg font-semibold mb-4">Lyrics (Optional)</h2>
      
      <!-- Auto-transcription Info Banner -->
      <div class="mb-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-md">
        <div class="flex items-start gap-2">
          <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm text-blue-900 dark:text-blue-100">
            <p class="font-medium mb-1">Lyrics not required! We'll automatically:</p>
            <ul class="list-disc list-inside space-y-0.5 ml-1">
              <li>Search our database for popular songs (instant)</li>
              <li>Transcribe from audio using AI if not found (~30-60s)</li>
            </ul>
            <p class="mt-2 text-xs text-blue-700 dark:text-blue-300">
              You can review and edit lyrics after upload.
            </p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div>
          <Label for="lyrics">Paste Lyrics</Label>
          <textarea
            id="lyrics"
            bind:value={lyrics}
            rows="8"
            class="w-full px-3 py-2 rounded-md border border-input bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Paste lyrics here or upload a file below..."
            disabled={uploading}
          ></textarea>
        </div>

        <div class="text-sm text-muted-foreground">Or upload a lyrics file:</div>
        {#if lyricsFile}
          <div class="flex items-center justify-between p-4 bg-primary/10 rounded-lg">
            <div class="flex items-center gap-3">
              <FileText class="h-6 w-6 text-primary" />
              <div>
                <p class="font-medium">{lyricsFile.name}</p>
                <p class="text-sm text-muted-foreground">{formatFileSize(lyricsFile.size)}</p>
              </div>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onclick={removeLyricsFile}
              disabled={uploading}
            >
              Remove
            </Button>
          </div>
        {:else}
          <div
            class="relative flex items-center gap-2 px-4 py-2 border rounded-lg cursor-pointer hover:bg-accent transition-colors w-fit"
            onclick={triggerLyricsFileInput}
            role="button"
            tabindex="0"
            onkeydown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                triggerLyricsFileInput();
              }
            }}
          >
            <div class="pointer-events-none flex items-center gap-2">
              <FileText class="h-4 w-4" />
              <span>Choose lyrics file (TXT)</span>
            </div>
            <input
              bind:this={lyricsInputElement}
              id="lyrics-file"
              type="file"
              accept=".txt"
              onchange={handleLyricsFileSelect}
              class="absolute inset-0 h-full w-full cursor-pointer opacity-0"
              disabled={uploading}
              aria-label="Select lyrics file"
            />
          </div>
        {/if}
      </div>
    </Card>

    <!-- Upload Progress -->
    {#if uploading}
      <Card class="p-6">
        <div class="space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium">Uploading track...</span>
            <span class="text-muted-foreground">{uploadProgress}%</span>
          </div>
          <div class="w-full bg-muted rounded-full h-2">
            <div
              class="bg-primary h-2 rounded-full transition-all duration-300"
              style="width: {uploadProgress}%"
            ></div>
          </div>
        </div>
      </Card>
    {/if}

    <!-- Submit Button -->
    <div class="flex gap-4">
      <Button
        type="submit"
        class="flex-1"
        size="lg"
        disabled={uploading || !trackTitle || !artistName}
      >
        {#if uploading}
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
          Uploading...
        {:else}
          <Upload class="w-4 h-4 mr-2" />
          Upload Track
        {/if}
      </Button>
      <Button type="button" variant="outline" size="lg" href="/dashboard" disabled={uploading}>
        Cancel
      </Button>
    </div>

    <!-- Help Text -->
    <div class="text-sm text-muted-foreground space-y-1">
      <p>* Required fields</p>
      <p>
        Tip: Leave lyrics blank and we'll find or transcribe them automatically.
        You can review and edit after upload.
      </p>
    </div>
  </form>
</div>


