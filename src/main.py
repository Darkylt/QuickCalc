import re
import sys
import threading
import tkinter as tk

import keyboard
import pyautogui
import sympy as simp
from PIL import Image
from pystray import Icon, Menu, MenuItem

import config_reader as config


class QuickCalc:
    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.root.withdraw()

        self.root.iconbitmap("assets/icon.ico")

        self.root.title("QuickCalc")
        self.root.geometry("400x120")
        self.root.minsize(400, 120)  # Set minimum width and height
        self.root.configure(bg="#333333")
        self.root.attributes("-topmost", True)

        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.text_var = tk.StringVar()
        self.suggestion_var = tk.StringVar()

        self.text_widget = tk.Text(
            self.root,
            font=("Arial", 16),
            bg="#333333",
            fg="white",
            insertbackground="white",
            wrap="word",
            height=2,
        )
        self.text_widget.pack(expand=True, fill="both", padx=10, pady=5)
        self.text_widget.bind("<KeyRelease>", self.update_suggestion)

        self.suggestion_label = tk.Label(
            self.root,
            textvariable=self.suggestion_var,
            font=("Arial", 14),
            bg="#333333",
            fg="gray",
            height=1,
        )
        self.suggestion_label.pack(fill="x", padx=10, pady=5)

        keyboard.add_hotkey(config.App.hotkey, self.show_window)
        keyboard.add_hotkey("tab", self.complete_calculation)

    def show_window(self):
        mouse_x, mouse_y = pyautogui.position()

        self.root.geometry(f"+{mouse_x}+{mouse_y}")

        self.root.after(
            0,
            lambda: [
                self.root.deiconify(),
                self.root.lift(),
                self.root.focus_force(),
                self.text_widget.focus_set(),
            ],
        )

    def hide_window(self):
        # print("Hiding window")
        self.root.withdraw()

    def update_suggestion(self, event=None):
        """Dynamically updates the suggestion label when typing"""
        text = self.text_widget.get("1.0", "end-1c")
        if text.endswith("="):
            try:
                match = re.search(r"([0-9+\-*/().]+)=$", text)
                if match:
                    expr = match.group(1)
                    result = simp.sympify(expr)

                    # Check if the result simplifies to an integer
                    if result.is_Integer:
                        self.suggestion_var.set(str(result))
                    elif result.is_real:
                        # Convert to string and strip trailing zeros
                        result_str = str(result.evalf())
                        self.suggestion_var.set(result_str.rstrip("0").rstrip("."))
                    else:
                        self.suggestion_var.set("")
                else:
                    self.suggestion_var.set("")
            except Exception:
                self.suggestion_var.set("")
        else:
            self.suggestion_var.set("")

    def complete_calculation(self, event=None):
        """Completes the calculation when Enter or Tab is pressed"""
        if self.suggestion_var.get():
            self.text_widget.insert("end", self.suggestion_var.get())
            self.suggestion_var.set("")
        return "break"

    def run(self):
        self.root.mainloop()


def create_tray_icon(app: QuickCalc):
    icon_image = Image.open("assets/icon.ico")
    tray_icon = Icon(
        "QuickCalc",
        icon_image,
        menu=Menu(MenuItem("Quit", lambda: quit_program(app, tray_icon))),
    )

    threading.Thread(target=tray_icon.run, daemon=True).start()


def quit_program(app: QuickCalc, tray_icon):
    """Properly quit the program"""
    app.hide_window()
    tray_icon.stop()
    app.root.quit()
    app.root.destroy()
