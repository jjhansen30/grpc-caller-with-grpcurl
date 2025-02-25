import tkinter as tk
from tkinter import ttk

class EnvironVarView(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.add_button_row = 2
        self._setup_ui()
    
    def _setup_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        environment_frame = ttk.Frame(main_container)
        environment_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.var_config_frame = ttk.Frame(main_container)
        self.var_config_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8)

        # Configure grid columns to expand equally along the x-axis
        self.var_config_frame.columnconfigure(0, weight=1)
        self.var_config_frame.columnconfigure(1, weight=1)

        # Environment list box
        ttk.Label(environment_frame, text="Environments").pack(anchor=tk.W)
        environment_list_box = tk.Listbox(environment_frame)
        environment_list_box.pack(fill=tk.BOTH, expand=True)

        # Variable configuration header
        ttk.Label(self.var_config_frame, text="Variable").grid(row=0, column=0, sticky="ew")
        ttk.Label(self.var_config_frame, text="Value").grid(row=0, column=1, sticky="ew")

        # Initial row of entry boxes for variable configuration
        variable_entry = ttk.Entry(self.var_config_frame)
        variable_entry.grid(row=1, column=0, sticky="ew")
        value_entry = ttk.Entry(self.var_config_frame)
        value_entry.grid(row=1, column=1, sticky="ew")

        # Adds more rows of text entries
        self.add_row_label = ttk.Label(self.var_config_frame, text="+", cursor="hand2")
        self.add_row_label.grid(row=self.add_button_row, column=0, sticky=tk.W)
        self.add_row_label.bind("<Button-1>", self.add_row)

        # Save environment
        self.save_button = ttk.Label(self.var_config_frame, text="Save", foreground="white", cursor="hand2")
        self.save_button.grid(row=self.add_button_row, column=1, sticky=tk.E)

    def add_row(self, event):
        # Insert a new row of entry boxes at the current add button row
        row_to_add = self.add_button_row
        variable_entry = ttk.Entry(self.var_config_frame)
        variable_entry.grid(row=row_to_add, column=0, sticky="ew")
        value_entry = ttk.Entry(self.var_config_frame)
        value_entry.grid(row=row_to_add, column=1, sticky="ew")
        
        # Update the row index and move the '+' and 'Save' labels below the new entries
        self.add_button_row += 1
        self.add_row_label.grid(row=self.add_button_row, column=0, sticky="ew")
        self.save_button.grid(row=self.add_button_row, column=1, sticky="ew")


class _MockParent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("API Caller with gRPCurl and curl")
        self.geometry("900x900")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.environment_view = EnvironVarView(self.notebook)
        self.notebook.add(self.environment_view, text="Environment Variables")


if __name__ == "__main__":
    mock_parent = _MockParent()
    mock_parent.mainloop()

