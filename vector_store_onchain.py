from web3 import Web3
import json


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  

# 2. Контракт
with open("VectorStore_abi.json", "r") as f:  
    abi = json.load(f)

contract_address = "0x24Ee65469B8e79B47529a72d89DA9185247803F7"
contract = w3.eth.contract(address=contract_address, abi=abi)
sender_address = w3.eth.accounts[0]

# 3. Добавление вектора
def add_vector(id: str, content: str, embedding: list[float]):
    scaled = [int(x * 1e6) for x in embedding]  # масштабируем для int256
    tx_hash = contract.functions.addVector(id, content, scaled).transact({'from': sender_address})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✅ Vector {id} added to blockchain.")

# 4. Получение вектора
def get_vector(id: str):
    content, scaled = contract.functions.getVector(id).call()
    embedding = [x / 1e6 for x in scaled]
    return content, embedding

# 5. Получение только embedding
def get_embedding(id: str):
    scaled = contract.functions.getEmbedding(id).call()
    return [x / 1e6 for x in scaled]


    
add_vector("article1", "Every citizen has rights...", [0.123456, 0.654321])
print(get_vector("article1"))
