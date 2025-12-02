<script lang="ts">
  import Titlebar from "$lib/Titlebar.svelte";
  import Editor from "$lib/Editor.svelte";
</script>

<main class="window">
  <Titlebar />
  <Editor />
</main>

<style>
.window {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}
</style>
