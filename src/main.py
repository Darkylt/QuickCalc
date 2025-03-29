import tkinter as tk

import keyboard
import sympy as sp


class QuickCalc:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.root.title("QuickCalc")
        self.root.geometry("400x120")
        self.root.configure(bg="#333333")
        self.root.attributes("-topmost", True)

        self.text_var = tk.StringVar()
        self.suggestion_var = tk.StringVar()

        self.entry = tk.Entry(
            self.root,
            textvariable=self.text_var,
            font=("Arial", 16),
            bg="#333333",
            fg="white",
            insertbackground="white",
        )
        self.entry.pack(expand=True, fill="both", padx=10, pady=5)
        self.entry.bind("<KeyRelease>", self.update_suggestion)

        self.suggestion_label = tk.Label(
            self.root,
            textvariable=self.suggestion_var,
            font=("Arial", 14),
            bg="#333333",
            fg="gray",
        )
        self.suggestion_label.pack(fill="x", padx=10, pady=5)

        keyboard.add_hotkey("F18", self.show_window)
        keyboard.add_hotkey("tab", self.complete_calculation)

    def show_window(self):
        print("Showing window")
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_set()

    def hide_window(self):
        print("Hiding window")
        self.root.withdraw()

    def update_suggestion(self, event=None):
        """Dynamically updates the suggestion label when typing"""
        text = self.text_var.get()
        if text.endswith("="):
            try:
                expr = text[:-1]
                result = sp.sympify(expr)

                # Check if the result simplifies to an integer
                if result.is_Integer:
                    self.suggestion_var.set(str(result))
                elif result.is_real:
                    # Convert to string and strip trailing zeros
                    result_str = str(result.evalf())
                    self.suggestion_var.set(result_str.rstrip("0").rstrip("."))
                else:
                    self.suggestion_var.set("")
            except Exception:
                self.suggestion_var.set("")
        else:
            self.suggestion_var.set("")

    def complete_calculation(self, event=None):
        """Completes the calculation when Enter or Tab is pressed"""
        if self.suggestion_var.get():
            self.text_var.set(self.text_var.get() + self.suggestion_var.get())
            self.suggestion_var.set("")

            self.entry.icursor(len(self.text_var.get()))
            self.entry.select_clear()
        return "break"

    def run(self):
        self.root.mainloop()


app = QuickCalc()
app.run()
