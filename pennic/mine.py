from dotenv import load_dotenv
from Crypto.PublicKey import RSA
from Blockchain import Blockchain, Block
import os
import requests


load_dotenv()

hash_rate = int(os.getenv("HASH_RATE"))
port = int(os.getenv("PORT"))

private = None
with open("private.pem", "rb") as private_file:
    private = RSA.import_key(private_file.read())


def new_block():
    block = requests.get(f"http://localhost:{port}/blockchain/new").json()
    transactions = block["transactions"]
    block = Block(block["index"], block["timestamp"],
                  block["hardness"], block["prev_hash"], block["nonse"])
    block.trasactions = transactions
    block.hash = block.generate_hash()
    return block


while True:
    block = new_block()
    block = block.calculate_correct_hash_multiprocess(private, hash_rate, port)
    if not block:
        continue
    response = requests.post(f"http://localhost:{port}/self/block", json={
        "index": block.index,
        "timestamp": block.timestamp,
        "hardness": block.hardness,
        "prev_hash": block.prev_hash,
        "transactions": block.trasactions,
        "nonse": block.nonse,
        "hash": block.hash
    }, headers={"port": str(port)})
    if response.status_code == 406:
        continue
    print(f"MINED: {block}")
