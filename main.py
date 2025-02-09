#!/usr/bin/env python3
"""
A Tkinter-based Python application to build and execute gRPC calls using grpcurl.
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import json
import os
from google.protobuf import descriptor_pb2


class ProtosetParser:
    """Encapsulates the logic of reading a protoset file and extracting call names and request fields."""
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
    #TODO this method is really messy. See if it can be cleaned up. 
    # Also check to see if it's possible to only return one thing, and not a list or Any.
    def get_method_request_fields(protoset_path, call_name):
        """
        Given a protoset file and a fully-qualified call name (e.g. "package.Service.Method"),
        returns a list of FieldDescriptorProto for the request message of the method.
        """
        try:
            with open(protoset_path, "rb") as f:
                fds = descriptor_pb2.FileDescriptorSet()
                fds.ParseFromString(f.read())
        except Exception:
            return []

        # Build a dictionary mapping fully-qualified message names to DescriptorProto.
        messages = {}

        def add_messages(prefix, message_list):
            for msg in message_list:
                full_name = f"{prefix}.{msg.name}" if prefix else msg.name
                messages[full_name] = msg
                # Recursively add nested types.
                add_messages(full_name, msg.nested_type)

        for file_desc in fds.file:
            package = file_desc.package.strip() if file_desc.package else ""
            add_messages(package, file_desc.message_type)

        # Parse the call_name. It was constructed as "full_service_name.method"
        parts = call_name.split('.')
        if len(parts) < 2:
            return []
        method_name = parts[-1]
        service_name = parts[-2]
        package = ".".join(parts[:-2])  # May be empty

        # Find the method descriptor by iterating over all file descriptors.
        for file_desc in fds.file:
            file_package = file_desc.package.strip() if file_desc.package else ""
            # Check package match if package is provided.
            if package and file_package != package:
                continue
            for service in file_desc.service:
                if service.name == service_name:
                    for method in service.method:
                        if method.name == method_name:
                            # Found the method; now get its input type.
                            input_type = method.input_type.lstrip('.')  # Remove any leading dot.
                            msg_descriptor = messages.get(input_type)
                            if msg_descriptor:
                                return msg_descriptor.field  # Returns a list of FieldDescriptorProto.
                            else:
                                return []
        return []


class GrpcCaller:
    """Handles construction and execution of the grpcurl command."""
    def build_command(self, plaintext, cookie, bearer_token, protoset, server, call_name, body):
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
        command.append(call_name)
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


class SavedCallsManager:
    """Manages persistence and formatting of grpcurl commands."""
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
        return (
            f"{call_info.get('server', '')} - "
            f"{call_info.get('call', '')} - "
            f"Body: {'Yes' if call_info.get('body') else 'No'}"
        )


class GrpcCallApp(tk.Tk):
    """
    The UI class that handles all user interaction. It relies on the GrpcCaller
    and SavedCallsManager instances that are injected into it.
    """
    def __init__(self, grpc_caller: GrpcCaller, saved_calls_manager: SavedCallsManager, protoset_parser: ProtosetParser):
        super().__init__()
        self.grpc_caller = grpc_caller
        self.saved_calls_manager = saved_calls_manager
        self.protoset_parser = protoset_parser

        self.title("gRPC Caller with grpcurl")
        self.geometry("900x600")
        self.is_history_selected = False
        self.selected_call_index = None  # Track the index of the currently selected call

        # Variables for input fields
        self.port_forward_var = tk.StringVar()
        self.cookie_var = tk.StringVar()
        self.bearer_token_var = tk.StringVar()
        self.protoset_var = tk.StringVar()
        self.server_var = tk.StringVar()
        self.call_var = tk.StringVar()
        self.plaintext_var = tk.BooleanVar(value=False)

        # Update Call Name dropdown when protoset path changes.
        self.protoset_var.trace_add("write", self.on_protoset_change)

        # Load history using SavedCallsManager
        self.calls_history = self.saved_calls_manager.load_saved_calls()

        # Main layout: side menu on the left, content frame on the right.
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Side Menu
        side_menu = ttk.Frame(main_container, width=150)
        side_menu.pack(side=tk.LEFT, fill=tk.Y)
        grpc_button = ttk.Button(side_menu, text="gRPC Caller", command=self.show_grpc_page)
        grpc_button.pack(padx=10, pady=10, fill=tk.X)
        hello_button = ttk.Button(side_menu, text="Hello World", command=self.show_hello_page)
        hello_button.pack(padx=10, pady=10, fill=tk.X)

        # Content Frame for pages.
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Initially show the gRPC caller page.
        self.show_grpc_page()

    def clear_content(self):
        """Destroy all widgets in the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_grpc_page(self):
        """Clear the content area and rebuild the gRPC caller UI."""
        self.clear_content()
        self.build_grpc_widgets()

    def show_hello_page(self):
        """Clear the content area and display a Hello World message."""
        self.clear_content()
        hello_label = ttk.Label(self.content_frame, text="Hello World", font=("Arial", 24))
        hello_label.pack(expand=True)

    def build_grpc_widgets(self):
        """Build all widgets associated with the gRPC caller UI."""
        # Frame for input fields
        input_frame = ttk.Frame(self.content_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Port Forward Command
        ttk.Label(input_frame, text="Port Forward Command:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.port_forward_entry = ttk.Entry(input_frame, textvariable=self.port_forward_var, width=50)
        self.port_forward_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        clear_pf = ttk.Label(input_frame, text="x", foreground="red", cursor="hand2")
        clear_pf.grid(row=0, column=2, sticky=tk.W, pady=2)
        clear_pf.bind("<Button-1>", lambda e: self.port_forward_var.set(""))

        # Authorization Cookie
        ttk.Label(input_frame, text="Authorization Cookie (value for s=):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cookie_entry = ttk.Entry(input_frame, textvariable=self.cookie_var, width=50)
        self.cookie_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        clear_cookie = ttk.Label(input_frame, text="x", foreground="red", cursor="hand2")
        clear_cookie.grid(row=1, column=2, sticky=tk.W, pady=2)
        clear_cookie.bind("<Button-1>", lambda e: self.cookie_var.set(""))

        # Bearer Token
        ttk.Label(input_frame, text="Bearer Token:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.token_entry = ttk.Entry(input_frame, textvariable=self.bearer_token_var, width=50)
        self.token_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        clear_token = ttk.Label(input_frame, text="x", foreground="red", cursor="hand2")
        clear_token.grid(row=2, column=2, sticky=tk.W, pady=2)
        clear_token.bind("<Button-1>", lambda e: self.bearer_token_var.set(""))

        # Protoset File Path
        ttk.Label(input_frame, text="Protoset File Path:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.protoset_entry = ttk.Entry(input_frame, textvariable=self.protoset_var, width=50)
        self.protoset_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        clear_protoset = ttk.Label(input_frame, text="x", foreground="red", cursor="hand2")
        clear_protoset.grid(row=3, column=2, sticky=tk.W, pady=2)
        clear_protoset.bind("<Button-1>", lambda e: self.protoset_var.set(""))

        # Server Address
        ttk.Label(input_frame, text="Server Address:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.server_entry = ttk.Entry(input_frame, textvariable=self.server_var, width=50)
        self.server_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        clear_server = ttk.Label(input_frame, text="x", foreground="red", cursor="hand2")
        clear_server.grid(row=4, column=2, sticky=tk.W, pady=2)
        clear_server.bind("<Button-1>", lambda e: self.server_var.set(""))

        # Method (Call Name)
        ttk.Label(input_frame, text="Method:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.call_dropdown = ttk.Combobox(input_frame, textvariable=self.call_var, width=48, state='readonly')
        self.call_dropdown.grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        # Bind event so that when a method is selected, body fields update dynamically.
        self.call_dropdown.bind("<<ComboboxSelected>>", self.on_method_select)

        # Use -plaintext checkbox
        plaintext_checkbox = ttk.Checkbutton(
            input_frame,
            text="Use -plaintext",
            variable=self.plaintext_var
        )
        plaintext_checkbox.grid(row=6, column=1, sticky=tk.W, pady=5)

        # Frame for dynamic Body input fields
        self.body_fields_frame = ttk.Frame(self.content_frame)
        self.body_fields_frame.pack(fill=tk.X, padx=10, pady=5)

        # (The previous Text widget for Body has been removed in favor of dynamic field entries.)

        # Frame for action buttons
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        make_call_button = ttk.Button(button_frame, text="Make gRPC Call", command=self.make_grpc_call)
        make_call_button.pack(side=tk.LEFT, padx=(0, 10))
        save_button = ttk.Button(button_frame, text="Save Call", command=self.save_current_call)
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        edit_button = ttk.Button(button_frame, text="Edit Call", command=self.edit_current_call)
        edit_button.pack(side=tk.LEFT)

        # Saved Calls Listbox
        saved_call_frame = ttk.Frame(self.content_frame)
        saved_call_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ttk.Label(saved_call_frame, text="Saved Calls:").pack(anchor=tk.W)
        self.saved_call_list_box = tk.Listbox(saved_call_frame, height=6)
        self.saved_call_list_box.pack(fill=tk.X, pady=5)
        self.saved_call_list_box.bind("<<ListboxSelect>>", self.on_saved_call_select)

        # Populate history listbox with saved calls
        for call_info in self.calls_history:
            display_text = self.saved_calls_manager.get_display_text(call_info)
            self.saved_call_list_box.insert(tk.END, display_text)

        # Output text area
        output_frame = ttk.Frame(self.content_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        ttk.Label(output_frame, text="Output:").pack(anchor=tk.W)
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def on_protoset_change(self, *args):
        """Called when the Protoset File Path changes; update the Call Name dropdown."""
        self.update_call_names()

    def update_call_names(self):
        """Update the Call Name dropdown based on the current protoset file."""
        protoset_path = self.protoset_var.get().strip()
        if not protoset_path or not os.path.exists(protoset_path):
            self.call_dropdown['values'] = []
            self.call_var.set('')
            return

        call_names = self.protoset_parser.get_call_names(protoset_path)
        self.call_dropdown['values'] = call_names
        if call_names:
            if self.call_var.get() not in call_names:
                self.call_var.set(call_names[0])
        else:
            self.call_var.set('')

    def on_method_select(self, event=None):
        """
        When a method is selected, dynamically create input fields for each
        field in the method's request message (based on the protoset) using grid.
        """
        # Clear any previous body field entries.
        for widget in self.body_fields_frame.winfo_children():
            widget.destroy()
        self.dynamic_body_fields = {}  # Dictionary to hold field name -> Entry widget mapping.

        call_name = self.call_var.get().strip()
        protoset_path = self.protoset_var.get().strip()
        if not call_name or not protoset_path or not os.path.exists(protoset_path):
            return

        fields = ProtosetParser.get_method_request_fields(protoset_path, call_name)
        if not fields:
            ttk.Label(self.body_fields_frame, text="(No body fields required for this method)").grid(row=0, column=0, sticky=tk.W)
        else:
            for row, field in enumerate(fields):
                field_name = field.name
                ttk.Label(self.body_fields_frame, text=f"{field_name}:").grid(row=row, column=0, sticky=tk.W, padx=(0, 5), pady=2)
                entry = ttk.Entry(self.body_fields_frame, width=50)
                entry.grid(row=row, column=1, sticky=tk.W, pady=2)
                self.dynamic_body_fields[field_name] = entry


    def make_grpc_call(self):
        """
        Gathers user input, constructs the JSON body from dynamic input fields,
        delegates execution of the grpcurl command to GrpcCaller,
        and then outputs the results.
        """
        port_forward = self.port_forward_var.get().strip()
        cookie = self.cookie_var.get().strip()
        bearer_token = self.bearer_token_var.get().strip()
        protoset = self.protoset_var.get().strip()
        server = self.server_var.get().strip()
        call_name = self.call_var.get().strip()

        # Build the body from dynamic fields.
        body_dict = {}
        if hasattr(self, 'dynamic_body_fields') and self.dynamic_body_fields:
            for field_name, entry in self.dynamic_body_fields.items():
                # For simplicity, treat all field values as strings.
                body_dict[field_name] = entry.get().strip()
            body = json.dumps(body_dict)
        else:
            body = ""

        self.output_text.delete("1.0", tk.END)

        if not protoset or not server or not call_name:
            error_msg = "Error: Missing required fields (Protoset, Server, or Call Name)."
            self.output_text.insert(tk.END, error_msg + "\n")
            return

        return_code, stdout, stderr, command = self.grpc_caller.execute_call(
            self.plaintext_var.get(), cookie, bearer_token, protoset, server, call_name, body
        )

        self.output_text.insert(tk.END, f"Executing command: {' '.join(command)}\n\n")

        if return_code is None or return_code != 0:
            self.output_text.insert(tk.END, f"Command failed with return code {return_code}.\n")
            if stderr.strip():
                self.output_text.insert(tk.END, f"stderr:\n{stderr}\n")
        else:
            self.output_text.insert(tk.END, f"stdout:\n{stdout}\n")
            if stderr.strip():
                self.output_text.insert(tk.END, f"stderr:\n{stderr}\n")

    def save_current_call(self):
        """
        Collects the current call information and delegates saving it to the SavedCallsManager.
        The UI history listbox is then updated.
        """
        # For now, we still store the body as a whole JSON string.
        current_call_info = {
            "port_forward": self.port_forward_var.get().strip(),
            "cookie": self.cookie_var.get().strip(),
            "bearer_token": self.bearer_token_var.get().strip(),
            "protoset": self.protoset_var.get().strip(),
            "server": self.server_var.get().strip(),
            "call": self.call_var.get().strip(),
            "body": ""  # Out of scope: saving the dynamic fields for now.
        }
        self.saved_calls_manager.append_call(current_call_info)
        self.saved_call_list_box.insert(tk.END, self.saved_calls_manager.get_display_text(current_call_info))

    def edit_current_call(self):
        """
        If a saved call is selected, update its information based on the current UI field values.
        The saved_calls.json file is updated and the history listbox reflects the new display text.
        """
        if self.saved_call_list_box.curselection():
            index = self.saved_call_list_box.curselection()[0]
        else:
            self.output_text.insert(tk.END, "No saved call selected to edit.\n")
            return

        current_call_info = {
            "port_forward": self.port_forward_var.get().strip(),
            "cookie": self.cookie_var.get().strip(),
            "bearer_token": self.bearer_token_var.get().strip(),
            "protoset": self.protoset_var.get().strip(),
            "server": self.server_var.get().strip(),
            "call": self.call_var.get().strip(),
            "body": ""  # Out of scope: saving the dynamic fields for now.
        }
        try:
            self.saved_calls_manager.update_call(index, current_call_info)
            # Update the listbox entry with the new display text.
            self.saved_call_list_box.delete(index)
            self.saved_call_list_box.insert(index, self.saved_calls_manager.get_display_text(current_call_info))
            self.output_text.insert(tk.END, f"Saved call at index {index} updated successfully.\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error updating call: {e}\n")

    def on_saved_call_select(self, event):
        """
        When a saved call item is selected, load its details into the input fields.
        """
        selection = self.saved_call_list_box.curselection()
        if not selection:
            self.is_history_selected = False
            self.selected_call_index = None
            return
        self.is_history_selected = True
        self.selected_call_index = selection[0]
        call_info = self.calls_history[self.selected_call_index]
        self.port_forward_var.set(call_info.get("port_forward", ""))
        self.cookie_var.set(call_info.get("cookie", ""))
        self.bearer_token_var.set(call_info.get("bearer_token", ""))
        self.protoset_var.set(call_info.get("protoset", ""))
        self.server_var.set(call_info.get("server", ""))
        self.call_var.set(call_info.get("call", ""))
        # Note: Dynamic body field values are not restored at this time.

def main():
    HISTORY_FILE = "/Users/joshansen/repo/vivint/grpcs/nest-grpcs/saved_calls.json"
    grpc_caller = GrpcCaller()
    protoset_parser = ProtosetParser()
    saved_calls_manager = SavedCallsManager(HISTORY_FILE)
    app = GrpcCallApp(grpc_caller, saved_calls_manager, protoset_parser)
    app.mainloop()


if __name__ == "__main__":
    main()
