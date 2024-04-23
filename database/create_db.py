import os
import sys
import re
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import tempfile
from dotenv import load_dotenv, find_dotenv
from embedding.call_emb import get_embedding

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# path of database
DEFAULT_DB_PATH = "./knowledge_db"
DEFAULT_PERSIST_PATH = "./vector_db"


def get_files(dir_path):
    file_list = []
    for filepath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            file_list.append(os.path.join(filepath, filename))
    return file_list


def file_loader(file, loaders):
    if isinstance(file, tempfile._TemporaryFileWrapper):
        file = file.name
    if not os.path.isfile(file):
        [file_loader(os.path.join(file, f), loaders) for f in  os.listdir(file)]
        return
    file_type = file.split('.')[-1]
    if file_type == 'pdf':
        loaders.append(PyMuPDFLoader(file))
    elif file_type == 'md':
        loaders.append(UnstructuredMarkdownLoader(file))
    elif file_type == 'txt':
        loaders.append(UnstructuredFileLoader(file))
    return



def create_db(files=DEFAULT_DB_PATH, persist_directory=DEFAULT_PERSIST_PATH, embeddings="openai"):
    if files == None:
        return "can't load empty file"
    if type(files) != list:
        files = [files]
    loaders = []
    [file_loader(file, loaders) for file in files]
    docs = []
    for loader in loaders:
        if loader is not None:
            docs.extend(loader.load())
    # split the files
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=300)
    split_docs = text_splitter.split_documents(docs)
    if type(embeddings) == str:
        embeddings = get_embedding(embedding=embeddings)
    # define persistent path
    persist_directory = './vector_db/chroma'
    # load db
    vectordb = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,
    persist_directory=persist_directory  # save to disk
    ) 

    vectordb.persist()
    return vectordb

def load_knowledge_db(path, embeddings):
    
    vectordb = Chroma(
        persist_directory=path,
        embedding_function=embeddings
    )
    print(type(vectordb))
    return vectordb

if __name__ == "__main__":
    create_db()