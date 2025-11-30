<script lang="ts">
  import { onMount } from 'svelte';
  import { setupHotkey } from '$lib/hotkey';

  onMount(() => {
    setupHotkey();
  });
</script>

<main class="container">
  <h1>Welcome to Tauri + Svelte</h1>
  
</main>
