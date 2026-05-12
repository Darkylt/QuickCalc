<script lang="ts">
  import { onMount } from "svelte";
  import Titlebar from "$lib/Titlebar.svelte";
  import Editor from "$lib/Editor.svelte";
  import Settings from "$lib/Settings.svelte";

  let editor: Editor;
  let showSettings = false;

  onMount(() => {
    // When the OS brings this window into focus (via the global shortcut),
    // move the cursor to the end of whatever is already typed.
    window.addEventListener("focus", () => {
      editor?.focusEnd();
    });
  });
</script>

<main class="window">
  <Titlebar onSettingsClick={() => (showSettings = true)} />
  <Editor bind:this={editor} />
  {#if showSettings}
    <Settings onClose={() => (showSettings = false)} />
  {/if}
</main>

<style>
.window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
</style>