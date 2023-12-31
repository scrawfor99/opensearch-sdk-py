# https://github.com/opensearch-project/OpenSearch/blob/main/server/src/main/java/org/opensearch/transport/TcpHeader.java

from opensearch_sdk_py.transport.stream_input import StreamInput
from opensearch_sdk_py.transport.stream_output import StreamOutput
from opensearch_sdk_py.transport.version import Version
from opensearch_sdk_py.transport.transport_status import TransportStatus

class TcpHeader:
    MARKER_BYTES_SIZE = 2
    MESSAGE_LENGTH_SIZE = 4
    REQUEST_ID_SIZE = 8
    STATUS_SIZE = 1
    VERSION_ID_SIZE = 4
    VARIABLE_HEADER_SIZE = 4
    BYTES_REQUIRED_FOR_MESSAGE_SIZE = MARKER_BYTES_SIZE + MESSAGE_LENGTH_SIZE
    VERSION_POSITION = MARKER_BYTES_SIZE + MESSAGE_LENGTH_SIZE + REQUEST_ID_SIZE + STATUS_SIZE
    VARIABLE_HEADER_SIZE_POSITION = VERSION_POSITION + VERSION_ID_SIZE
    PRE_76_HEADER_SIZE = VERSION_POSITION + VERSION_ID_SIZE
    BYTES_REQUIRED_FOR_VERSION = PRE_76_HEADER_SIZE
    HEADER_SIZE = PRE_76_HEADER_SIZE + VARIABLE_HEADER_SIZE

    def __init__(self, prefix='ES', request_id=1, status=0, version=None, size=-1, variable_header_size=0):
        self.prefix = prefix
        self.request_id = request_id
        self.status = TransportStatus.STATUS_HANDSHAKE
        self.version = version
        self.size = size
        self.variable_header_size = variable_header_size

    def read_from(self, input: StreamInput):
        self.raw = input.raw
        self.prefix = input.read_bytes(2)
        self.size = input.read_int()
        self.request_id = input.read_long()
        self.status = input.read_byte()
        self.version = Version(input.read_int())
        self.variable_header_size = input.read_int()
        # print(f"remaining: {input.read_bytes(self.variable_header_size)}")

    def write_to(self, output: StreamOutput):
        output.write(bytes(self.prefix, 'ascii'))
        output.write_int(self.size)
        output.write_long(self.request_id)
        output.write_byte(self.status)
        output.write_version(self.version)
        output.write_byte(self.variable_header_size)

    def __str__(self):
        return f"{self.statuses} {self.prefix}, message={self.size} byte(s), request_id={self.request_id}, status={self.status}, version={self.version}"

    def __bytes__(self):
        return self.raw

    def is_request(self) -> bool:
        return (self.status & TransportStatus.STATUS_REQRES) == 0

    def is_error(self) -> bool:
        return (self.status & TransportStatus.STATUS_ERROR) != 0

    def is_compress(self) -> bool:
        return (self.status & TransportStatus.STATUS_COMPRESS) != 0

    def is_handshake(self) -> bool:
        return (self.status & TransportStatus.STATUS_HANDSHAKE) != 0

    @property
    def statuses(self) -> str:
        result = []
        if self.is_request():
            result.append("request")
        if self.is_error():
            result.append("error")
        if self.is_compress():
            result.append("compressed")
        if self.is_handshake():
            result.append("handshake")
        return result