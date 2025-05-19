from ui.grpcurl_page import GrpcUrlView, ProtosetParser, GrpcCallPresenter
from ui.curl_page import CurlView
from ui.environments_page import EnvironVarView, EnvironmentRepo, EnvironmentPresenter
from ui.automations_page import AutomationsView
from tkinter import ttk
import tkinter as tk
import feature_flags as flag

class MainView(tk.Tk):
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
        self.curl_page = CurlView(self.notebook)
        self.automations_page = AutomationsView(self.notebook)
        self.environment_page = EnvironVarView(self.notebook)

        self.notebook.add(self.grpcurl_page, text="grpcurl", padding=self.notebook_padding)
        if flag.SHOW_CURL_PAGE:
            self.notebook.add(self.curl_page, text="curl", padding=self.notebook_padding)
        if flag.SHOW_AUTOMATIONS_PAGE:
            self.notebook.add(self.automations_page, text="Automations", padding=self.notebook_padding)
        self.notebook.add(self.environment_page, text="Environment variables", padding=self.notebook_padding)

        self.model = EnvironmentRepo("data/environments.json")
        self.grpcurl_page.set_environment_options(self.model.get_all_environment_names())

if __name__ == "__main__":
    protoset_parser = ProtosetParser()
    main_view = MainView()
    
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
