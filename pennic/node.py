import dotenv
import os
from Blockchain import Blockchain
import uvicorn
from fastapi import FastAPI
dotenv.load_dotenv()
chain = Blockchain(os.getenv("BLOCKCHAIN_DATABASE_PATH"))
chain.load_database()
app = FastAPI()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


@app.get("/blockchain")
async def blockchain():
    return chain.to_json()


@app.get("/blockchain/{start_block}/{end_block}")
async def from_to_somewhere_blockchain(start_block, end_block):
    start_block = int(start_block)
    end_block = int(end_block)
    return chain.from_to_somwhere_to_json(start_block, end_block)


@app.get("/blockchain/{start_block}")
async def from_to_end_blockchain(start_block):
    start_block = int(start_block)
    return chain.from_to_somwhere_to_json(start_block, len(chain.blocks) - 1)

if __name__ == "__main__":
    uvicorn.run("node:app", port=int(
        os.getenv("PORT")), reload=True if int(os.getenv("DEVELOPMENT")) else False)
