import socket
from Socket import Message
HOST, PORT = "localhost", 9999

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    message = Message.from_string("Hi server!")
    sock.sendall(message.to_bytes())
    # sock.sendall(bytes(data + "\n", "utf-8"))
