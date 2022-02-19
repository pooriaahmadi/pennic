from pickle import TRUE
from typing import List
from .Block import Block
import hashlib
from Crypto.PublicKey import RSA
from Database import Database
from pypika import Query, Column, enums, functions, queries
import os


class Blockchain():
    def __init__(self, database_path: str) -> None:
        self.__blocks = []
        self.database = Database(database_path)
        self.database.setup()

    def install_database(self):
        os.remove(self.database.path)
        open(self.database.path, "w").close()
        self.database.setup()

        blocks_query: queries.CreateQueryBuilder = Query.create_table("blocks").columns(
            Column("id", enums.SqlTypes.INTEGER, nullable=False),
            Column("timestamp", enums.SqlTypes.TIMESTAMP,
                   nullable=False, default=functions.CurTimestamp()),
            Column("previous_block", enums.SqlTypes.INTEGER, nullable=True),
            Column("hardness", enums.SqlTypes.INTEGER, nullable=False),
            Column("nonse", enums.SqlTypes.INTEGER, nullable=False),
        ).unique("previous_block").primary_key("id")
        transactions_query: queries.CreateQueryBuilder = Query.create_table("transactions").columns(
            Column("id", enums.SqlTypes.INTEGER, nullable=False),
            Column("sender", enums.SqlTypes.VARCHAR(
                2048).get_sql(), nullable=True),
            Column("receiver", enums.SqlTypes.VARCHAR(
                2048).get_sql(), nullable=False),
            Column("amount", enums.SqlTypes.INTEGER, nullable=False),
            Column("timestamp", enums.SqlTypes.TIMESTAMP,
                   default=functions.CurTimestamp(), nullable=False),
            Column("hash", enums.SqlTypes.VARCHAR(
                256).get_sql(), nullable=False),
            Column("signature", enums.SqlTypes.VARCHAR(
                2048).get_sql(), nullable=False)
        ).primary_key("id")
        self.database.execute(blocks_query.__str__())
        self.database.execute(transactions_query.__str__())
        self.database.commit()

    @property
    def blocks(self) -> List[Block]:
        return self.__blocks

    @staticmethod
    def generateKeys():
        key = RSA.generate(2048)
        private_key = key.exportKey(format="PEM")
        public_key = key.publickey().exportKey(format="PEM")

        public_key_file = open("public.pem", 'wb')
        public_key_file.write(public_key)
        public_key_file.close()

        private_key_file = open("private.pem", 'wb')
        private_key_file.write(private_key)
        private_key_file.close()

        return (public_key, private_key)

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
