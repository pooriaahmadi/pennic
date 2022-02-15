import time
from Blockchain import Block
from Blockchain import Blockchain

chain = Blockchain()
chain.blocks.append(Block(
    index=0,
    timestamp=time.time(),
    hardness=2,
    nonse=0
))
chain.blocks.append(Block(
    index=1,
    timestamp=time.time(),
    hardness=2,
    nonse=0,
    prev_hash=chain.blocks[-1].hash
))
chain.blocks.append(Block(
    index=2,
    timestamp=time.time(),
    hardness=2,
    nonse=0,
    prev_hash=chain.blocks[-1].hash
))

print(chain)
