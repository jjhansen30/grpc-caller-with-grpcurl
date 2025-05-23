import json
import tkinter as tk
import os
import subprocess
from tkinter import ttk
from google.protobuf.descriptor import Descriptor
from google.protobuf import descriptor_pb2
from environments_page import substitute_env_vars, EnvironmentRepo

class GrpcCaller:
    """Handles construction and execution of the grpcurl command."""
    def build_command(self, plaintext, cookie, bearer_token, protoset, server, method, body):
        command = ["grpcurl"]
        if plaintext:
            command.append("-plaintext")
        if cookie:
            command.extend(["-H", f"Cookie:s={cookie}"])
        elif bearer_token:
            command.extend(["-H", f"authorization: Bearer {bearer_token}"])
        command.extend(["--protoset", protoset])
        if body:
            command.extend(["-d", body])
        command.append(server)
        command.append(method)
        return command

    def execute_call(self, plaintext, cookie, bearer_token, protoset, server, call_name, body):
        command = self.build_command(plaintext, cookie, bearer_token, protoset, server, call_name, body)
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr, command
        except Exception as e:
            return None, "", f"Error while running grpcurl: {e}", command

class SavedGrpcManager:
    """Manages persistence of grpcurl call details."""
    def __init__(self, history_file: str):
        self.history_file = history_file
        self.saved_calls = []

    def load_saved_calls(self) -> list:
        if not os.path.exists(self.history_file):
            self.saved_calls = []
        else:
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.saved_calls = data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                self.saved_calls = []
        return self.saved_calls

    def save_call(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.saved_calls, f, indent=4)
        except IOError as e:
            raise Exception(f"Error saving history: {e}")

    def append_call(self, call_info):
        self.saved_calls.append(call_info)
        self.save_call()

    def update_call(self, index, call_info):
        if index < 0 or index >= len(self.saved_calls):
            raise IndexError("Invalid call index")
        self.saved_calls[index] = call_info
        self.save_call()

    def get_display_text(self, call_info: dict):
        return (f"{call_info.get('method', '')}")

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

        # --- Updated Environment Drop Down ---
        ttk.Label(self.input_frame, text="Environment").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.environment_var = tk.StringVar()  # new dedicated variable
        self.environment_drop_down = ttk.Combobox(self.input_frame, textvariable=self.environment_var, width=48, state='readonly')
        self.environment_drop_down.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        # ---------------------------------------

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

    # --- New helper methods for Environment drop down ---
    def set_environment_options(self, options):
        self.environment_drop_down['values'] = options
        if options:
            self.environment_var.set(options[0])
        else:
            self.environment_var.set("")

    def get_selected_environment(self):
        return self.environment_var.get()
    # ---------------------------------------------------

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
            for field_name, widget_info in self.dynamic_body_fields.items():
                widget_type = widget_info["widget_type"]
                widget_ref = widget_info["widget_ref"]
                # Get the stripped value
                field_value = widget_ref.get().strip()
                if field_value:
                    body_dict[field_name] = field_value

        return json.dumps(body_dict) if body_dict else ""

    # Methods for the Presenter to update the view
    def set_call_names(self, call_names):
        self.call_dropdown['values'] = call_names
        if call_names:
            self.method_var.set(call_names[0])
        else:
            self.method_var.set("")

    def build_body_fields(self, fields_with_enums):
        for widget in self.body_fields_frame.winfo_children():
            widget.destroy()
        self.dynamic_body_fields = {}

        if not fields_with_enums:
            ttk.Label(self.body_fields_frame, text="(No body fields required for this method)").grid(row=0, column=0, sticky=tk.W)
            return

        ttk.Label(self.body_fields_frame, text="BODY").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=2)

        for row_index, (field_desc, enum_values) in enumerate(fields_with_enums, start=1):
            field_name = field_desc.name
            ttk.Label(self.body_fields_frame, text=f"{field_name}:").grid(row=row_index, column=0, sticky=tk.W, padx=(0, 5), pady=2)

            if enum_values:
                combobox = ttk.Combobox(self.body_fields_frame, values=enum_values, width=48, state='readonly')
                combobox.grid(row=row_index, column=1, sticky=tk.W, pady=2)
                self.dynamic_body_fields[field_name] = {
                    "widget_type": "combo",
                    "widget_ref": combobox
                }
            else:
                entry = ttk.Entry(self.body_fields_frame, width=50)
                entry.grid(row=row_index, column=1, sticky=tk.W, pady=2)
                self.dynamic_body_fields[field_name] = {
                    "widget_type": "entry",
                    "widget_ref": entry
                }

    def populate_body_fields(self, body_data):
        if not hasattr(self, 'dynamic_body_fields') or not body_data:
            return

        for key, value in body_data.items():
            if key in self.dynamic_body_fields:
                widget_type = self.dynamic_body_fields[key]["widget_type"]
                widget_ref = self.dynamic_body_fields[key]["widget_ref"]
                if widget_type == "combo":
                    widget_ref.set(value)
                else:
                    widget_ref.delete(0, tk.END)
                    widget_ref.insert(0, value)

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
        enums = {}

        def add_messages(prefix, message_list, enum_list):
            for msg in message_list:
                full_msg_name = f"{prefix}.{msg.name}" if prefix else msg.name
                messages[full_msg_name] = msg
                add_messages(full_msg_name, msg.nested_type, msg.enum_type)
            for en in enum_list:
                full_enum_name = f"{prefix}.{en.name}" if prefix else en.name
                enums[full_enum_name] = en

        for file_desc in fds.file:
            package = file_desc.package.strip() if file_desc.package else ""
            add_messages(package, file_desc.message_type, file_desc.enum_type)

        parts = call_name.split('.')
        if len(parts) < 2:
            return []
        method_name = parts[-1]
        service_name = parts[-2]
        package = ".".join(parts[:-2])

        input_msg = None
        for file_desc in fds.file:
            file_package = file_desc.package.strip() if file_desc.package else ""
            if package and file_package != package:
                continue
            for service in file_desc.service:
                if service.name == service_name:
                    for method in service.method:
                        if method.name == method_name:
                            input_type = method.input_type.lstrip('.')
                            input_msg = messages.get(input_type)
                            break

        if not input_msg:
            return []

        output = []
        for field in input_msg.field:
            if field.type == descriptor_pb2.FieldDescriptorProto.TYPE_ENUM:
                enum_type_name = field.type_name.lstrip('.')
                enum_descriptor = enums.get(enum_type_name)
                if enum_descriptor:
                    possible_values = [v.name for v in enum_descriptor.value]
                else:
                    possible_values = []
                output.append((field, possible_values))
            else:
                output.append((field, []))

        return output

class GrpcCallPresenter:
    """
    The Presenter in the MVP pattern. It responds to view events,
    calls the model/service classes as needed, and then instructs the view to update.
    """
    def __init__(self, view: GrpcUrlView, protoset_parser: ProtosetParser, env_model: EnvironmentRepo):
        self.view = view
        self.grpc_caller = GrpcCaller()
        self.saved_calls_manager = SavedGrpcManager("grpc_calls.json")
        self.protoset_parser = protoset_parser
        self.env_model = env_model
        self.calls_history = self.saved_calls_manager.load_saved_calls()
        self.saved_body = None

        # Register callbacks for various UI events.
        self.view.set_on_protoset_change(self.handle_protoset_change)
        self.view.set_on_method_select(self.handle_method_select)
        self.view.set_on_make_call(self.handle_make_call)
        self.view.set_on_save_call(self.handle_save_call)
        self.view.set_on_edit_call(self.handle_edit_call)
        self.view.set_on_saved_call_select(self.handle_saved_call_select)

        self.view.update_saved_calls_list(self.calls_history, self.saved_calls_manager.get_display_text)

        # --- NEW: Initialize the environment drop down with the current options ---
        initial_env_names = self.env_model.get_all_environment_names()
        self.refresh_environment_options(initial_env_names)

    # NEW helper to update the drop down options.
    def refresh_environment_options(self, env_names):
        self.view.set_environment_options(env_names)

    def handle_protoset_change(self, protoset_path):
        if not protoset_path or not os.path.exists(protoset_path):
            self.view.set_call_names([])
            return
        call_names = self.protoset_parser.get_call_names(protoset_path)
        self.view.set_call_names(call_names)

    def handle_method_select(self, call_name, protoset_path):
        if not call_name or not protoset_path or not os.path.exists(protoset_path):
            return
        fields_with_enums = self.protoset_parser.get_method_request_fields(protoset_path, call_name)
        self.view.build_body_fields(fields_with_enums)
        if self.saved_body:
            self.view.populate_body_fields(self.saved_body)
            self.saved_body = None

    def handle_make_call(self):
        details = self.view.get_call_details()
        body = self.view.get_body_data()

        # Retrieve environment variables from the selected environment
        selected_env = self.view.get_selected_environment()
        env_vars = self.env_model.get_environment(selected_env) if selected_env else {}

        # Apply substitution on all details and body using the decoupled utility
        for key, value in details.items():
            details[key] = substitute_env_vars(value, env_vars)
        if body:
            body = substitute_env_vars(body, env_vars)

        # Check if any unsubstituted placeholders remain
        unsubstituted_fields = []
        for key, value in details.items():
            if "{{" in value or "}}" in value:
                unsubstituted_fields.append(key)
        if body and ("{{" in body or "}}" in body):
            unsubstituted_fields.append("body")
        if unsubstituted_fields:
            self.view.display_output(
                "Error: Unsubstituted environment variables found in fields: " +
                ", ".join(unsubstituted_fields) +
                ". Please define the missing variables."
            )
            return

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
        protoset_path = call_info.get("protoset", "")
        method_name = call_info.get("method", "")
        if protoset_path and method_name and os.path.exists(protoset_path):
            fields_with_enums = self.protoset_parser.get_method_request_fields(protoset_path, method_name)
            self.view.build_body_fields(fields_with_enums)
            if self.saved_body:
                self.view.populate_body_fields(self.saved_body)
                self.saved_body = None

class MockMainView(tk.Tk):
    """
    Main application window that holds a Notebook with separate pages.
    """
    def __init__(self):
        super().__init__()
        self.title("API Caller with gRPCurl and curl")
        self.geometry("900x900")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook_padding = 8

        self.grpcurl_page = GrpcUrlView(self.notebook)
        self.environment_page = EnvironVarView(self.notebook)

        self.notebook.add(self.grpcurl_page, text="grpcurl", padding=self.notebook_padding)
        self.notebook.add(self.environment_page, text="Environment variables", padding=self.notebook_padding)

        self.model = EnvironmentRepo("data/environments.json")
        self.grpcurl_page.set_environment_options(self.model.get_all_environment_names())

if __name__ == "__main__":
    from environments_page import EnvironVarView, EnvironmentRepo, EnvironmentPresenter
    protoset_parser = ProtosetParser()
    main_view = MockMainView()
    
    # First, create the gRPC presenter.
    grpc_presenter = GrpcCallPresenter(
        main_view.grpcurl_page,
        protoset_parser,
        main_view.model
    )
    
    # Then, create the Environment presenter and pass the gRPC presenter's refresh method as callback.
    env_presenter = EnvironmentPresenter(
        main_view.environment_page,
        main_view.model,
        on_change_callback=grpc_presenter.refresh_environment_options
    )
    
    main_view.mainloop()