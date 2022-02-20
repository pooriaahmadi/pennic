import socket
from Blockchain import Message
HOST, PORT = "localhost", 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    message = Message.from_string("", 0)
    sock.sendall(message.to_bytes())
    response = Message.receive(sock)
    if response.mode_int == 1:
        print("node has accepted us")
    sock.sendall(Message.from_string("", 3).to_bytes())
    chain = Message.receive(sock)
    print(chain.data_string)
