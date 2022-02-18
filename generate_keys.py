from Blockchain import Blockchain
chain = Blockchain()
chain.generateKeys()
print("""
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

=> Files private.pem and public.pem have been generated
=> Feel free to share your public.pem file with whoever wants to transfer some pennic to you
=> Don't share your private.pem file with others, that's basically your key to access pennics you have
""")
