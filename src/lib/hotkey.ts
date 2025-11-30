import { register } from '@tauri-apps/plugin-global-shortcut';
import { getCurrentWindow } from '@tauri-apps/api/window';

export async function setupHotkey() {
  await register("Ctrl+Space", async () => {
    const win = getCurrentWindow();
    if (!(await win.isVisible())) {
      await win.show();
    }
    await win.setFocus();
  });
}
