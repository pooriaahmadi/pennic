from hashlib import sha256


class Transaction():
    def __init__(self, sender, reciever, amount, time) -> None:
        self.sender = sender
        self.reciever = reciever
        self.amount
        self.time = time
        self.hash = self.generate_hash()

    @property
    def hash(self) -> str:
        return self.__hash

    @hash.setter
    def hash(self, value: str) -> None:
        self.__hash = sha256(value.encode("utf-8")).hexdigest()

    def generate_hash(self) -> str:
        return f"{self.sender}{self.reciever}{self.amount}{self.time}"
