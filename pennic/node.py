from concurrent.futures import process
from io import TextIOWrapper
import operator
import random
from typing import List
from urllib import request
import dotenv
import os
from Blockchain import Blockchain, Transaction, Block
import uvicorn
import requests
import json
from fastapi import FastAPI, Request, Response, status
import multiprocessing
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Crypto.PublicKey import RSA
dotenv.load_dotenv()


class TransactionBase(BaseModel):
    sender: str
    receiver: str
    amount: float
    time: float
    signature: str
    hash: str


class BlockMined(BaseModel):
    index: float
    timestamp: float
    hardness: int
    prev_hash: str | None = None
    transactions: list
    nonse: int
    hash: str


hashes_rate = int(os.getenv("HASH_RATE"))  # got from the benchmark.py
hardness = 5
private = None
with open("private.pem", "rb") as private_file:
    private = RSA.import_key(private_file.read())
nodes_ask_limit = int(os.getenv("NODES_ASK_LIMIT"))
chain = Blockchain(os.getenv("BLOCKCHAIN_DATABASE_PATH"))
chain.load_database()
recent_nodes_file: TextIOWrapper = open(
    os.getenv("RECENT_NODES_FILE_PATH"), 'r')
recent_nodes: list = json.load(recent_nodes_file)
random.shuffle(recent_nodes)
connected_nodes: List[str] = []
recent_nodes_file.close()


app = FastAPI()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


@app.middleware("http")
async def get_ip_address(request: Request, call_next):
    if not request.client.host in recent_nodes:
        recent_nodes.append(request.client.host)
        recent_nodes_file: TextIOWrapper = open(
            os.getenv("RECENT_NODES_FILE_PATH"), 'w')
        recent_nodes_file.write(json.dumps(recent_nodes))
        recent_nodes_file.close()

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def broadcast_transaction_to_nodes(transaction: TransactionBase):
    for node in connected_nodes:
        requests.post(
            f"{node}:{PORT}/broadcast/transaction", json=transaction.json())
    print(f"Broadcasted a transaction to {len(connected_nodes)}")


def broadcast_block_to_nodes(block: BlockMined):
    for node in connected_nodes:
        requests.post(
            f"{node}:{PORT}/broadcast/block", json=block.json())
    print(f"Broadcasted a block to {len(connected_nodes)}")


@app.get("/blockchain")
async def blockchain():
    return chain.to_json()


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
async def nodes():
    return recent_nodes


@app.post("/broadcast/block")
async def broadcast_mined_block(block: BlockMined, response: Response):
    broadcast_block_to_nodes(block)
    transaction = block.transactions
    block: Block = Block(block.index, block.timestamp,
                         block.hardness, block.prev_hash, block.nonse)
    block.trasactions = transaction
    block.hash = block.generate_hash()
    if not block.is_valid():
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "block was invalid"}
    chain.add_block(block)


@app.post("/broadcast/transaction")
async def broadcast_transaction(transaction: TransactionBase, response: Response):
    broadcast_transaction_to_nodes(transaction)
    transaction: Transaction = Transaction(
        0, transaction.sender.encode("utf-8"), transaction.receiver.encode("utf-8"), transaction.amount, transaction.time, transaction.signature)
    transaction.hash = transaction.generate_hash()

    if transaction.to_json() in chain.pending_transactions:
        response.status_code = status.HTTP_208_ALREADY_REPORTED
        return {"message": "transaction has been already reported to me"}
    if transaction.validate():
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return {"message": "transaction was invalid"}
    chain.add_pending_transaction(transaction)
    return {}


def mine():
    while True:
        block = chain.new_block()
        print(block.hardness)
        block.calculate_correct_hash_multiprocess(private, hashes_rate)
        broadcast_block_to_nodes(BlockMined(index=block.index, timestamp=block.timestamp, hardness=block.hardness,
                                 prev_hash=block.prev_hash, transactions=block.trasactions, nonse=block.nonse, hash=block.hash))
        chain.add_block(block)


if __name__ == "__main__":
    blocks_length = len(chain.blocks) - 1
    received_blocks = []
    recent_nodes_file: TextIOWrapper = open(
        os.getenv("RECENT_NODES_FILE_PATH"), 'w')
    for recent_node in recent_nodes:
        if nodes_ask_limit <= 0:
            break
        nodes_ask_limit -= 1
        try:
            resposne = None
            if blocks_length >= 0:
                response = requests.get(
                    f"http://{recent_node}:{PORT}/blockchain/{blocks_length}")
            else:
                response = requests.get(
                    f"http://{recent_node}:{PORT}/blockchain")

            data = response.json()
            received_blocks.append(data)
            connected_nodes.append(recent_node)
            break
        except:
            print(f"Node {recent_node} is not active")
            recent_nodes.remove(recent_node)

    if len(connected_nodes) <= nodes_ask_limit / 2:
        for node in connected_nodes:
            response = request.get(f"http://{node}:{PORT}/nodes/")
            data = response.json()
            for fetched_node in data:
                if not fetched_node in recent_nodes:
                    recent_nodes.append(fetched_node)
    recent_nodes_file.write(json.dumps(recent_nodes))
    recent_nodes_file.close()
    accpeted_blocks = [0, []]
    for received_block in received_blocks:
        if received_blocks.count(received_block) >= accpeted_blocks[0]:
            accpeted_blocks[1] = received_block
    accpeted_blocks[1].sort(key=operator.attrgetter("index"))

    for block in accpeted_blocks[1]:
        chain.add_block(block)
    del accpeted_blocks
    del received_blocks
    del blocks_length
    if not chain.validate_chain():
        print("Chain is not valid")

    mining_process = multiprocessing.Process(target=mine)
    mining_process.daemon = True
    mining_process.run()

    uvicorn.run("node:app", port=PORT, reload=True if int(
        os.getenv("DEVELOPMENT")) else False)
