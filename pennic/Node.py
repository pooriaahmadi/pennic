from urllib import response
from Crypto.PublicKey.RSA import RsaKey
from typing import List
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from Networking.body_types import Block as BlockBody, Transaction as TransactionBody
from Blockchain import Blockchain, Block, Transaction, Address
import requests
import operator
import uvicorn
import sys


class Node():
    def __init__(self, hashes_rate: int, private_key: RsaKey, blockchain: Blockchain, nodes: List[Address], port: int) -> None:
        self.hashes_rate = hashes_rate
        self.private_key = private_key
        self.blockchain = blockchain
        self.nodes = nodes
        self.port = port
        self.app = FastAPI()

    def broadcast_mined_block(self, block: Block):
        for node in self.nodes:
            try:
                requests.post(
                    f"http://{node}/broadcast/block", json=block.to_json(), headers={"port": str(self.port)})
                print(
                    f"Block {block.index} has been broadcasted to {node}")
            except requests.ConnectionError:
                self.nodes.remove(node)

    def broadcast_transaction(self, transaction: Transaction):
        for node in self.nodes:
            try:
                requests.post(
                    f"http://{node}/broadcast/transaction", json=transaction.to_json(), headers={"port": str(self.port)})
                print(
                    f"Transaction {transaction.index} has been broadcasted to {node}")
            except requests.ConnectionError:
                self.nodes.remove(node)

    def receive_blockchain(self):
        blocks_length = len(self.blockchain.blocks)
        received_blocks = []
        for index, node in enumerate(self.nodes):
            if index == 10:
                break
            try:
                response: requests.Response = None
                if blocks_length >= 0:
                    response = requests.get(
                        f"http://{node}/blockchain/{blocks_length}", headers={"port": str(self.port)})
                else:
                    response = requests.get(
                        f"http://{node}/blockchain", headers={"port": str(self.port)})

                data = response.json()
                received_blocks.append(data)
            except requests.ConnectionError:
                print(
                    f"Node {node} is not active and has been deleted")
                self.nodes.remove(node)

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
            self.blockchain.add_block(block)

    def routes(self):
        @self.app.middleware("http")
        async def get_ip_address(request: Request, call_next):
            port = request.headers.get("port")
            if not Address(request.client.host, port) in self.nodes:
                if Address(request.client.host, port).__str__() != f"localhost:{self.port}":
                    self.nodes.append(
                        Address(request.client.host, int(port)))
            response = await call_next(request)
            return response

        self.app.add_middleware(
            CORSMiddleware,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/blockchain")
        async def blockchain():
            return self.blockchain.to_json()

        @self.app.get("/blockchain/{start_block}/{end_block}")
        async def from_to_somewhere_blockchain(start_block, end_block):
            start_block = int(start_block)
            end_block = int(end_block)
            return self.blockchain.from_to_somwhere_to_json(start_block, end_block)

        @self.app.get("/blockchain/{start_block}")
        async def from_to_end_blockchain(start_block):
            start_block = int(start_block)
            return self.blockchain.from_to_somwhere_to_json(start_block, len(self.blockchain.blocks) - 1)

        @self.app.get("/nodes/")
        async def nodes():
            return list(map(lambda x: x.to_json(), self.nodes))

        @self.app.post("/broadcast/block")
        async def broadcast_mined_block(block: BlockBody, response: Response):
            transaction = block.transactions
            block: Block = Block(block.index, block.timestamp,
                                 block.hardness, block.prev_hash, block.nonse)
            block.trasactions = transaction
            block.hash = block.generate_hash()
            self.broadcast_mined_block(block)
            if not block.is_valid():
                response.status_code = status.HTTP_406_NOT_ACCEPTABLE
                return {"message": "block was invalid"}
            self.blockchain.add_block(block)

        @self.app.post("/broadcast/transaction")
        async def broadcast_transaction(transaction: TransactionBody, response: Response):
            transaction: Transaction = Transaction(
                transaction.index, transaction.sender.encode("utf-8"), transaction.receiver.encode("utf-8"), transaction.amount, transaction.time, transaction.signature)
            transaction.hash = transaction.generate_hash()
            self.broadcast_transaction(transaction)

            if transaction.to_json() in self.blockchain.pending_transactions:
                response.status_code = status.HTTP_208_ALREADY_REPORTED
                return {"message": "transaction has been already reported to me"}
            if transaction.validate():
                response.status_code = status.HTTP_406_NOT_ACCEPTABLE
                return {"message": "transaction was invalid"}
            self.blockchain.add_pending_transaction(transaction)
            return {}

        @self.app.post("/self/block")
        async def self_block(mined_block: BlockBody, request: Request, response: Response):
            if request.client.host != "127.0.0.1":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "You are not me >;/"}

            block = Block(mined_block.index, mined_block.timestamp,
                          mined_block.hardness, mined_block.prev_hash, mined_block.nonse)

            block.trasactions = mined_block.transactions
            block.hash = block.generate_hash()
            self.broadcast_mined_block(block)
            return {"message": "broadcasted"}

        @self.app.post("/self/transaction")
        async def self_transaction(received_transaction: TransactionBody, request: Request, response: Response):
            if request.client.host != "127.0.0.1":
                response.status_code = status.HTTP_403_FORBIDDEN
                return {"message": "You are not me >;/"}

            transaction = Transaction(received_transaction.index, received_transaction.sender, received_transaction.receiver,
                                      received_transaction.amount, received_transaction.time, received_transaction.signature)
            self.broadcast_transaction(transaction)
            return {"message": "broadcasted"}

    def setup(self):
        self.receive_blockchain()
        if not self.blockchain.validate_chain():
            print("Chain is not valid")
            sys.exit(0)

    # def mine(self):
    #     while True:
    #         block = self.blockchain.new_block()
    #         block.calculate_correct_hash_multiprocess(
    #             self.private_key, self.hashes_rate)
    #         self.broadcast_mined_block(block)
    #         self.blockchain.add_block(block)

    def runapp(self):
        uvicorn.run(self.app, port=self.port, host='0.0.0.0')

    def run(self):
        # mining_process = multiprocessing.Process(target=self.mine)
        # mining_process.start()
        pass
