import json
import os

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
        return (
            f"{call_info.get('server', '')} - "
            f"{call_info.get('method', '')} - "
            f"Body: {'Yes' if call_info.get('body') else 'No'}"
        )
