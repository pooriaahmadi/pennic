from pydantic import BaseModel
from typing import Optional, List


class Transaction(BaseModel):
    index: int
    sender: str
    receiver: str
    amount: float
    time: float
    signature: str
    hash: str


class Block(BaseModel):
    index: int
    timestamp: float
    hardness: int
    prev_hash: Optional[str] = None
    transactions: List
    nonse: int
    hash: str
