import dotenv
import os
from Blockchain import TcpServer, TcpHandler
dotenv.load_dotenv()

if __name__ == "__main__":
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    with TcpServer((HOST, int(PORT)), TcpHandler) as server:
        server.serve_forever()
