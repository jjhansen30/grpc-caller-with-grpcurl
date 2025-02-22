from google.protobuf import descriptor_pb2

class ProtosetParser:
    """Handles reading a protoset file and extracting call names and request fields."""
    @staticmethod
    def get_call_names(protoset_path):
        call_names = []
        try:
            with open(protoset_path, "rb") as f:
                fds = descriptor_pb2.FileDescriptorSet()
                fds.ParseFromString(f.read())
            for file_desc in fds.file:
                package_prefix = file_desc.package.strip() if file_desc.package else ""
                for service in file_desc.service:
                    full_service_name = f"{package_prefix}.{service.name}" if package_prefix else service.name
                    for method in service.method:
                        call_names.append(f"{full_service_name}.{method.name}")
            return call_names
        except Exception:
            return []

    @staticmethod
    def get_method_request_fields(protoset_path, call_name):
        try:
            with open(protoset_path, "rb") as f:
                fds = descriptor_pb2.FileDescriptorSet()
                fds.ParseFromString(f.read())
        except Exception:
            return []

        messages = {}

        def add_messages(prefix, message_list):
            for msg in message_list:
                full_name = f"{prefix}.{msg.name}" if prefix else msg.name
                messages[full_name] = msg
                add_messages(full_name, msg.nested_type)

        for file_desc in fds.file:
            package = file_desc.package.strip() if file_desc.package else ""
            add_messages(package, file_desc.message_type)

        parts = call_name.split('.')
        if len(parts) < 2:
            return []
        method_name = parts[-1]
        service_name = parts[-2]
        package = ".".join(parts[:-2])

        for file_desc in fds.file:
            file_package = file_desc.package.strip() if file_desc.package else ""
            if package and file_package != package:
                continue
            for service in file_desc.service:
                if service.name == service_name:
                    for method in service.method:
                        if method.name == method_name:
                            input_type = method.input_type.lstrip('.')
                            msg_descriptor = messages.get(input_type)
                            if msg_descriptor:
                                return msg_descriptor.field
                            else:
                                return []
        return []
