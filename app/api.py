from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys



project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from chains.qa_chain import QA_Chain

# from llm.call_llm import parse_llm_api_key
# API_KEY =  parse_llm_api_key('openai')

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
API_KEY = os.environ["OPENAI_API_KEY"]

app = FastAPI()

template = """Refer to the following context to answer the final question. 
    If you don't know the answer, just say you don't know and don't try to make up the answer. 
    If the questioin is not relevant to the context or no context is provided, just say it is not relevant.
    Use a maximum of five sentences. Try to keep your answers concise and to the point. 
    Always end your answer with "Hope my answer helps!"
    context: {context}
    question: {question}
    correct answer:"""


# define a class to receive the data from POST requests
class Item(BaseModel):
    prompt: str  # user prompt
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    include_history: bool = False
    # API_Key
    api_key: str = None
    # path to the vector database
    db_path: str = "../vector_db/chroma"
    # path to the source files
    file_path: str = "../data"
    # prompt template
    prompt_template: str = template
    input_variables: list = ["context", "question"]
    embedding: str = "openai"
    # topk for vector db retrieval
    top_k: int = 5
    # embedding_key
    embedding_key: str = None


@app.post("/")
async def get_response(item: Item):

    if not item.include_history:
        if item.embedding_key == None:
            item.embedding_key = item.api_key
        chain = QA_Chain(
            model=item.model,
            temperature=item.temperature,
            top_k=item.top_k,
            file_path=item.file_path,
            persist_path=item.db_path,
            api_key=item.api_key,
            embedding=item.embedding,
            template=template,
            embedding_key=item.embedding_key,
        )

        response = chain.answer(question=item.prompt)

        return response

    else:
        # historical conversion chain under development
        return "API does not support historical conversion for now."
