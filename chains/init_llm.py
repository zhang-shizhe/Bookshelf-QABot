import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOpenAI


def init_llm(model:str=None, temperature:float=0.0, api_key:str=None):
    '''
    call llm via langchain
    '''
    if model in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613", "gpt-4", "gpt-4-32k"]:
        if api_key == None:
            api_key = parse_llm_api_key("openai")
        llm = ChatOpenAI(model_name = model, temperature = temperature , openai_api_key = api_key)
    else:
        raise ValueError(f"model{model} not support!!!")
    return llm

def parse_llm_api_key(model:str, env_file:dict=None):
 
    if env_file == None:
        _ = load_dotenv(find_dotenv())
        env_file = os.environ
    if model == "openai":
        return env_file["OPENAI_API_KEY"]
    else:
        raise ValueError(f"model {model} not support!!!")