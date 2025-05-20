from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from ui.grpcurl_page import GrpcUrlView
from ui.curl_page import CurlView
from ui.environments_page import EnvironVarView, EnvironmentRepo, EnvironmentPresenter
from ui.automations_page import AutomationsView
import feature_flags as flag

class MainTabbedPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False

        # Initialize model (adjust path or flag as needed)
        self.model = EnvironmentRepo('data/environments.json')

        # gRPCurl tab
        grpc_tab = TabbedPanelItem(text='gRPCurl')
        self.grpcurl_page = GrpcUrlView()
        grpc_tab.add_widget(self.grpcurl_page)
        self.add_widget(grpc_tab)

        # curl tab
        # curl_tab = TabbedPanelItem(text='curl')
        # self.curl_page = CurlView()
        # curl_tab.add_widget(self.curl_page)
        # self.add_widget(curl_tab)

        # environments tab
        # env_tab = TabbedPanelItem(text='Environments')
        # self.environment_page = EnvironVarView()
        # env_tab.add_widget(self.environment_page)
        # self.add_widget(env_tab)

        # automations tab
        # auto_tab = TabbedPanelItem(text='Automations')
        # self.automations_page = AutomationsView()
        # auto_tab.add_widget(self.automations_page)
        # self.add_widget(auto_tab)

class MainApp(App):
    def build(self):
        self.title = 'API Caller with gRPCurl and curl'
        root = MainTabbedPanel()

        # Set up parser and presenter for gRPCurl view
        # protoset_parser = ProtosetParser()
        # grpc_presenter = GrpcCallPresenter(
        #     root.grpcurl_page,
        #     protoset_parser,
        #     root.model
        # )

        # Hook view events to presenter callbacks
        # root.grpcurl_page.set_on_protoset_change(grpc_presenter.on_protoset_change)
        # root.grpcurl_page.set_on_method_select(grpc_presenter.on_method_select)
        # root.grpcurl_page.set_on_make_call(grpc_presenter.on_make_call)
        # root.grpcurl_page.set_on_save_call(grpc_presenter.on_save_call)
        # root.grpcurl_page.set_on_edit_call(grpc_presenter.on_edit_call)
        # root.grpcurl_page.set_on_saved_call_select(grpc_presenter.on_saved_call_select)

        # Initialize environment options in gRPCurl view
        # grpc_presenter.refresh_environment_options()

        # Set up environment presenter
        # EnvironmentPresenter(
        #     root.environment_page,
        #     root.model,
        #     on_change_callback=grpc_presenter.refresh_environment_options
        # )

        return root

if __name__ == '__main__':
    MainApp().run()
