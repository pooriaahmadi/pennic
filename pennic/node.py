from io import TextIOWrapper
import dotenv
import os
from Blockchain import Blockchain
import uvicorn
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv()
chain = Blockchain(os.getenv("BLOCKCHAIN_DATABASE_PATH"))
chain.load_database()
recent_nodes_file: TextIOWrapper = open(
    os.getenv("RECENT_NODES_FILE_PATH"), 'r')
recent_nodes = json.load(recent_nodes_file)
recent_nodes_file.close()


app = FastAPI()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


@app.middleware("http")
async def get_ip_address(request: Request, call_next):
    if not request.client.host in recent_nodes:
        recent_nodes.append(request.client.host)
        recent_nodes_file: TextIOWrapper = open(
            os.getenv("RECENT_NODES_FILE_PATH"), 'w')
        recent_nodes_file.write(json.dumps(recent_nodes))
        recent_nodes_file.close()

    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
