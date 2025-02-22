import tkinter as tk
from tkinter import ttk
import json
import os

# -------------------------
# Model / Service Classes
# -------------------------

class SavedCallsManager:
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
        return (
            f"{call_info.get('server', '')} - "
            f"{call_info.get('method', '')} - "
            f"Body: {'Yes' if call_info.get('body') else 'No'}"
        )

# -------------------------
# View (UI) Components
# -------------------------


class PlaceholderView(ttk.Frame):
    """
    A simple placeholder view that displays:
    "No functionality implemented yet."
    """
    def __init__(self, parent):
        super().__init__(parent)
        label = ttk.Label(self, text="No functionality implemented yet.", font=("Arial", 14))
        label.pack(expand=True)

class MainView(tk.Tk):
    """
    Main application window that holds a Notebook with separate pages.
    """

    def __init__(self):
        super().__init__()
        from pages.grpcurl.grpcurl_view import GrpcUrlView
        self.title("gRPC Caller with grpcurl")
        self.geometry("900x900")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Instantiate each page view
        self.grpcurl_page = GrpcUrlView(self.notebook)
        self.curl_page = PlaceholderView(self.notebook)
        self.automations_page = PlaceholderView(self.notebook)
        self.env_vars_page = PlaceholderView(self.notebook)

        # Add pages to the notebook with appropriate tab labels
        self.notebook.add(self.grpcurl_page, text="grpcurl")
        self.notebook.add(self.curl_page, text="curl")
        self.notebook.add(self.automations_page, text="Automations")
        self.notebook.add(self.env_vars_page, text="Environment variables")

# -------------------------
# Main Application Entry Point
# -------------------------

def main():
    from pages.grpcurl.grpcurl_presenter import GrpcCallPresenter
    from pages.grpcurl.protoset_parser import ProtosetParser
    from pages.grpcurl.grpc_caller import GrpcCaller

    HISTORY_FILE = "saved_calls.json"  # Adjust the history file path as needed
    grpc_caller = GrpcCaller()
    protoset_parser = ProtosetParser()
    saved_calls_manager = SavedCallsManager(HISTORY_FILE)
    main_view = MainView()
    # Only the grpcurl page is functional, so pass that to the presenter.
    GrpcCallPresenter(main_view.grpcurl_page, grpc_caller, saved_calls_manager, protoset_parser)
    main_view.mainloop()

if __name__ == "__main__":
    main()
