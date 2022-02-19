from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


class Transaction():
    def __init__(self, index, sender, receiver, amount, time) -> None:
        self.index = index
        self.sender = sender  # sender public key
        self.receiver = receiver  # receiver public key
        self.amount = amount
        self.time = time
        self.hash = self.generate_hash()
        self.signature = None

    @property
    def hash(self) -> str:
        return self.__hash.hexdigest()

    @hash.setter
    def hash(self, value: str) -> None:
        self.__hash = SHA256.new(value.encode("utf-8"))

    def generate_hash(self) -> str:
        return f"{self.sender}{self.receiver}{self.amount}{self.time}"

    def sign(self, private_key):
        self.signature = pkcs1_15.new(private_key).sign(self.__hash)

    def to_json(self):
        return {
            "index": self.index,
            "sender": self.sender.decode(),
            "receiver": self.receiver.decode(),
            "amount": self.amount,
            "time": self.time,
            "hash": self.hash,
            "signature": self.signature.hex()
        }
