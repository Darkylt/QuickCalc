import os
import re
import sys
import threading
import tkinter as tk
from tkinter import simpledialog, ttk

import customtkinter as ctk
import keyboard
import pyautogui
import sympy as simp
from PIL import Image
from pystray import Icon, Menu, MenuItem

import config_reader as config

# Determine base path (supports both script & executable)
if getattr(sys, "frozen", False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(BASE_PATH, "icon.ico")


class QuickCalc:
    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.root.withdraw()
        self.root.title("QuickCalc")
        self.root.geometry("400x180")
        self.root.minsize(400, 180)
        self.root.configure(bg="#333333")
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

        if os.path.exists(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except tk.TclError:
                print(f"Error: Failed to load icon file at {ICON_PATH}")
        else:
            print(f"Warning: Icon file not found at {ICON_PATH}")

        self.tabs = {}
        self.current_tab = None
        self.tab_buttons = {}

        self.tab_frame = tk.Frame(self.root, bg="#444444")
        self.tab_frame.pack(fill="x", padx=5, pady=5)

        self.add_tab_button = ctk.CTkButton(
            self.tab_frame,
            text="+",
            command=self.add_tab,
            corner_radius=15,
            fg_color="#555555",
            text_color="white",
            hover_color="#666666",
            width=40,
            height=30,
        )
        self.add_tab_button.pack(side="right", padx=5, pady=5)

        self.text_var = tk.StringVar()
        self.suggestion_var = tk.StringVar()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.text_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#1a1a1a")
        self.text_frame.pack(expand=True, fill="both", padx=10, pady=5)

        self.text_widget = ctk.CTkTextbox(
            self.text_frame,
            font=("Arial", 16),
            fg_color="#1a1a1a",
            text_color="white",
            corner_radius=10,
            wrap="word",
            height=2,
        )
        self.text_widget.pack(expand=True, fill="both", padx=5, pady=5)
        self.text_widget.bind("<KeyRelease>", self.update_suggestion)
        self.text_widget.bind("<Delete>", lambda event: self.hide_window())

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

        self.add_tab("Tab 1")

    def add_tab(self, name=None):
        if name is None:
            # Generate a unique tab name
            base_name = "Tab"
            counter = 1
            while f"{base_name} {counter}" in self.tabs:
                counter += 1
            name = f"{base_name} {counter}"

        button = ctk.CTkButton(
            self.tab_frame,
            text=name,
            command=lambda n=name: self.switch_tab(n),
            corner_radius=15,
            fg_color="#555555",
            text_color="white",
            hover_color="#666666",
            width=80,
            height=30,
        )
        button.pack(side="left", padx=5, pady=5)
        button.bind("<Button-3>", lambda event, n=name: self.show_tab_menu(event, n))

        self.tabs[name] = ""
        self.tab_buttons[name] = button
        self.switch_tab(name)

    def switch_tab(self, name):
        if self.current_tab is not None:
            self.tabs[self.current_tab] = self.text_widget.get("1.0", "end-1c")
            self.tab_buttons[self.current_tab].configure(fg_color="#555555")

        self.current_tab = name
        self.tab_buttons[self.current_tab].configure(fg_color="#333333")

        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", self.tabs[name])
        self.update_suggestion()

    def show_tab_menu(self, event, tab_name):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Rename", command=lambda: self.rename_tab(tab_name))
        menu.add_command(label="Delete", command=lambda: self.delete_tab(tab_name))
        menu.post(event.x_root, event.y_root)

    def rename_tab(self, old_name):
        button = self.tab_buttons[old_name]

        button.pack_forget()

        entry = ctk.CTkEntry(
            self.tab_frame,
            font=("Arial", 12),
            fg_color="#555555",
            text_color="white",
            corner_radius=10,
        )
        entry.pack(side="left", padx=5, pady=5)
        entry.insert(0, old_name)
        entry.focus_set()

        def set_new_name(event=None):
            new_name = entry.get().strip()
            if new_name and new_name not in self.tabs:
                # Update the tabs dictionary
                self.tabs[new_name] = self.tabs.pop(old_name)

                # Update the button's text and command
                button.configure(
                    text=new_name, command=lambda n=new_name: self.switch_tab(n)
                )

                # Update the tab_buttons dictionary
                self.tab_buttons.pop(old_name)
                self.tab_buttons[new_name] = button

                # Rebind the right-click menu to the new name
                button.unbind("<Button-3>")
                button.bind(
                    "<Button-3>", lambda event, n=new_name: self.show_tab_menu(event, n)
                )

                # Destroy the entry widget and re-add the button
                entry.destroy()
                button.pack(side="left", padx=5, pady=5)

                # If the renamed tab is the current tab, update the current_tab reference
                if self.current_tab == old_name:
                    self.current_tab = new_name
            else:
                cancel_rename()

        def cancel_rename(event=None):
            entry.destroy()
            button.pack(side="left", padx=5, pady=5)

        entry.bind("<Return>", set_new_name)
        entry.bind("<Escape>", cancel_rename)

    def delete_tab(self, name):
        if len(self.tabs) > 1:  # Ensure there is more than one tab
            if name == self.current_tab:
                # Switch to another tab before deleting the current one
                remaining_tab = next(tab for tab in self.tabs if tab != name)
                self.switch_tab(remaining_tab)

            # Remove the tab and its button
            self.tabs.pop(name)
            self.tab_buttons[name].destroy()
            self.tab_buttons.pop(name)
        else:
            print("Cannot delete the last remaining tab.")

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
        self.root.withdraw()

    def update_suggestion(self, event=None):
        text = self.text_widget.get("1.0", "end-1c")
        if text.endswith("="):
            try:
                match = re.search(r"([0-9+\-*/().^]+)=$", text)
                if match:
                    expr = match.group(1)
                    expr = expr.replace("^", "**")
                    result = simp.sympify(expr)

                    if result.is_Integer:
                        self.suggestion_var.set(str(result))
                    elif result.is_real:
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
        if self.suggestion_var.get():
            self.text_widget.insert("end", self.suggestion_var.get())
            self.suggestion_var.set("")
        return "break"

    def run(self):
        self.root.mainloop()


def create_tray_icon(app: QuickCalc):
    icon_image = Image.open(ICON_PATH)
    tray_icon = Icon(
        "QuickCalc",
        icon_image,
        menu=Menu(MenuItem("Quit", lambda: quit_program(app, tray_icon))),
    )
    threading.Thread(target=tray_icon.run, daemon=True).start()


def quit_program(app: QuickCalc, tray_icon):
    app.hide_window()
    tray_icon.stop()
    app.root.quit()
    app.root.destroy()
