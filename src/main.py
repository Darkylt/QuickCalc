import tkinter as tk

import keyboard


class QuickCalc:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.root.title("QuickCalc")
        self.root.geometry("400x100")
        self.root.configure(bg="#333333")
        self.root.attributes("-topmost", True)

        self.text_var = tk.StringVar()
        self.entry = tk.Entry(
            self.root,
            textvariable=self.text_var,
            font=("Arial", 16),
            bg="#333333",
            fg="white",
            insertbackground="white",
        )
        self.entry.pack(expand=True, fill="both", padx=10, pady=10)
        self.entry.bind("<Return>", self.calculate)

        keyboard.add_hotkey("F18", self.show_window)

    def show_window(self):
        print("Showing window")
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_set()

    def hide_window(self):
        print("Hiding window")
        self.root.withdraw()

    def calculate(self, event=None):
        text = self.text_var.get()
        if text.endswith("="):
            try:
                result = str(eval(text[:-1]))
                self.text_var.set(text + result)
            except Exception as e:
                print("Error:", e)

    def run(self):
        self.root.mainloop()


# Start app
app = QuickCalc()
app.run()
