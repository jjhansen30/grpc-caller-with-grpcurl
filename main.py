from network.grpc_caller import GrpcCaller
from ui.grpcurl_page import GrpcUrlView, ProtosetParser, GrpcCallPresenter
from ui.curl_page import CurlView
from ui.environments_page import EnvironVarView, EnvironmentModel, EnvironmentPresenter
from ui.automations_page import AutomationsView
from data.saved_grpc_manager import SavedGrpcManager
from tkinter import ttk
import tkinter as tk
import constants as c

class MainView(tk.Tk):
    """
    Main application window that holds a Notebook with separate pages.
    """

    def __init__(self):
        super().__init__()
        self.title(c.APP_NAME)
        self.geometry(c.GEOMETRY)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook_padding = 8

        # Instantiate each page view
        self.grpcurl_page = GrpcUrlView(self.notebook)
        self.curl_page = CurlView(self.notebook)
        self.automations_page = AutomationsView(self.notebook)
        self.environment_page = EnvironVarView(self.notebook)

        # Add pages to the notebook with appropriate tab labels
        self.notebook.add(self.grpcurl_page, text="grpcurl", padding=self.notebook_padding)
        self.notebook.add(self.curl_page, text="curl", padding=self.notebook_padding)
        self.notebook.add(self.automations_page, text="Automations", padding=self.notebook_padding)
        self.notebook.add(self.environment_page, text="Environment variables", padding=self.notebook_padding)

        self.model = EnvironmentModel(c.SAVED_ENVIRONMENTS_FILE)
        self.presenter = EnvironmentPresenter(self.environment_page, self.model)

if __name__ == "__main__":

    grpc_caller = GrpcCaller()
    protoset_parser = ProtosetParser()
    saved_calls_manager = SavedGrpcManager(c.GRPC_CALLS_FILE)
    main_view = MainView()
    GrpcCallPresenter(main_view.grpcurl_page, grpc_caller, saved_calls_manager, protoset_parser)
    main_view.mainloop()
