import subprocess

class GrpcCaller:
    """Handles construction and execution of the grpcurl command."""
    def build_command(self, plaintext, cookie, bearer_token, protoset, server, method, body):
        command = ["grpcurl"]
        if plaintext:
            command.append("-plaintext")
        if cookie:
            command.extend(["-H", f"Cookie:s={cookie}"])
        elif bearer_token:
            command.extend(["-H", f"authorization: Bearer {bearer_token}"])
        command.extend(["--protoset", protoset])
        if body:
            command.extend(["-d", body])
        command.append(server)
        command.append(method)
        return command

    def execute_call(self, plaintext, cookie, bearer_token, protoset, server, call_name, body):
        command = self.build_command(plaintext, cookie, bearer_token, protoset, server, call_name, body)
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr, command
        except Exception as e:
            return None, "", f"Error while running grpcurl: {e}", command
