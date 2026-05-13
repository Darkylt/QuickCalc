<script lang="ts">
  import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
  const win = getCurrentWebviewWindow();

  export let onSettingsClick: () => void = () => {};

  function minimize() {
    win.minimize();
  }

  function close() {
    win.close();
  }
</script>

<div class="titlebar" data-tauri-drag-region>
  <div class="title">QuickCalc</div>

  <div class="window-controls">
    <button class="btn settings" on:click={onSettingsClick} title="Settings"
      >⚙</button
    >
    <button class="btn" on:click={minimize}>—</button>
    <button class="btn close" on:click={close}>×</button>
  </div>
</div>

<style>
  .titlebar {
    height: 42px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;

    background: linear-gradient(
      135deg,
      rgba(25, 12, 40, 0.95),
      rgba(40, 0, 65, 0.95),
      rgba(90, 0, 140, 0.9)
    );

    box-shadow:
      0 0 22px rgba(160, 60, 255, 0.25),
      0 0 6px rgba(120, 40, 200, 0.4) inset;

    backdrop-filter: blur(14px);
    -webkit-user-select: none;
    user-select: none;

    padding: 0 14px;
    box-sizing: border-box;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .title {
    font-family: "JetBrains Mono", monospace;
    font-size: 15px;
    letter-spacing: 0.5px;
    font-weight: 500;
    color: #d8cafa;
    text-shadow: 0 0 5px rgba(160, 60, 255, 0.4);
  }

  .window-controls {
    display: flex;
    gap: 8px;
  }

  .btn {
    width: 32px;
    height: 32px;
    border: none;
    outline: none;

    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    cursor: pointer;

    font-size: 18px;
    color: #e6d7ff;
    display: flex;
    align-items: center;
    justify-content: center;

    transition: all 0.15s ease;
  }

  .btn:hover {
    background: rgba(160, 60, 255, 0.18);
    box-shadow:
      0 0 10px rgba(160, 60, 255, 0.4),
      0 0 4px rgba(160, 60, 255, 0.5) inset;
    transform: translateY(-1px);
  }

  .settings:hover {
    background: rgba(160, 60, 255, 0.22);
    box-shadow:
      0 0 10px rgba(160, 60, 255, 0.4),
      0 0 4px rgba(160, 60, 255, 0.5) inset;
  }

  .close:hover {
    background: rgba(255, 70, 70, 0.25);
    color: #fff;
    box-shadow:
      0 0 10px rgba(255, 60, 60, 0.45),
      0 0 5px rgba(255, 70, 70, 0.6) inset;
  }
</style>
