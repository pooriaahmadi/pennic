import time
from Blockchain import Block
from Blockchain import Blockchain
from Crypto.PublicKey import RSA
hashes_rate = 5500  # got from the benchmark.py
hardness = 5
private = None
with open("private.pem", "rb") as private_file:
    private = RSA.import_key(private_file.read())

chain = Blockchain()
chain.add_block(Block(
    index=0,
    timestamp=time.time(),
    hardness=hardness,
    nonse=0
).calculate_correct_hash_multiprocess(hashes_rate))
chain.add_block(Block(
    index=1,
    timestamp=time.time(),
    hardness=hardness,
    nonse=0,
    prev_hash=chain.blocks[-1].hash
).calculate_correct_hash_multiprocess(hashes_rate))
chain.add_block(Block(
    index=2,
    timestamp=time.time(),
    hardness=hardness,
    nonse=0,
    prev_hash=chain.blocks[-1].hash
).add_transaction(private.public_key().export_key(), b"Asd", 50, time.time(), private).calculate_correct_hash_multiprocess(hashes_rate))
print(chain)
