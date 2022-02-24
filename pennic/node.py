from dotenv import load_dotenv
from Node import Node
from Crypto.PublicKey import RSA
from Blockchain import Blockchain
from typing import List
from Blockchain import Address
import os
import json


load_dotenv()

hash_rate = int(os.getenv("HASH_RATE"))
port = int(os.getenv("PORT"))

private = None
with open("private.pem", "rb") as private_file:
    private = RSA.import_key(private_file.read())
nodes: List[Address] = []
try:
    with open("recent_nodes.json", "r", encoding="utf-8") as nodes_file:
        raw_nodes = json.loads(nodes_file.read())
        for node in raw_nodes:
            nodes.append(Address(node["ip"], node["port"]))

        if not len(nodes):
            input_node = input("Please enter a node to start")
            if input_node:
                nodes.append(Address(input_node))
except:
    input_node = input("Please enter a node to start")
    if input_node:
        nodes.append(Address(input_node))

chain = Blockchain()
chain.load_database()

node = Node(hash_rate, private, chain, nodes, port)
node.routes()
node.setup()
node.runapp()


with open("recent_nodes.json", 'w') as nodes_file:
    nodes_file.write(json.dumps(node.nodes))
