from email import message
from socketserver import BaseRequestHandler
from .Message import Message


class TcpHandler(BaseRequestHandler):
    def handle(self) -> None:
        message = Message.receive(self.request)
