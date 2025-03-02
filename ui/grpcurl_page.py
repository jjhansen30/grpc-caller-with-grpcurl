import json
import tkinter as tk
import os
from tkinter import ttk
from google.protobuf.descriptor import Descriptor
from google.protobuf import descriptor_pb2
from data.saved_grpc_manager import SavedGrpcManager
from network.grpc_caller import GrpcCaller

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
        self.content_frame.pack(fill=tk.BOTH, expand=True)

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

class ProtosetParser:
    """Handles reading a protoset file and extracting call names and request fields."""
    @staticmethod
    def get_call_names(protoset_path):
        call_names = []
        try:
            with open(protoset_path, "rb") as f:
                fds = descriptor_pb2.FileDescriptorSet()
                fds.ParseFromString(f.read())
            for file_desc in fds.file:
                package_prefix = file_desc.package.strip() if file_desc.package else ""
                for service in file_desc.service:
                    full_service_name = f"{package_prefix}.{service.name}" if package_prefix else service.name
                    for method in service.method:
                        call_names.append(f"{full_service_name}.{method.name}")
            return call_names
        except Exception:
            return []

    @staticmethod
    def get_method_request_fields(protoset_path, call_name):
        try:
            with open(protoset_path, "rb") as f:
                fds = descriptor_pb2.FileDescriptorSet()
                fds.ParseFromString(f.read())
        except Exception:
            return []

        messages = {}

        def add_messages(prefix, message_list):
            for msg in message_list:
                full_name = f"{prefix}.{msg.name}" if prefix else msg.name
                messages[full_name] = msg
                add_messages(full_name, msg.nested_type)

        for file_desc in fds.file:
            package = file_desc.package.strip() if file_desc.package else ""
            add_messages(package, file_desc.message_type)

        parts = call_name.split('.')
        if len(parts) < 2:
            return []
        method_name = parts[-1]
        service_name = parts[-2]
        package = ".".join(parts[:-2])

        for file_desc in fds.file:
            file_package = file_desc.package.strip() if file_desc.package else ""
            if package and file_package != package:
                continue
            for service in file_desc.service:
                if service.name == service_name:
                    for method in service.method:
                        if method.name == method_name:
                            input_type = method.input_type.lstrip('.')
                            msg_descriptor = messages.get(input_type)
                            if msg_descriptor:
                                return msg_descriptor.field
                            else:
                                return []
        return []

class GrpcCallPresenter:
    """
    The Presenter in the MVP pattern. It responds to view events,
    calls the model/service classes as needed, and then instructs the view to update.
    """
    def __init__(self, view: GrpcUrlView, grpc_caller: GrpcCaller, saved_calls_manager: SavedGrpcManager, protoset_parser: ProtosetParser):
        self.view = view
        self.grpc_caller = grpc_caller
        self.saved_calls_manager = saved_calls_manager
        self.protoset_parser = protoset_parser
        self.calls_history = self.saved_calls_manager.load_saved_calls()
        self.saved_body = None

        # Register callbacks from the view.
        self.view.set_on_protoset_change(self.handle_protoset_change)
        self.view.set_on_method_select(self.handle_method_select)
        self.view.set_on_make_call(self.handle_make_call)
        self.view.set_on_save_call(self.handle_save_call)
        self.view.set_on_edit_call(self.handle_edit_call)
        self.view.set_on_saved_call_select(self.handle_saved_call_select)

        # Initialize the saved calls list.
        self.view.update_saved_calls_list(self.calls_history, self.saved_calls_manager.get_display_text)

    def handle_protoset_change(self, protoset_path):
        if not protoset_path or not os.path.exists(protoset_path):
            self.view.set_call_names([])
            return
        call_names = self.protoset_parser.get_call_names(protoset_path)
        self.view.set_call_names(call_names)

    def handle_method_select(self, call_name, protoset_path):
        if not call_name or not protoset_path or not os.path.exists(protoset_path):
            return
        fields = self.protoset_parser.get_method_request_fields(protoset_path, call_name)
        self.view.build_body_fields(fields)
        if self.saved_body:
            self.view.populate_body_fields(self.saved_body)
            self.saved_body = None

    def handle_make_call(self):
        details = self.view.get_call_details()
        body = self.view.get_body_data()
        if not details["protoset"] or not details["server"] or not details["method"]:
            self.view.display_output("Error: Missing required fields (Protoset, Server, or Call Name).\n")
            return

        return_code, stdout, stderr, command = self.grpc_caller.execute_call(
            self.view.plaintext_var.get(),
            details["cookie"],
            details["bearer_token"],
            details["protoset"],
            details["server"],
            details["method"],
            body
        )
        output = f"Executing command: {' '.join(command)}\n\n"
        if return_code is None or return_code != 0:
            output += f"Command failed with return code {return_code}.\n"
            if stderr.strip():
                output += f"stderr:\n{stderr}\n"
        else:
            output += f"stdout:\n{stdout}\n"
            if stderr.strip():
                output += f"stderr:\n{stderr}\n"
        self.view.display_output(output)

    def handle_save_call(self):
        details = self.view.get_call_details()
        details["body"] = self.view.get_body_data()
        self.saved_calls_manager.append_call(details)
        self.calls_history = self.saved_calls_manager.load_saved_calls()
        self.view.update_saved_calls_list(self.calls_history, self.saved_calls_manager.get_display_text)

    def handle_edit_call(self):
        selection = self.view.saved_call_list_box.curselection()
        if not selection:
            self.view.display_output("No saved call selected to edit.\n")
            return
        index = selection[0]
        details = self.view.get_call_details()
        details["body"] = self.view.get_body_data()
        try:
            self.saved_calls_manager.update_call(index, details)
            self.calls_history = self.saved_calls_manager.load_saved_calls()
            self.view.update_saved_calls_list(self.calls_history, self.saved_calls_manager.get_display_text)
            self.view.display_output(f"Saved call at index {index} updated successfully.\n")
        except Exception as e:
            self.view.display_output(f"Error updating call: {e}\n")

    def handle_saved_call_select(self, selection):
        if not selection:
            return
        index = selection[0]
        call_info = self.calls_history[index]
        self.view.set_input_fields(call_info)
        body_str = call_info.get("body", "")
        if body_str:
            try:
                self.saved_body = json.loads(body_str)
            except Exception:
                self.saved_body = None
        else:
            self.saved_body = None
        self.view.populate_body_fields(self.saved_body)