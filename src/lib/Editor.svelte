<script lang="ts">
  import { onMount } from "svelte";
  import { invoke } from "@tauri-apps/api/core";

  let text = "";
  let suggestion = "";
  let textarea: HTMLTextAreaElement;

  const match = text.match(/([0-9+\-*/().^]+)=/);


  async function updateSuggestion() {
    if (!match) {
      suggestion = "";
      return;
    }

    const expr = match[1];

    try {
      const result = await invoke("evaluate_math", { expr });
      suggestion = String(result);
    } catch (e) {
      suggestion = "";
    }
  }


  function acceptSuggestion() {
    if (!suggestion) return;
    if (!match) return;

    const expr = match[0];
    const fullMatch = match[0];
    const index = text.indexOf(fullMatch);

    const before = text.slice(0, index + fullMatch.length);
    const after = text.slice(index + fullMatch.length);

    text = before + suggestion + after;
    suggestion = "";
  }


  function handleKeydown(e: KeyboardEvent) {
    if (e.key === "Tab" && suggestion) {
      e.preventDefault();
      acceptSuggestion();
    }
  }
</script>

<div class="editor-wrapper">
  <textarea
    bind:this={textarea}
    bind:value={text}
    on:input={updateSuggestion}
    on:keydown={handleKeydown}
  ></textarea>

  {#if suggestion}
    <div class="ghost">
      {suggestion}
    </div>
  {/if}
</div>

<style>
  .editor-wrapper {
    position: relative;
  }

  textarea {
    width: 100%;
    height: 100%;
    font-family: monospace;
    font-size: 16px;
    padding: 8px;
  }

  .ghost {
    position: absolute;
    bottom: 8px;
    right: 8px;
    opacity: 0.4;
    font-family: monospace;
    pointer-events: none;
  }
</style>
