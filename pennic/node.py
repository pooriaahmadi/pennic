from urllib import response
from Crypto.PublicKey.RSA import RsaKey
from Crypto.PublicKey import RSA
from typing import List
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from Networking.body_types import Block as BlockBody, Transaction as TransactionBody
from Blockchain import Blockchain, Block, Transaction, Address
from dotenv import load_dotenv
import requests
import operator
import uvicorn
import sys
import os
import json


load_dotenv()
app = FastAPI()
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
            node = node.split(":")
            nodes.append(Address(node[0], node[1]))
        if not len(nodes):
            input_node = input("Please enter a node to start")
            if input_node:
                nodes.append(Address(input_node))
except:
    input_node = input("Please enter a node to start").split(":")
    if input_node:
        nodes.append(Address(input_node[0], input_node[1]))

chain = Blockchain()
chain.load_database()


def broadcast_mined_block(block: Block):
    for node in nodes:
        try:
            requests.post(
                f"http://{node}/broadcast/block", json=block.to_json(), headers={"port": str(port)})
            print(
                f"Block {block.index} has been broadcasted to {node}")
        except requests.ConnectionError:
            nodes.remove(node)


def broadcast_transaction(transaction: Transaction):
    for node in nodes:
        try:
            requests.post(
                f"http://{node}/broadcast/transaction", json=transaction.to_json(), headers={"port": str(port)})
            print(
                f"Transaction {transaction.index} has been broadcasted to {node}")
        except requests.ConnectionError:
            nodes.remove(node)


def receive_blockchain():
    blocks_length = len(chain.blocks)
    received_blocks = []
    for index, node in enumerate(nodes):
        if index == 10:
            break
        try:
            response: requests.Response = None
            if blocks_length >= 0:
                response = requests.get(
                    f"http://{node}/blockchain/{blocks_length}", headers={"port": str(port)})
            else:
                response = requests.get(
                    f"http://{node}/blockchain", headers={"port": str(port)})

            data = response.json()
            received_blocks.append(data)
        except requests.ConnectionError:
            print(
                f"Node {node} is not active and has been deleted")
            nodes.remove(node)

    accpeted_blocks = []
    same_blocks = 0
    for received_block in received_blocks:
        if received_blocks.count(received_block) >= same_blocks:
            accpeted_blocks = received_block
    for index, block in enumerate(accpeted_blocks):
        block_ = Block(block["index"], block["timestamp"],
                       block["hardness"], block["prev_hash"], block["nonse"])
        block_.trasactions = block["transactions"]
        block_.hash = block_.generate_hash()
        accpeted_blocks[index] = block_
    accpeted_blocks.sort(key=operator.attrgetter("index"))

    for block in accpeted_blocks:
        chain.add_block(block)
        print(f"Block #{block.index} added")


# @app.middleware("http")
# async def get_ip_address(request: Request, call_next):
#     port = request.headers.get("port")
#     if not Address(request.client.host, port) in nodes:
#         if Address(request.client.host, port).__str__() != f"localhost:{port}":
#             nodes.append(
#                 Address(request.client.host, int(port)))
#     response = await call_next(request)
#     return response

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/blockchain")
async def blockchain():
    return chain.to_json()


@app.get("/blockchain/last")
async def last_block():
    return chain.blocks[-1].to_json()


@app.get("/blockchain/{start_block}/{end_block}")
async def from_to_somewhere_blockchain(start_block, end_block):
    start_block = int(start_block)
    end_block = int(end_block)
    return chain.from_to_somwhere_to_json(start_block, end_block)


@app.get("/blockchain/{start_block}")
async def from_to_end_blockchain(start_block):
    start_block = int(start_block)
    return chain.from_to_somwhere_to_json(start_block, len(chain.blocks) - 1)


@app.get("/nodes/")
async def reveive_nodes():
    return list(map(lambda x: x.to_json(), nodes))


@app.post("/broadcast/block")
async def broadcast_mined_block(block: BlockBody, response: Response):
    transaction = block.transactions
    block: Block = Block(block.index, block.timestamp,
                         block.hardness, block.prev_hash, block.nonse)
    block.trasactions = transaction
    block.hash = block.generate_hash()
    if not block.is_valid():
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "block was invalid"}
    try:
        chain.add_block(block)
        broadcast_mined_block(block)
    except:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "requested block does not fit the blockchain"}


@app.post("/broadcast/transaction")
async def broadcast_transaction(transaction: TransactionBody, response: Response):
    transaction: Transaction = Transaction(
        transaction.index, transaction.sender.encode("utf-8"), transaction.receiver.encode("utf-8"), transaction.amount, transaction.time, transaction.signature)
    transaction.hash = transaction.generate_hash()
    broadcast_transaction(transaction)

    if transaction.to_json() in chain.pending_transactions:
        response.status_code = status.HTTP_208_ALREADY_REPORTED
        return {"message": "transaction has been already reported to me"}
    if transaction.validate():
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "transaction was invalid"}
    chain.add_pending_transaction(transaction)
    return {}


@app.post("/self/block")
async def self_block(mined_block: BlockBody, request: Request, response: Response):
    if request.client.host != "127.0.0.1":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "You are not me >;/"}
    block = Block(mined_block.index, mined_block.timestamp,
                  mined_block.hardness, mined_block.prev_hash, mined_block.nonse)
    block.trasactions = mined_block.transactions
    block.hash = block.generate_hash()
    if block.is_valid() or not chain.does_fit_in_chain(block):
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "block does not fit in chain"}
    broadcast_mined_block(block)
    return {"message": "broadcasted"}


@app.post("/self/transaction")
async def self_transaction(received_transaction: TransactionBody, request: Request, response: Response):
    if request.client.host != "127.0.0.1":
        response.status_code = status.HTTP_403_FORBIDDEN
        return {"message": "You are not me >;/"}
    transaction = Transaction(received_transaction.index, received_transaction.sender, received_transaction.receiver,
                              received_transaction.amount, received_transaction.time, received_transaction.signature)
    broadcast_transaction(transaction)
    return {"message": "broadcasted"}


@app.get("/trasactions")
async def receive_transactions():
    return chain.pending_transactions


receive_blockchain()
if not chain.validate_chain():
    print("Chain is not valid")
    sys.exit(0)

uvicorn.run(app, port=port, host='0.0.0.0')
