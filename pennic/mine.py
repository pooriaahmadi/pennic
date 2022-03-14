from dotenv import load_dotenv
from Crypto.PublicKey import RSA
from Blockchain import Blockchain
import os
import requests


load_dotenv()

hash_rate = int(os.getenv("HASH_RATE"))
port = int(os.getenv("PORT"))

private = None
with open("private.pem", "rb") as private_file:
    private = RSA.import_key(private_file.read())


chain = Blockchain()
chain.load_database()

while True:
    block = chain.calculate_correct_hash_multiprocess(
        chain.new_block(), private, hash_rate)
    requests.post(f"http://localhost:{port}/self/block", json={
        "index": block.index,
        "timestamp": block.timestamp,
        "hardness": block.hardness,
        "prev_hash": block.prev_hash,
        "transactions": block.trasactions,
        "nonse": block.nonse,
        "hash": block.hash
    })
