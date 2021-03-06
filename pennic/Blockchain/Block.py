from __future__ import annotations
from hashlib import sha256
import multiprocessing
from .Transaction import Transaction
import time
import json
import requests


class Block():
    def __init__(self, index: int, timestamp: float, hardness=2, prev_hash: str = None, nonse=0) -> None:
        self.index = index
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.hardness = hardness
        self.nonse = nonse
        self.trasactions = []
        self.__hash = None

    @property
    def hash(self) -> str:
        return self.__hash

    @hash.setter
    def hash(self, value: str) -> None:
        self.__hash = sha256(value.encode("utf-8")).hexdigest()

    def generate_hash(self) -> str:
        return self.generate_hash_with_nonse(self.nonse)

    def generate_hash_with_nonse(self, nonse: int):
        return f"{self.index}{self.timestamp}{self.hardness}{self.prev_hash}{json.dumps(self.trasactions)}{nonse}"

    def calculate_correct_hash(self) -> str:
        calculated = False
        while not calculated:
            self.hash = self.generate_hash()
            if self.hash.startswith('0'*self.hardness):
                calculated = True
                break
            self.nonse += 1
        return self.hash

    def pool_hashing(self, nonse: int) -> list:
        hash = sha256(self.generate_hash_with_nonse(
            nonse).encode("utf-8")).hexdigest()
        if hash.startswith('0' * self.hardness):
            return [hash, nonse]

    def is_valid(self) -> bool:
        if not self.hash.startswith('0'*self.hardness):
            return False
        for transaction in self.trasactions:
            if not Transaction(transaction["index"], transaction["sender"], transaction["receiver"], transaction["amount"], transaction["time"]).validate():
                return False
        return True

    def override_hash(self, value):
        self.__hash = value

    def check_updated(self, port):
        last_block = requests.get(
            f"http://localhost:{port}/blockchain/last").json()
        return last_block["index"] >= self.index

    def calculate_correct_hash_multiprocess(self, miner_private_key, hashes_per_cycle, port) -> Block:
        self.add_transaction(len(self.trasactions), "network".encode("utf-8"), miner_private_key.public_key(
        ).export_key(), 10, time.time(), miner_private_key)
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        is_done = False
        start = 0
        end = hashes_per_cycle

        while not is_done:
            results = pool.map(self.pool_hashing, range(start, end))
            if self.check_updated():
                return None

            for result in results:
                if result == None:
                    continue
                self.__hash = result[0]
                self.nonse = result[1]
                is_done = True
                break
            start = end
            end += hashes_per_cycle
        self.tmp = []
        return self

    def add_transaction(self, index, sender, receiver, amount, time, sender_private_key) -> Block:
        transaction = Transaction(index, sender, receiver, amount, time)
        transaction.sign(sender_private_key)
        self.trasactions.append(transaction.to_json())
        return self

    def add_existing_transaction(self, transaction: Transaction) -> Block:
        self.trasactions.append(transaction.to_json())
        return self

    @staticmethod
    def from_json(data: dict[str, any]) -> Block:
        block = Block(data["index"], data["timestamp"],
                      data["hardness"], data["prev_hash"], data["nonse"])
        block.trasactions = data["transactions"]
        block.hash = block.generate_hash()
        return block

    def to_json(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "hardness": self.hardness,
            "nonse": self.nonse,
            "transactions": self.trasactions,
            "hash": self.hash
        }
