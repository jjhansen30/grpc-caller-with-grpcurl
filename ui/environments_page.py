import json
import os
import constants as c
import tkinter as tk
from tkinter import ttk

# Model: Handles JSON file operations.
class EnvironmentModel:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}
        else:
            self.data = {}

    def save_environment(self, env_name, variables):
        # Save (or update) the environment in the model.
        self.data[env_name] = variables
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_environment(self, env_name):
        return self.data.get(env_name, {})

    def get_all_environment_names(self):
        return list(self.data.keys())

# View: Displays the UI and exposes methods for data access and update.
class EnvironVarView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.presenter = None
        self.variable_entries = []
        self.value_entries = []
        self._setup_ui()

    def _setup_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side: Environment list box.
        environment_frame = ttk.Frame(main_container)
        environment_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        ttk.Label(environment_frame, text="Environments").pack(anchor=tk.W)
        self.env_list_box = tk.Listbox(environment_frame)
        self.env_list_box.pack(fill=tk.BOTH, expand=True)
        self.env_list_box.bind("<<ListboxSelect>>", self.on_listbox_select)

        # Right side: Environment and variable entries.
        self.var_config_frame = ttk.Frame(main_container)
        self.var_config_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8)
        self.var_config_frame.columnconfigure(0, weight=1)
        self.var_config_frame.columnconfigure(1, weight=1)

        # Environment Name label and entry.
        ttk.Label(self.var_config_frame, text="Environment Name", anchor="center") \
            .grid(row=0, column=0, columnspan=2, pady=(5,2))
        self.env_entry = ttk.Entry(self.var_config_frame, justify="center")
        self.env_entry.grid(row=1, column=0, columnspan=2, pady=(0,10))

        # Variable configuration headers.
        ttk.Label(self.var_config_frame, text="Variable").grid(row=2, column=0, sticky="ew")
        ttk.Label(self.var_config_frame, text="Value").grid(row=2, column=1, sticky="ew")

        # Initial row for variable configuration.
        var_entry = ttk.Entry(self.var_config_frame)
        var_entry.grid(row=3, column=0, sticky="ew")
        self.variable_entries.append(var_entry)
        val_entry = ttk.Entry(self.var_config_frame)
        val_entry.grid(row=3, column=1, sticky="ew")
        self.value_entries.append(val_entry)

        # Set the starting row index for add row and save button.
        self.add_button_row = 4

        # Add row label (to add more variable rows).
        self.add_row_label = ttk.Label(self.var_config_frame, text="+", cursor="hand2")
        self.add_row_label.grid(row=self.add_button_row, column=0, sticky="ew")
        self.add_row_label.bind("<Button-1>", self.add_row)

        # Save button.
        self.save_button = ttk.Label(self.var_config_frame, text="Save", cursor="hand2")
        self.save_button.grid(row=self.add_button_row, column=1, sticky="ew")
        # Its callback will be set by the presenter.

    def add_row(self, event):
        # Create a new row of variable and value entries.
        row_to_add = self.add_button_row
        var_entry = ttk.Entry(self.var_config_frame)
        var_entry.grid(row=row_to_add, column=0, sticky="ew")
        self.variable_entries.append(var_entry)
        val_entry = ttk.Entry(self.var_config_frame)
        val_entry.grid(row=row_to_add, column=1, sticky="ew")
        self.value_entries.append(val_entry)
        
        self.add_button_row += 1
        self.add_row_label.grid(row=self.add_button_row, column=0, sticky="ew")
        self.save_button.grid(row=self.add_button_row, column=1, sticky="ew")

    def on_listbox_select(self, event):
        selection = self.env_list_box.curselection()
        if selection and self.presenter:
            index = selection[0]
            env_name = self.env_list_box.get(index)
            self.presenter.environment_selected(env_name)

    def set_save_callback(self, callback):
        self.save_button.bind("<Button-1>", callback)

    def set_presenter(self, presenter):
        self.presenter = presenter

    def get_environment_name(self):
        return self.env_entry.get().strip()

    def get_variables(self):
        # Retrieve variable and value pairs from the current rows.
        variables = {}
        for var_entry, val_entry in zip(self.variable_entries, self.value_entries):
            key = var_entry.get().strip()
            val = val_entry.get().strip()
            if key:
                variables[key] = val
        return variables

    def update_list_box(self, env_names):
        self.env_list_box.delete(0, tk.END)
        for name in env_names:
            self.env_list_box.insert(tk.END, name)

    def clear_variable_entries(self):
        # Remove current variable/value entry widgets.
        for widget in self.variable_entries + self.value_entries:
            widget.destroy()
        self.variable_entries = []
        self.value_entries = []

    def populate_variables(self, var_dict):
        # Remove any current variable entries.
        self.clear_variable_entries()
        # Starting row for variable entries.
        row_index = 3
        for key, value in var_dict.items():
            var_entry = ttk.Entry(self.var_config_frame)
            var_entry.insert(0, key)
            var_entry.grid(row=row_index, column=0, sticky="ew")
            self.variable_entries.append(var_entry)
            val_entry = ttk.Entry(self.var_config_frame)
            val_entry.insert(0, value)
            val_entry.grid(row=row_index, column=1, sticky="ew")
            self.value_entries.append(val_entry)
            row_index += 1
        # Reset the add row button and save button to follow the last entry.
        self.add_button_row = row_index
        self.add_row_label.grid(row=self.add_button_row, column=0, sticky="ew")
        self.save_button.grid(row=self.add_button_row, column=1, sticky="ew")
    
    # New method to update the environment name entry.
    def set_environment_name(self, name):
        self.env_entry.delete(0, tk.END)
        self.env_entry.insert(0, name)

# Presenter: Mediates between the View and Model.
class EnvironmentPresenter:
    def __init__(self, view: EnvironVarView, model: EnvironmentModel):
        self.view = view
        self.model = model
        self.view.set_presenter(self)
        self.view.set_save_callback(self.on_save)
        self.update_environment_list()

    def update_environment_list(self):
        env_names = self.model.get_all_environment_names()
        self.view.update_list_box(env_names)

    def on_save(self, event):
        env_name = self.view.get_environment_name()
        if not env_name:
            return
        variables = self.view.get_variables()
        self.model.save_environment(env_name, variables)
        self.update_environment_list()

    def environment_selected(self, env_name):
        # Update the environment name field when a list box item is selected.
        self.view.set_environment_name(env_name)
        env_data = self.model.get_environment(env_name)
        self.view.populate_variables(env_data)

# Main application
class _MockParent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("API Caller with gRPCurl and curl")
        self.geometry(c.GEOMETRY)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.environment_view = EnvironVarView(self.notebook)
        self.notebook.add(self.environment_view, text="Environment Variables")

        # Instantiate the Model and Presenter.
        self.model = EnvironmentModel(filename=c.SAVED_ENVIRONMENTS_FILE)
        self.presenter = EnvironmentPresenter(self.environment_view, self.model)

if __name__ == "__main__":
    mock_parent = _MockParent()
    mock_parent.mainloop()
