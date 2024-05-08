import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# print(sys.path)

import os
from utils.create_db import create_db,load_knowledge_db
from utils.call_emb import get_embedding

def get_vectordb(file_path:str=None, persist_path:str=None, embedding="openai",embedding_key:str=None):
    
    embedding = get_embedding(embedding=embedding, embedding_key=embedding_key)
    if os.path.exists(persist_path): 
        print("use existing vectordb")
        contents = os.listdir(persist_path)
        if len(contents) == 0:
            vectordb = create_db(file_path, persist_path, embedding)
        else:
            vectordb = load_knowledge_db(persist_path, embedding)
    else:
        print("building new vectordb")
        vectordb = create_db(file_path, persist_path, embedding)

    return vectordb