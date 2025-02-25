from network.grpc_caller import GrpcCaller
from ui.grpcurl.grpcurl_view import GrpcUrlView
from ui.grpcurl.grpcurl_presenter import GrpcCallPresenter
from ui.grpcurl.protoset_parser import ProtosetParser
from ui.curl.curl_view import CurlView
from ui.environment_variables.environ_var_view import EnvironVarView
from ui.automations.automations_view import AutomationsView
from data.saved_grpc_manager import SavedGrpcManager
from tkinter import ttk
import tkinter as tk

class MainView(tk.Tk):
    """
    Main application window that holds a Notebook with separate pages.
    """

    def __init__(self):
        super().__init__()
        self.title("gRPC Caller with grpcurl")
        self.geometry("900x900")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Instantiate each page view
        self.grpcurl_page = GrpcUrlView(self.notebook)
        self.curl_page = CurlView(self.notebook)
        self.automations_page = AutomationsView(self.notebook)
        self.env_vars_page = EnvironVarView(self.notebook)

        # Add pages to the notebook with appropriate tab labels
        self.notebook.add(self.grpcurl_page, text="grpcurl")
        self.notebook.add(self.curl_page, text="curl")
        self.notebook.add(self.automations_page, text="Automations")
        self.notebook.add(self.env_vars_page, text="Environment variables")

if __name__ == "__main__":

    SAVED_CALLS = "data/saved_calls.json"
    grpc_caller = GrpcCaller()
    protoset_parser = ProtosetParser()
    saved_calls_manager = SavedGrpcManager(SAVED_CALLS)
    main_view = MainView()
    # Only the grpcurl page is functional, so pass that to the presenter.
    GrpcCallPresenter(main_view.grpcurl_page, grpc_caller, saved_calls_manager, protoset_parser)
    main_view.mainloop()
