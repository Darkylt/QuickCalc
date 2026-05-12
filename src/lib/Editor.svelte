<script lang="ts">
  import { onMount } from "svelte";
  import { invoke } from "@tauri-apps/api/core";

  let text = "";
  let suggestion = "";
  let textarea: HTMLTextAreaElement;
  let shadowStyle = "";

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

  function updateShadow() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const spread = Math.min(width, height) / 5; // scale factor
    const blur = Math.min(width, height) / 20;
    shadowStyle = `inset 0 0 ${blur}px rgba(132, 0, 255, 0.1), inset 0 0 ${spread}px rgba(132, 0, 255, 0.1)`;
  }

  export function focusEnd() {
    if (!textarea) return;
    textarea.focus();
    const len = textarea.value.length;
    textarea.setSelectionRange(len, len);
  }

  onMount(() => {
    updateShadow();
    window.addEventListener("resize", updateShadow);
    return () => window.removeEventListener("resize", updateShadow);
  });
</script>

<div class="editor-container" style="box-shadow: {shadowStyle}">
  <textarea
    bind:this={textarea}
    bind:value={text}
    on:input={updateSuggestion}
    on:keydown={handleKeydown}
    class="editor"
    placeholder="Type here..."
    spellcheck="false"
    autocorrect="off"
    autocomplete="off"
    autocapitalize="off"
  ></textarea>

  {#if suggestion}
    <div class="suggestion">{suggestion}</div>
  {/if}
</div>

<style>
.editor-container {
  position: relative;
  flex: 1;
  background: rgba(17, 17, 17);
  overflow: hidden;
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
</style>