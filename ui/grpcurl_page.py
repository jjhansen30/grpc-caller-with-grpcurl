from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.properties import ListProperty

class GrpcUrlView(BoxLayout):
    # properties for dropdown options
    environment_options = ListProperty([])
    method_options = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        # callback placeholders
        self._external_protoset_change = None
        self._external_method_select = None
        self._external_make_call = None
        self._external_save_call = None
        self._external_edit_call = None
        self._external_saved_call_select = None
        # build the UI
        self._build_ui()

    def _build_ui(self):
        # Input fields grid with fixed row height
        input_layout = GridLayout(
            cols=3,
            spacing=5,
            size_hint_y=None,
            row_default_height=40,
            row_force_default=True
        )
        input_layout.bind(minimum_height=input_layout.setter('height'))

        # Environment spinner
        input_layout.add_widget(Label(text='Environment:'))
        self.environment_spinner = Spinner(text='', values=self.environment_options)
        input_layout.add_widget(self.environment_spinner)
        input_layout.add_widget(Label())

        # Port Forward
        input_layout.add_widget(Label(text='Port Forward:'))
        self.port_forward_input = TextInput(multiline=False)
        input_layout.add_widget(self.port_forward_input)
        input_layout.add_widget(Label())

        # Cookie
        input_layout.add_widget(Label(text='Cookie:'))
        self.cookie_input = TextInput(multiline=False)
        input_layout.add_widget(self.cookie_input)
        input_layout.add_widget(Label())

        # Bearer Token
        input_layout.add_widget(Label(text='Bearer Token:'))
        self.bearer_input = TextInput(multiline=False)
        input_layout.add_widget(self.bearer_input)
        input_layout.add_widget(Label())

        # Protoset path with browse
        input_layout.add_widget(Label(text='Protoset File Path:'))
        protoset_box = BoxLayout(orientation='horizontal', spacing=5)
        self.protoset_input = TextInput(multiline=False)
        btn_browse = Button(text='Browse')
        btn_browse.bind(on_release=self._open_protoset_chooser)
        protoset_box.add_widget(self.protoset_input)
        protoset_box.add_widget(btn_browse)
        input_layout.add_widget(protoset_box)
        input_layout.add_widget(Label())

        # Server Address
        input_layout.add_widget(Label(text='Server Address:'))
        self.server_input = TextInput(multiline=False)
        input_layout.add_widget(self.server_input)
        input_layout.add_widget(Label())

        # Method spinner
        input_layout.add_widget(Label(text='Method:'))
        self.method_spinner = Spinner(text='', values=self.method_options)
        self.method_spinner.bind(text=self._on_method_select)
        input_layout.add_widget(self.method_spinner)
        input_layout.add_widget(Label())

        # Plaintext checkbox
        input_layout.add_widget(Label())
        plaintext_box = BoxLayout(orientation='horizontal', spacing=5)
        self.plaintext_checkbox = CheckBox()
        plaintext_box.add_widget(self.plaintext_checkbox)
        plaintext_box.add_widget(Label(text='Use -plaintext'))
        input_layout.add_widget(plaintext_box)
        input_layout.add_widget(Label())

        self.add_widget(input_layout)

        # Saved calls list section
        list_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=(0,5)
        )
        list_layout.add_widget(Label(text='Saved Calls:', size_hint_y=None, height=30))
        self.saved_calls_list = Spinner(text='', values=[], size_hint_y=None, height=30)
        self.saved_calls_list.bind(text=self._on_saved_call_select)
        list_layout.add_widget(self.saved_calls_list)
        self.add_widget(list_layout)

        # Dynamic body fields
        self.add_widget(Label(text='Body Fields:', size_hint_y=None, height=30))
        self.body_scroll = ScrollView(size_hint=(1, None), height=200)
        self.body_container = GridLayout(
            cols=2,
            spacing=5,
            size_hint_y=None,
            row_default_height=40,
            row_force_default=True
        )
        self.body_container.bind(minimum_height=self.body_container.setter('height'))
        self.body_scroll.add_widget(self.body_container)
        self.add_widget(self.body_scroll)

        # Output area
        self.add_widget(Label(text='Output:', size_hint_y=None, height=30))
        self.output = TextInput(readonly=True, size_hint_y=None, height=150)
        self.add_widget(self.output)

        # Action buttons
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10, padding=(0,5))
        self.make_call_button = Button(text='Make Call')
        self.make_call_button.bind(on_release=lambda inst: self._external_make_call())
        self.save_call_button = Button(text='Save Call')
        self.save_call_button.bind(on_release=lambda inst: self._external_save_call())
        self.edit_call_button = Button(text='Edit Call')
        self.edit_call_button.bind(on_release=lambda inst: self._external_edit_call())
        btn_layout.add_widget(self.make_call_button)
        btn_layout.add_widget(self.save_call_button)
        btn_layout.add_widget(self.edit_call_button)
        self.add_widget(btn_layout)

    def _open_protoset_chooser(self, instance):
        chooser = FileChooserListView(filters=['*.protoset'], path='.')
        popup = Popup(title='Select Protoset', content=chooser, size_hint=(0.9, 0.9))
        chooser.bind(on_submit=lambda chooser, selection, touch: self._on_protoset_selected(selection, popup))
        popup.open()

    def _on_protoset_selected(self, selection, popup):
        if selection:
            path = selection[0]
            self.protoset_input.text = path
            if self._external_protoset_change:
                self._external_protoset_change(path)
        popup.dismiss()

    def _on_method_select(self, spinner, text):
        if self._external_method_select:
            self._external_method_select(text, self.protoset_input.text.strip())

    def _on_saved_call_select(self, spinner, text):
        if self._external_saved_call_select:
            index = self.saved_calls_list.values.index(text)
            self._external_saved_call_select(index)

    # Presenter registrations
    def set_on_protoset_change(self, handler):
        self._external_protoset_change = handler

    def set_on_method_select(self, handler):
        self._external_method_select = handler

    def set_on_make_call(self, handler):
        self._external_make_call = handler

    def set_on_save_call(self, handler):
        self._external_save_call = handler

    def set_on_edit_call(self, handler):
        self._external_edit_call = handler

    def set_on_saved_call_select(self, handler):
        self._external_saved_call_select = handler

    # Presenter-facing getters/setters
    def set_environment_options(self, options):
        self.environment_spinner.values = options
        self.environment_spinner.text = options[0] if options else ''

    def get_selected_environment(self):
        return self.environment_spinner.text

    def get_port_forward(self):
        return self.port_forward_input.text.strip()

    def get_cookie(self):
        return self.cookie_input.text.strip()

    def get_bearer_token(self):
        return self.bearer_input.text.strip()

    def get_protoset_file_path(self):
        return self.protoset_input.text.strip()

    def get_server_address(self):
        return self.server_input.text.strip()

    def set_method_dropdown(self, methods):
        self.method_spinner.values = methods
        self.method_spinner.text = methods[0] if methods else ''

    def get_method(self):
        return self.method_spinner.text.strip()

    def is_plaintext(self):
        return self.plaintext_checkbox.active

    def set_saved_calls_list(self, calls):
        self.saved_calls_list.values = calls
        self.saved_calls_list.text = calls[0] if calls else ''

    def get_selected_saved_call_index(self):
        return self.saved_calls_list.values.index(self.saved_calls_list.text)

    def set_input_fields(self, call_info):
        self.port_forward_input.text = call_info.get('port_forward', '')
        self.cookie_input.text = call_info.get('cookie', '')
        self.bearer_input.text = call_info.get('bearer_token', '')
        self.protoset_input.text = call_info.get('protoset', '')
        self.server_input.text = call_info.get('server', '')
        self.method_spinner.text = call_info.get('method', '')

    def clear_body_fields(self):
        self.body_container.clear_widgets()

    def render_body_fields(self, fields):
        self.clear_body_fields()
        for field, options in fields:
            lbl = Label(text=field.name)
            self.body_container.add_widget(lbl)
            if options:
                spinner = Spinner(text=options[0], values=options)
                self.body_container.add_widget(spinner)
            else:
                ti = TextInput(multiline=False)
                self.body_container.add_widget(ti)

    def get_body_fields(self):
        data = {}
        # children are reversed; reverse them
        children = list(self.body_container.children)[::-1]
        for i in range(0, len(children), 2):
            lbl = children[i]
            widget = children[i+1]
            key = lbl.text
            if isinstance(widget, Spinner):
                data[key] = widget.text
            elif isinstance(widget, TextInput):
                data[key] = widget.text
        return data

    def render_output(self, text):
        self.output.text = text

    def disable_save(self):
        self.save_call_button.disabled = True

    def enable_save(self):
        self.save_call_button.disabled = False

    def disable_edit(self):
        self.edit_call_button.disabled = True

    def enable_edit(self):
        self.edit_call_button.disabled = False
