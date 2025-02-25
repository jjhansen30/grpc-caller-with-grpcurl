from tkinter import ttk

class EnvironVarView(ttk.Frame):
    """
    A simple placeholder view that displays:
    "No functionality implemented yet."
    """
    def __init__(self, parent):
        super().__init__(parent)
        label = ttk.Label(self, text="No functionality implemented yet.", font=("Arial", 14))
        label.pack(expand=True)