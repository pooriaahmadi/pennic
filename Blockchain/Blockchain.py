from typing import List
from .Block import Block
import hashlib


class Blockchain():
    def __init__(self) -> None:
        self.__blocks = []

    @property
    def blocks(self) -> List[Block]:
        return self.__blocks

    def add_block(self, block: Block):
        if len(self.blocks) and not block.prev_hash:
            raise ValueError("requested block does not fit the blockchain")
        if len(self.blocks):
            previous_block: Block = self.blocks[-1]
            if previous_block.hash != block.prev_hash:
                raise ValueError("requested block does not fit the blockchain")
            hash = hashlib.sha256(
                block.generate_hash().encode('utf-8')).hexdigest()
            if not hash.startswith('0'*block.hardness) or not (previous_block.index + 1) == block.index:
                raise ValueError("requested block does not fit the blockchain")

        self.__blocks.append(block)

    def __str__(self) -> str:
        output = ""
        for block in self.blocks:
            output += f"#{block.index} with hash {block.hash} {f'with previous hash {block.prev_hash}' if block.prev_hash else ''}\n"
        return output
