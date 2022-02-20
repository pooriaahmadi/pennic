from typing import List
from .Block import Block
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Database import Database
from pypika import Query, Column, enums, functions, queries
from .Transaction import Transaction
import os
import json


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
            Column("hardness", enums.SqlTypes.INTEGER, nullable=False),
            Column("nonse", enums.SqlTypes.INTEGER, nullable=False),
            Column("hash", enums.SqlTypes.VARCHAR(
                256).get_sql(), nullable=False)
        ).primary_key("id")
        transactions_query: queries.CreateQueryBuilder = Query.create_table("transactions").columns(
            Column("id", enums.SqlTypes.INTEGER, nullable=False),
            Column("block_index", enums.SqlTypes.INTEGER, nullable=False),
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
                2048).get_sql(), nullable=False),
            Column("block", enums.SqlTypes.INTEGER, nullable=False)
        ).primary_key("id")
        self.database.execute(blocks_query.get_sql())
        self.database.execute(transactions_query.get_sql())
        self.database.commit()

    def load_database(self):
        self.database.execute(Query.from_("blocks").select("*").get_sql())
        fetched_blocks = self.database.fetchall()
        self.database.execute(Query.from_(
            "transactions").select("*").get_sql())
        fetched_transactions = self.database.fetchall()

        for index, fetched_block in enumerate(fetched_blocks):
            prev_hash = None
            if index != 0:
                prev_hash = self.blocks[-1].hash
            block = Block(fetched_block[0], fetched_block[1],
                          fetched_block[2], prev_hash, fetched_block[3])
            for index, fetched_transaction in enumerate(fetched_transactions):
                if fetched_transaction[8] == block.index:
                    transaction = Transaction(
                        fetched_transaction[1], fetched_transaction[2].encode("utf-8"), fetched_transaction[3].encode("utf-8"), fetched_transaction[4], fetched_transaction[5])
                    transaction.signature = fetched_transaction[7].encode(
                        "utf-8")
                    block.trasactions.append(transaction.to_json())
                    del fetched_transactions[index]
            self.__blocks.append(block)

    def from_to_somewhere(self, start_block: int, end_block: int) -> List[Block]:
        return list(filter(lambda x: x.index >= start_block and x.index <= end_block, self.blocks))

    def from_to_somwhere_to_json(self, start_block: int, end_block: int):
        return list(map(lambda x: x.to_json(), self.from_to_somewhere(start_block, end_block)))

    def to_json(self):
        return list(map(lambda x: x.to_json(), self.blocks))

    def to_string(self):
        return json.dumps(list(map(lambda x: x.to_json(), self.blocks))).encode("utf-8")

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

        # Inserting block into database
        query = Query.into("blocks").insert(
            block.index, block.timestamp, block.hardness, block.nonse, block.hash)
        self.database.execute(query.get_sql())

        # Inserting transactions into database
        for transaction in block.trasactions:
            query = Query.into("transactions").insert(None, transaction["index"], transaction["sender"], transaction["receiver"],
                                                      transaction["amount"], transaction["time"], transaction["hash"], transaction["signature"], block.index)
            self.database.execute(query.get_sql())

        self.database.commit()
        self.__blocks.append(block)

    def __str__(self) -> str:
        output = ""
        for block in self.blocks:
            output += f"#{block.index} with hash {block.hash} {f'with previous hash {block.prev_hash}' if block.prev_hash else ''}\n"
        return output
