import openai
from dotenv import load_dotenv, find_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def get_completion(prompt :str, model :str, temperature=0.1,api_key=None, secret_key=None, access_token=None, appid=None, api_secret=None, max_tokens=2048):

    if model in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613", "gpt-4", "gpt-4-32k"]:
        return get_completion_gpt(prompt, model, temperature, api_key, max_tokens)
    else:
        return "unsupported model"
    
def get_completion_gpt(prompt : str, model : str, temperature : float, api_key:str, max_tokens:int):
    # OpenAI Native API
    if api_key == None:
        api_key = parse_llm_api_key("openai")
    openai.api_key = api_key
    # make a completion
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens = max_tokens,
    )
    # see notebook
    return response.choices[0].message["content"]


def parse_llm_api_key(model:str, env_file:dict=None):
 
    if env_file == None:
        _ = load_dotenv(find_dotenv())
        env_file = os.environ
    if model == "openai":
        return env_file["OPENAI_API_KEY"]
    else:
        raise ValueError(f"model {model} not support!!!")