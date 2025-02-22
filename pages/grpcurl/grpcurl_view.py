import tkinter as tk
from tkinter import ttk
import json

class GrpcUrlView(ttk.Frame):
    """
    The grpcurl page view with full functionality.
    This is the only page that retains the original UI and logic.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Input frame for gRPC call details
        self.input_frame = ttk.Frame(self.content_frame)
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)
        self.port_forward_var = tk.StringVar()
        self.cookie_var = tk.StringVar()
        self.bearer_token_var = tk.StringVar()
        self.protoset_var = tk.StringVar()
        self.server_var = tk.StringVar()
        self.method_var = tk.StringVar()
        self.plaintext_var = tk.BooleanVar(value=False)

        # Port Forward Command
        ttk.Label(self.input_frame, text="Port Forward Command:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.port_forward_entry = ttk.Entry(self.input_frame, textvariable=self.port_forward_var, width=50)
        self.port_forward_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        clear_pf = ttk.Label(self.input_frame, text="x", foreground="red", cursor="hand2")
        clear_pf.grid(row=0, column=2, sticky=tk.W, pady=2)
        clear_pf.bind("<Button-1>", lambda e: self.port_forward_var.set(""))

        # Authorization Cookie
        ttk.Label(self.input_frame, text="Authorization Cookie (s=):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cookie_entry = ttk.Entry(self.input_frame, textvariable=self.cookie_var, width=50)
        self.cookie_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        clear_cookie = ttk.Label(self.input_frame, text="x", foreground="red", cursor="hand2")
        clear_cookie.grid(row=1, column=2, sticky=tk.W, pady=2)
        clear_cookie.bind("<Button-1>", lambda e: self.cookie_var.set(""))

        # Bearer Token
        ttk.Label(self.input_frame, text="Bearer Token:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.token_entry = ttk.Entry(self.input_frame, textvariable=self.bearer_token_var, width=50)
        self.token_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        clear_token = ttk.Label(self.input_frame, text="x", foreground="red", cursor="hand2")
        clear_token.grid(row=2, column=2, sticky=tk.W, pady=2)
        clear_token.bind("<Button-1>", lambda e: self.bearer_token_var.set(""))

        # Protoset File Path
        ttk.Label(self.input_frame, text="Protoset File Path:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.protoset_entry = ttk.Entry(self.input_frame, textvariable=self.protoset_var, width=50)
        self.protoset_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        clear_protoset = ttk.Label(self.input_frame, text="x", foreground="red", cursor="hand2")
        clear_protoset.grid(row=3, column=2, sticky=tk.W, pady=2)
        clear_protoset.bind("<Button-1>", lambda e: self.protoset_var.set(""))

        # Server Address
        ttk.Label(self.input_frame, text="Server Address:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.server_entry = ttk.Entry(self.input_frame, textvariable=self.server_var, width=50)
        self.server_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        clear_server = ttk.Label(self.input_frame, text="x", foreground="red", cursor="hand2")
        clear_server.grid(row=4, column=2, sticky=tk.W, pady=2)
        clear_server.bind("<Button-1>", lambda e: self.server_var.set(""))

        # Method (Call Name)
        ttk.Label(self.input_frame, text="Method:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.call_dropdown = ttk.Combobox(self.input_frame, textvariable=self.method_var, width=48, state='readonly')
        self.call_dropdown.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)

        # -plaintext Checkbox
        self.plaintext_checkbox = ttk.Checkbutton(self.input_frame, text="Use -plaintext", variable=self.plaintext_var)
        self.plaintext_checkbox.grid(row=6, column=1, sticky=tk.W, pady=5)

        # Saved Calls Listbox
        self.saved_call_frame = ttk.Frame(self.content_frame)
        self.saved_call_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ttk.Label(self.saved_call_frame, text="Saved Calls:").pack(anchor=tk.W)
        self.saved_call_list_box = tk.Listbox(self.saved_call_frame, height=6)
        self.saved_call_list_box.pack(fill=tk.X, pady=5)

        # Dynamic Body Fields Frame
        self.body_fields_frame = ttk.Frame(self.content_frame)
        self.body_fields_frame.pack(fill=tk.X, padx=10, pady=5)

        # Action Buttons
        self.button_frame = ttk.Frame(self.content_frame)
        self.button_frame.pack(fill=tk.X, padx=10, pady=5)
        self.make_call_button = ttk.Button(self.button_frame, text="Make gRPC Call")
        self.make_call_button.pack(side=tk.LEFT, padx=(0, 10))
        self.save_call_button = ttk.Button(self.button_frame, text="Save Call")
        self.save_call_button.pack(side=tk.LEFT, padx=(0, 10))
        self.edit_call_button = ttk.Button(self.button_frame, text="Edit Call")
        self.edit_call_button.pack(side=tk.LEFT)

        # Output text area
        self.output_frame = ttk.Frame(self.content_frame)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ttk.Label(self.output_frame, text="Output:").pack(anchor=tk.W)
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # --- Internal event wiring ---
        self.protoset_var.trace_add("write", lambda *args: self._on_protoset_change())
        self.method_var.trace_add("write", lambda *args: self._on_method_select())
        self.saved_call_list_box.bind("<<ListboxSelect>>", lambda e: self._on_saved_call_select())

    # Methods to allow the Presenter to register callbacks
    def set_on_protoset_change(self, handler):
        self._external_protoset_change = handler

    def set_on_method_select(self, handler):
        self._external_method_select = handler

    def set_on_make_call(self, handler):
        self.make_call_button.config(command=handler)

    def set_on_save_call(self, handler):
        self.save_call_button.config(command=handler)

    def set_on_edit_call(self, handler):
        self.edit_call_button.config(command=handler)

    def set_on_saved_call_select(self, handler):
        self._external_saved_call_select = handler

    # Internal handlers that forward events to the Presenter if a callback is registered
    def _on_protoset_change(self):
        if hasattr(self, "_external_protoset_change") and callable(self._external_protoset_change):
            self._external_protoset_change(self.protoset_var.get().strip())

    def _on_method_select(self):
        if hasattr(self, "_external_method_select") and callable(self._external_method_select):
            self._external_method_select(self.method_var.get().strip(), self.protoset_var.get().strip())

    def _on_saved_call_select(self):
        if hasattr(self, "_external_saved_call_select") and callable(self._external_saved_call_select):
            selection = self.saved_call_list_box.curselection()
            self._external_saved_call_select(selection)

    # Getter methods for input fields (the Presenter can query these)
    def get_call_details(self):
        return {
            "port_forward": self.port_forward_var.get().strip(),
            "cookie": self.cookie_var.get().strip(),
            "bearer_token": self.bearer_token_var.get().strip(),
            "protoset": self.protoset_var.get().strip(),
            "server": self.server_var.get().strip(),
            "method": self.method_var.get().strip()
        }

    def get_body_data(self):
        body_dict = {}
        if hasattr(self, 'dynamic_body_fields'):
            for field_name, entry in self.dynamic_body_fields.items():
                body_dict[field_name] = entry.get().strip()
        return json.dumps(body_dict) if body_dict else ""

    # Methods for the Presenter to update the view
    def set_call_names(self, call_names):
        self.call_dropdown['values'] = call_names
        if call_names:
            self.method_var.set(call_names[0])
        else:
            self.method_var.set("")

    def build_body_fields(self, fields):
        for widget in self.body_fields_frame.winfo_children():
            widget.destroy()
        self.dynamic_body_fields = {}
        if not fields:
            ttk.Label(self.body_fields_frame, text="(No body fields required for this method)").grid(row=0, column=0, sticky=tk.W)
        else:
            ttk.Label(self.body_fields_frame, text="BODY").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)
            for row, field in enumerate(fields, start=1):
                field_name = field.name
                ttk.Label(self.body_fields_frame, text=f"{field_name}:").grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=2)
                entry = ttk.Entry(self.body_fields_frame, width=50)
                entry.grid(row=row, column=1, sticky=tk.W, pady=2)
                self.dynamic_body_fields[field_name] = entry

    def populate_body_fields(self, body_data):
        if hasattr(self, 'dynamic_body_fields'):
            for key, value in body_data.items():
                if key in self.dynamic_body_fields:
                    self.dynamic_body_fields[key].delete(0, tk.END)
                    self.dynamic_body_fields[key].insert(0, value)

    def display_output(self, text):
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)

    def update_saved_calls_list(self, saved_calls, get_display_text):
        self.saved_call_list_box.delete(0, tk.END)
        for call_info in saved_calls:
            display_text = get_display_text(call_info)
            self.saved_call_list_box.insert(tk.END, display_text)

    def set_input_fields(self, call_info):
        self.port_forward_var.set(call_info.get("port_forward", ""))
        self.cookie_var.set(call_info.get("cookie", ""))
        self.bearer_token_var.set(call_info.get("bearer_token", ""))
        self.protoset_var.set(call_info.get("protoset", ""))
        self.server_var.set(call_info.get("server", ""))
        self.method_var.set(call_info.get("method", ""))
