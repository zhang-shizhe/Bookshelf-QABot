import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import IPython.display
import io
import gradio as gr
from dotenv import load_dotenv, find_dotenv
from llm.call_llm import get_completion
from database.create_db import create_db
from chains.conversation_qa_chain import Conversation_QA_Chain
from chains.qa_chain import QA_Chain
import re

load_dotenv(find_dotenv())
LLM_MODEL_DICT = {
    "openai": [
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k-0613",
        "gpt-3.5-turbo-0613",
        "gpt-4",
        "gpt-4-32k",
    ]
}


LLM_MODEL_LIST = sum(list(LLM_MODEL_DICT.values()), [])
INIT_LLM = "gpt-3.5-turbo"
EMBEDDING_MODEL_LIST = ["openai", "m3e"]
INIT_EMBEDDING_MODEL = "openai"
DEFAULT_DB_PATH = "./data"
DEFAULT_PERSIST_PATH = "../vector_db/chroma"


def get_model_by_platform(platform):
    return LLM_MODEL_DICT.get(platform, "")


class Model_center:
    """
    
    store QA-chain objects

    - chat_qa_chain_self: (model, embedding) as key, store qa chain with historical conversations.
    - qa_chain_self: (model, embedding) as key, store qa chain without historical conversations.
    """

    def __init__(self):
        self.chat_qa_chain_self = {}
        self.qa_chain_self = {}

    def qa_chain_self_answer(
        self,
        question: str,
        chat_history: list = [],
        model: str = "openai",
        embedding="openai",
        temperature: float = 0.0,
        top_k: int = 30,
        file_path: str = DEFAULT_DB_PATH,
        persist_path: str = DEFAULT_PERSIST_PATH,
    ):
        """
        Calls the QA Chain without history to answer.
        """
        if question == None or len(question) < 1:
            return "", chat_history
        try:
            if (model, embedding) not in self.qa_chain_self:
                # Here, ensure the template is correctly used when initializing the QA_Chain
                self.qa_chain_self[(model, embedding)] = QA_Chain(
                    model=model,
                    temperature=temperature,
                    top_k=top_k,
                    file_path=file_path,
                    persist_path=persist_path,
                    embedding=embedding,
                )
            chain = self.qa_chain_self[(model, embedding)]
            response = chain.answer(question, temperature, top_k)
            chat_history.append((question, response))
            print(chat_history)
            return "", chat_history
        except Exception as e:
            return str(e), chat_history

    def chat_qa_chain_self_answer(
        self,
        question: str,
        chat_history: list = [],
        model: str = "openai",
        embedding: str = "openai",
        temperature: float = 0.0,
        top_k: int = 30,
        file_path: str = DEFAULT_DB_PATH,
        persist_path: str = DEFAULT_PERSIST_PATH,
    ):
        """
        Calls the QA Chain with historical conversations to answer questions.
        """
        if question == None or len(question) < 1:
            return "", chat_history
        try:
            if (model, embedding) not in self.chat_qa_chain_self:
                self.chat_qa_chain_self[(model, embedding)] = Conversation_QA_Chain(
                    model=model,
                    temperature=temperature,
                    top_k=top_k,
                    chat_history=chat_history,
                    file_path=file_path,
                    persist_path=persist_path,
                    embedding=embedding,
                )
            chain = self.chat_qa_chain_self[(model, embedding)]
            return "", chain.answer(
                question=question, temperature=temperature, top_k=top_k
            )
        except Exception as e:
            return e, chat_history

    def clear_history(self):
        if len(self.chat_qa_chain_self) > 0:
            for chain in self.chat_qa_chain_self.values():
                chain.clear_history()


def format_chat_prompt(message, chat_history):
    prompt = ""
    # iterate over all history conversation messages
    for turn in chat_history:
        user_message, bot_message = turn
        prompt = f"{prompt}\nUser: {user_message}\nAssistant: {bot_message}"
    # add current user message to the prompt
    prompt = f"{prompt}\nUser: {message}\nAssistant:"
    return prompt


def respond(
    message, chat_history, llm, history_len=3, temperature=0.1, max_tokens=2048
):
    '''
    Only for "chat with general LLM"
    '''

    if message == None or len(message) < 1:
        return "", chat_history
    try:
        # constraints on maximum history records
        chat_history = chat_history[-history_len:] if history_len > 0 else []
        formatted_prompt = format_chat_prompt(message, chat_history)

        bot_message = get_completion(
            formatted_prompt, llm, temperature=temperature, max_tokens=max_tokens
        )

        bot_message = re.sub(r"\\n", "<br/>", bot_message)
        chat_history.append((message, bot_message))
        return "", chat_history
    except Exception as e:
        return e, chat_history


model_center = Model_center()

block = gr.Blocks()
with block as demo:
    with gr.Row(equal_height=True):

        with gr.Column(scale=2):
            gr.Markdown(
                """<h1><center>Book Shelf QA_Bot</center></h1>
                <h3><center>your personal QA_Bot</center></h3>
                """
            )

    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(
                height=400, show_copy_button=True, show_share_button=True
            )
            # create a textbox to input prompt/question
            msg = gr.Textbox(label="Prompt/Question")

            with gr.Row():
                # create submit button
                db_with_his_btn = gr.Button("Chat Bookshelf QA-Bot with history")
                db_wo_his_btn = gr.Button("Chat Bookshelf QA-Bot without history")
                llm_btn = gr.Button("Chat with General LLM")
            with gr.Row():
                # create a clear button to clear the chatbox
                clear = gr.ClearButton(components=[chatbot], value="Clear console")

        with gr.Column(scale=1):
            file = gr.File(
                label="Upload your file to BookShelf",
                file_count="directory",
                file_types=[".txt", ".md", ".docx", ".pdf"],
            )
            with gr.Row():
                init_db = gr.Button("Digest your files to Vector Database")
            model_argument = gr.Accordion("Parameter settings", open=False)
            with model_argument:
                temperature = gr.Slider(
                    0,
                    1,
                    value=0.01,
                    step=0.01,
                    label="llm temperature",
                    interactive=True,
                )

                top_k = gr.Slider(
                    1,
                    100,
                    value=30,
                    step=1,
                    label="vector db search top k",
                    interactive=True,
                )

                history_len = gr.Slider(
                    0, 5, value=3, step=1, label="history length", interactive=True
                )

            model_select = gr.Accordion("Select your model")
            with model_select:
                llm = gr.Dropdown(
                    LLM_MODEL_LIST,
                    label="large language model",
                    value=INIT_LLM,
                    interactive=True,
                )

                embeddings = gr.Dropdown(
                    EMBEDDING_MODEL_LIST,
                    label="Embedding model",
                    value=INIT_EMBEDDING_MODEL,
                )

        # ineraction logic for bottons.

        init_db.click(create_db, inputs=[file, embeddings], outputs=[msg])

        db_with_his_btn.click(
            model_center.chat_qa_chain_self_answer,
            inputs=[msg, chatbot, llm, embeddings, temperature, top_k, history_len],
            outputs=[msg, chatbot],
        )

        db_wo_his_btn.click(
            model_center.qa_chain_self_answer,
            inputs=[msg, chatbot, llm, embeddings, temperature, top_k],
            outputs=[msg, chatbot],
        )

        llm_btn.click(
            respond,
            inputs=[msg, chatbot, llm, history_len, temperature],
            outputs=[msg, chatbot],
            show_progress="minimal",
        )

        # set the logic for hit "enter" button, use qa chain without historical conversation. 
        msg.submit(
            model_center.qa_chain_self_answer,
            inputs=[msg, chatbot, llm, embeddings, temperature, top_k],
            outputs=[msg, chatbot],
            show_progress="hidden",
        )
        # logic for clear
        clear.click(model_center.clear_history)
    gr.Markdown(
    """Reminder:<br>
    1. Please upload your own knowledge files before use; otherwise, the project's default knowledge base will be used.
    2. Initializing the database might take some time, please be patient.
    3. If any errors occur during use, they will be displayed in the text input box, please do not panic.<br>
    """

    )
# threads to consume the request
gr.close_all()

demo.launch()
