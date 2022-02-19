from __future__ import annotations


class Message():
    def __init__(self, data: bytes, header_length=10) -> None:
        self.data = data
        self.header_length = header_length

    def to_bytes(self):
        message_length = len(self.data)
        return f"{'0'*(self.header_length - len(str(abs(message_length))))}{message_length}".encode("utf-8") + self.data

    @property
    def data_string(self) -> str:
        return self.data.decode("utf-8")

    @staticmethod
    def from_string(data: str, header_length=10) -> Message:
        return Message(data.encode("utf-8"), header_length)

    @staticmethod
    def receive(request, header_length=10) -> Message:
        message_length = int(request.recv(header_length).decode('utf-8'))
        data = request.recv(message_length)
        return Message(data, header_length)
