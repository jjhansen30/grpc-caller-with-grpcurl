# API Caller with gRPCurl

A desktop GUI application built with Tkinter that lets you make gRPC calls using the [grpcurl](https://github.com/fullstorydev/grpcurl) tool. The application also provides functionality for managing environment variables and saving and editing call details.

## Overview

This project offers a simple user interface to:
- **Make gRPC calls:** Compose and execute gRPC calls by specifying details such as protoset files, server addresses, and methods.
- **Manage Environment Variables:** Save and substitute environment variables within call parameters using a dedicated page.
- **Save & Edit Calls:** Persist call configurations into JSON files so that you can reuse or modify them later.

The application uses the Model-View-Presenter (MVP) pattern to separate concerns between UI components and business logic.

## Project Structure

- **constants.py**  
  Defines key constants such as file paths, the application name, and window geometry.  

- **feature_flags.py**  
  Contains feature flags to toggle optional tabs (e.g., curl and automations pages). By default, these features are disabled.

- **main.py**  
  The entry point for the application. It initializes the main Tkinter window with a Notebook containing various pages (gRPC, environments, and optionally curl and automations). It also sets up the necessary presenters and models.  

- **saved_grpc_manager.py**  
  Manages the persistence of gRPC call details. It handles loading, appending, updating, and saving call information to a JSON file.  

- **grpc_caller.py**  
  Builds and executes the grpcurl command based on user inputs (such as whether to use plaintext, authorization details, and request body data).  

- **environments_page.py**  
  Contains the model, view, and presenter for managing environment variables. This page allows users to add, edit, delete, and substitute environment variable values (using the format `{{variable}}`) in API call details.  

- **grpcurl_page.py**  
  The primary interface for making gRPC calls. This page includes:
  - Input fields for environment selection, authentication details, protoset file path, server address, and call method.
  - A dynamic area for building request body fields (including support for enumerated values).
  - A saved calls list to quickly recall previous configurations.
  - Integration with the protoset parser to extract gRPC service methods and build corresponding input forms.
  - Handlers for executing, saving, and editing call details.  

## Installation

### Prerequisites
- **Python 3.x**  
- **Tkinter:** Usually included with Python distributions.
- **grpcurl:** Ensure the grpcurl tool is installed and available in your system’s PATH.
- **Python Packages:**  
  - `google-protobuf` (for parsing protoset files)  
  - Other standard libraries (e.g., `json`, `subprocess`, `os`, `tkinter`)

### Setup
1. Clone the repository.
   ```bash
   git clone git@github.com:jjhansen30/grpc-caller-with-grpcurl.git
3. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
4. Install required packages:
   ```bash
   pip3 install google-protobuf
5. Verify that grpcurl is installed:
   ```bash
   grpcurl -version

## Usage

1. Run the application  
   ```bash
   cd /path/of/main/file/ #This is to ensure the .json files are created in the right spot
   python3 main.py
2. Making a gRPC Call:
    - Switch to the grpcurl tab.
    - Select or enter the environment to substitute variables in the call parameters.
    - Provide necessary details such as the protoset file, server address, and method.
    - (Optional) Fill in request body fields if required.
    - Click Make gRPC Call to execute.
3. Managing Environments:
    - Go to the Environment variables tab.
    - Create or edit environment entries by adding variable-value pairs.
    - Save your changes; the environment names will update in the grpcurl page drop-down.
4. Using Environment Variables in Calls:
    - In the grpcurl tab, select the environment you created from the dropdown menu.
    - Reference your environment variables in any input field (such as server address or method) by using the syntax {{VARIABLE_NAME}}. For example, if you have an environment variable named HOST, you can enter {{HOST}} in the server address field.
    - When you execute the call, the application will automatically substitute these placeholders with the corresponding values from the selected environment.
5. Saved Calls:
    - Use the saved calls list to quickly load or edit previous call configurations.
    - Save and update call details as needed.
  
## Configuration

- **Data Files**  
  The paths for saving gRPC calls and environments are defined in constants.py:
    - `GRPC_CALLS_FILE` (e.g., `data/grpc_calls.json`)
    - `SAVED_ENVIRONMENTS_FILE` (e.g., `data/environments.json`)
 
## Future Work

- **Implement Curl and Automations Pages**  
  Eventually I'd like the ability to use Curl commands. Then I'd like to implement a way to automate a list of calls.
- **Enhanced Error Handling**  
  I'm thinking of a more robust error handling based on user feedback.
- **UI/UX Improvements**
  I'm considering refining the interface and adding more detailed documentation or tooltips.
