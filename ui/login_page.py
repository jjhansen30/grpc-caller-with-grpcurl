import tkinter as tk
from tkinter import ttk
import subprocess
import json

from environments_page import EnvironVarView, EnvironmentPresenter, EnvironmentRepo

class LoginView(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Row 0: Label for URL (above dropdown and URL entry)
        url_label = ttk.Label(self, text="URL")
        url_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 0))
        
        # Row 1, Column 0: HTTP Method dropdown with default GET
        self.method_var = tk.StringVar(value="GET")
        self.method_dropdown = ttk.Combobox(self, textvariable=self.method_var, state="readonly")
        self.method_dropdown['values'] = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
        self.method_dropdown.current(0)  # Default selection is GET
        self.method_dropdown.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Row 1, Column 1: URL text input
        self.url_entry = ttk.Entry(self)
        self.url_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Allow the URL entry column to expand
        self.columnconfigure(1, weight=1)
        
        # Row 2: User Name label and input
        username_label = ttk.Label(self, text="User Name")
        username_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Row 3: Password label and input
        password_label = ttk.Label(self, text="Password")
        password_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Row 4: Login button below the password input
        login_button = ttk.Button(self, text="Login", command=self.do_login)
        login_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Row 5: Output frame with a label and text widget, with extra spacing from above
        output_frame = ttk.Frame(self)
        output_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=(10,5))
        self.rowconfigure(5, weight=1)  # Allow the output frame to expand vertically
        
        # Output label inside the output frame
        output_label = ttk.Label(output_frame, text="Output")
        output_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5,0))
        
        # Output text widget inside the output frame
        self.output_text = tk.Text(output_frame, height=10)
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure the output frame to expand its text widget properly
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
    
    def do_login(self):
        # Retrieve the input values from the GUI
        method = self.method_var.get().upper()
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        # Build the JSON payload using username and password
        if username or password:
            payload = {"username": username, "password": password}
            data = json.dumps(payload)
            # Include the Content-Type header for JSON
            cmd = ["curl", "-X", method, url, "-H", "Content-Type: application/json", "-d", data]
        else:
            cmd = ["curl", "-X", method, url]
        
        # Convert the command list to a string for display purposes.
        cmd_str = " ".join(cmd)
        
        try:
            # Execute the curl command and capture its output.
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            response = result.stdout
        except subprocess.CalledProcessError as e:
            response = e.stderr if e.stderr else str(e)
        
        # Attempt to pretty print the response if it's valid JSON
        try:
            parsed = json.loads(response)
            pretty_response = json.dumps(parsed, indent=4)
        except Exception:
            pretty_response = response
        
        # Display the command and its (pretty printed) response in the output text widget.
        output = f"Command: {cmd_str}\n\nResponse:\n{pretty_response}"
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)

# Main application
class _MockParent(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("API Caller with gRPCurl and curl")
        self.geometry("900x900")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.environment_page = EnvironVarView(self.notebook)
        self.login_view = LoginView(self.notebook)
        self.notebook.add(self.login_view, text="Login")
        self.notebook.add(self.environment_page, text="Environment")
        
        self.model = EnvironmentRepo("data/environments.json")
        self.presenter = EnvironmentPresenter(self.environment_page, self.model)

if __name__ == "__main__":
    mock_parent = _MockParent()
    mock_parent.mainloop()
