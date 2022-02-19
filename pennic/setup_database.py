import os
import dotenv
from Blockchain import Blockchain
dotenv.load_dotenv()

chain = Blockchain(os.getenv("BLOCKCHAIN_DATABASE_PATH") or "blockchain.db")

chain.install_database()
print(f"""
=================================================
8888888b.                            d8b          
888   Y88b                           Y8P          
888    888                                        
888   d88P .d88b.  88888b.  88888b.  888  .d8888b 
8888888P" d8P  Y8b 888 "88b 888 "88b 888 d88P"    
888       88888888 888  888 888  888 888 888      
888       Y8b.     888  888 888  888 888 Y88b.    
888        "Y8888  888  888 888  888 888  "Y8888P 
=================================================

=> Database has been created at {chain.database.path} and it's ready to go
""")
