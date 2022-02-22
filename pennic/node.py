from dotenv import load_dotenv
from Networking import Node
from Crypto.PublicKey import RSA
from Blockchain import Blockchain
import os
import json

load_dotenv()

if __name__ == "__main__":
    hash_rate = os.getenv("HASH_RATE")
    private = None
    with open("private.pem", "rb") as private_file:
        private = RSA.import_key(private_file.read())
    port = os.getenv("PORT")
    nodes = []
    try:
        with open("recent_nodes.json", "r", encoding="utf-8") as nodes_file:
            nodes = json.loads(nodes_file.read())
    except:
        nodes.append(input("Please enter a node to start"))
    chain = Blockchain()
    chain.load_database()

    node = Node(hash_rate, private, chain, nodes, port)
    node.routes()
    node.setup()
    node.run()

    with open("recent_nodes.json", 'w') as nodes_file:
        nodes_file.write(json.dumps(node.nodes))
