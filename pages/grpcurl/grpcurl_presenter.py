from pages.grpcurl.grpcurl_view import GrpcUrlView
from pages.grpcurl.protoset_parser import ProtosetParser
from pages.grpcurl.grpc_caller import GrpcCaller
from data.saved_calls_manager import SavedCallsManager
import os
import json

class GrpcCallPresenter:
    """
    The Presenter in the MVP pattern. It responds to view events,
    calls the model/service classes as needed, and then instructs the view to update.
    """
    def __init__(self, view: GrpcUrlView, grpc_caller: GrpcCaller, saved_calls_manager: SavedCallsManager, protoset_parser: ProtosetParser):
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
