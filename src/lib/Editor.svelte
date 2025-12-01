<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { onMount } from "svelte";

  let text = "";
  let suggestion = "";

  let textarea: HTMLTextAreaElement;

  async function updateSuggestion() {
    const match = text.match(/([0-9+\-*/().^]+)=/);

    if (!match) {
      suggestion = "";
      return;
    }

    const expr = match[1];

    try {
      const result = await invoke("evaluate_math", { expr });
      suggestion = String(result);
    } catch {
      suggestion = "";
    }
  }

  function acceptSuggestion() {
    if (!suggestion) return;

    const match = text.match(/([0-9+\-*/().^]+)=/);
    if (!match) return;

    const fullMatch = match[0];
    const index = text.indexOf(fullMatch);

    const before = text.slice(0, index + fullMatch.length);
    const after = text.slice(index + fullMatch.length);

    text = before + suggestion + after;
    suggestion = "";
  }

  function handleKeydown(e) {
    if (e.key === "Tab" && suggestion) {
      e.preventDefault();
      acceptSuggestion();
    }
  }
</script>

<div class="editor-container">
  <textarea
    bind:this={textarea}
    bind:value={text}
    on:input={updateSuggestion}
    on:keydown={handleKeydown}
    class="editor"
    placeholder="Type here..."
  ></textarea>

  {#if suggestion}
    <div class="suggestion">{suggestion}</div>
  {/if}
</div>

<style>
.editor-container {
  position: absolute;
  inset: 0;
  background: rgba(17, 17, 17);
  padding: 0;
  overflow: hidden;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.1),
    0 4px 40px rgba(0,0,0,0.6),
    0 0 30px rgba(132, 0, 255, 0.15);
}

.editor {
  width: 100%;
  height: 100%;
  resize: none;
  background: transparent;
  border: none;
  outline: none;
  padding: 18px;
  color: #eaeaea;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 18px;
  line-height: 1.5;
  caret-color: #8f4ff7;
  box-sizing: border-box;
}

.suggestion {
  position: absolute;
  bottom: 14px;
  right: 18px;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 18px;
  opacity: 0.6;
  color: #8f4ff7;
  pointer-events: none;
}

.editor::-webkit-scrollbar {
  width: 10px;
}

.editor::-webkit-scrollbar-thumb {
  background: #2e2e2e;
  border-radius: 10px;
}

.editor::-webkit-scrollbar-thumb:hover {
  background: #444;
}
</style>
