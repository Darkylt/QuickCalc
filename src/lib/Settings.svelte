<script lang="ts">
  import { onMount } from "svelte";
  import { invoke } from "@tauri-apps/api/core";

  export let onClose: () => void = () => {};

  let currentKey = "";
  let currentMods: string[] = [];
  let capturing = false;
  let saveStatus = "";

  $: displayShortcut = formatShortcut(currentMods, currentKey);

  function formatShortcut(mods: string[], key: string) {
    if (!key) return "None";
    return [...mods, key].join(" + ");
  }

  onMount(async () => {
    try {
      const settings = await invoke<{ shortcut_key: string; shortcut_mods: string[] }>("get_settings");
      currentKey = settings.shortcut_key;
      currentMods = settings.shortcut_mods;
    } catch {
      // defaults
      currentKey = "F13";
      currentMods = [];
    }
  });

  function startCapture() {
    capturing = true;
    saveStatus = "";
  }

  function handleCapture(e: KeyboardEvent) {
    if (!capturing) return;
    e.preventDefault();
    e.stopPropagation();

    if (["Control", "Shift", "Alt", "Meta"].includes(e.key)) return;

    if (e.key === "Escape") {
      capturing = false;
      return;
    }

    const mods: string[] = [];
    if (e.ctrlKey)  mods.push("Ctrl");
    if (e.altKey)   mods.push("Alt");
    if (e.shiftKey) mods.push("Shift");
    if (e.metaKey)  mods.push("Super");

    let key = e.key;
    if (key === " ") key = "Space";
    else if (key.length === 1) key = key.toUpperCase();

    currentMods = mods;
    currentKey = key;
    capturing = false;
  }

  async function save() {
    try {
      await invoke("save_settings", {
        settings: { shortcut_key: currentKey, shortcut_mods: currentMods },
      });
      saveStatus = "Saved! Restart to apply.";
    } catch (err) {
      saveStatus = typeof err === "string" ? err : "Error saving settings.";
      console.error(err);
    }
  }
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  class="overlay"
  on:keydown={handleCapture}
  tabindex="-1"
>
  <div class="modal">
    <div class="modal-header">
      <span class="modal-title">Settings</span>
      <button class="close-btn" on:click={onClose}>x</button>
    </div>

    <div class="section">
      <label class="label">Global shortcut</label>
      <div class="shortcut-row">
        <div class="shortcut-display" class:active={capturing}>
          {capturing ? "Press a key…" : displayShortcut}
        </div>
        <button class="capture-btn" on:click={startCapture}>
          {capturing ? "Listening…" : "Change"}
        </button>
      </div>
      <p class="hint">Press Escape to cancel. Restart the app after saving.</p>
    </div>

    <div class="actions">
      {#if saveStatus}
        <span class="save-status">{saveStatus}</span>
      {/if}
      <button class="save-btn" on:click={save}>Save</button>
    </div>
  </div>
</div>

<style>
.overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: linear-gradient(
    160deg,
    rgba(28, 14, 45, 0.98),
    rgba(45, 5, 72, 0.98)
  );
  border: 1px solid rgba(160, 60, 255, 0.25);
  border-radius: 10px;
  box-shadow:
    0 0 40px rgba(130, 40, 220, 0.3),
    0 0 8px rgba(130, 40, 220, 0.2) inset;
  width: 320px;
  padding: 0;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(90, 0, 140, 0.25);
}

.modal-title {
  font-family: "JetBrains Mono", monospace;
  font-size: 13px;
  font-weight: 500;
  color: #d8cafa;
  letter-spacing: 0.5px;
}

.close-btn {
  background: none;
  border: none;
  color: #a07cc5;
  font-size: 20px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
  transition: color 0.15s;
}
.close-btn:hover { color: #ff6060; }

.section {
  padding: 18px 16px 10px;
}

.label {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: #7a5ea0;
  display: block;
  margin-bottom: 10px;
}

.shortcut-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.shortcut-display {
  flex: 1;
  font-family: "JetBrains Mono", monospace;
  font-size: 14px;
  color: #e2d4ff;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(160, 60, 255, 0.2);
  border-radius: 6px;
  padding: 7px 12px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.shortcut-display.active {
  border-color: rgba(160, 60, 255, 0.6);
  box-shadow: 0 0 10px rgba(160, 60, 255, 0.25);
  color: #c49dff;
}

.capture-btn {
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  background: rgba(130, 40, 220, 0.2);
  border: 1px solid rgba(160, 60, 255, 0.3);
  border-radius: 6px;
  color: #c49dff;
  padding: 7px 12px;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.capture-btn:hover {
  background: rgba(160, 60, 255, 0.28);
  box-shadow: 0 0 10px rgba(160, 60, 255, 0.3);
}

.hint {
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: #5a4570;
  margin: 8px 0 0;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 10px 16px 16px;
}

.save-status {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  color: #9f7fd4;
}

.save-btn {
  font-family: "JetBrains Mono", monospace;
  font-size: 13px;
  background: linear-gradient(135deg, rgba(130, 40, 220, 0.5), rgba(100, 20, 180, 0.6));
  border: 1px solid rgba(160, 60, 255, 0.4);
  border-radius: 6px;
  color: #e2d4ff;
  padding: 7px 20px;
  cursor: pointer;
  transition: all 0.15s;
}
.save-btn:hover {
  background: linear-gradient(135deg, rgba(160, 60, 255, 0.5), rgba(120, 30, 210, 0.65));
  box-shadow: 0 0 14px rgba(160, 60, 255, 0.35);
}
</style>