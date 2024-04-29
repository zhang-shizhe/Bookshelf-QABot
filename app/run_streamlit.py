import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from llm.call_llm import get_completion
from database.create_db import create_db
from chains.conversation_qa_chain import Conversation_QA_Chain
from chains.qa_chain import QA_Chain

# Load environment variables
_ = load_dotenv(find_dotenv())

# Constants and model configurations
LLM_MODEL_DICT = {
    "openai": ["gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613", "gpt-4", "gpt-4-32k"]
}
LLM_MODEL_LIST = sum(list(LLM_MODEL_DICT.values()), [])
INIT_LLM = "gpt-3.5-turbo"
EMBEDDING_MODEL_LIST = ['openai', 'm3e']
INIT_EMBEDDING_MODEL = "openai"
DEFAULT_DB_PATH = "../data"
DEFAULT_PERSIST_PATH = "../vector_db/chroma"

class ModelCenter:
    def __init__(self):
        self.chat_qa_chain_self = {}
        self.qa_chain_self = {}

    def chat_qa_chain_self_answer(self, question, chat_history, model, embedding, temperature, top_k, history_len, file_path, persist_path):
        if not question:
            return "", chat_history
        try:
            if (model, embedding) not in self.chat_qa_chain_self:
                self.chat_qa_chain_self[(model, embedding)] = Conversation_QA_Chain(model=model, temperature=temperature,
                                                                                    top_k=top_k, chat_history=chat_history, file_path=file_path, persist_path=persist_path, embedding=embedding)
            chain = self.chat_qa_chain_self[(model, embedding)]
            return "", chain.answer(question=question, temperature=temperature, top_k=top_k)
        except Exception as e:
            return str(e), chat_history

    def qa_chain_self_answer(self, question, chat_history, model, embedding, temperature, top_k, file_path, persist_path):
        if not question:
            return "", chat_history
        try:
            if (model, embedding) not in self.qa_chain_self:
                self.qa_chain_self[(model, embedding)] = QA_Chain(model=model, temperature=temperature,
                                                                  top_k=top_k, file_path=file_path, persist_path=persist_path, embedding=embedding)
            chain = self.qa_chain_self[(model, embedding)]
            chat_history.append((question, chain.answer(question, temperature, top_k)))
            return "", chat_history
        except Exception as e:
            return str(e), chat_history

    def clear_history(self):
        for chain in self.chat_qa_chain_self.values():
            chain.clear_history()

# Initialize the model center
model_center = ModelCenter()

# Streamlit layout
st.title("Book Shelf QA Bot")
st.caption("Your personal QA Bot")

# Sidebar for model configurations
with st.sidebar:
    selected_llm = st.selectbox("Select Language Model", options=LLM_MODEL_LIST, index=LLM_MODEL_LIST.index(INIT_LLM))
    selected_embedding = st.selectbox("Select Embedding Model", options=EMBEDDING_MODEL_LIST, index=EMBEDDING_MODEL_LIST.index(INIT_EMBEDDING_MODEL))
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.1, step=0.01)
    top_k = st.slider("Top K for Vector DB Search", min_value=1, max_value=10, value=4)
    history_len = st.slider("History Length", min_value=0, max_value=5, value=3)
    file_path = st.text_input("Database Path", value=DEFAULT_DB_PATH)
    persist_path = st.text_input("Persistence Path", value=DEFAULT_PERSIST_PATH)
    if st.button("Clear History"):
        model_center.clear_history()
        st.experimental_rerun()

question = st.text_input("Enter your question")
if st.button("Get Answer with History"):
    response, history = model_center.chat_qa_chain_self_answer(question, [], selected_llm, selected_embedding, temperature, top_k, history_len, file_path, persist_path)
    st.text(response)
elif st.button("Get Answer without History"):
    response, history = model_center.qa_chain_self_answer(question, [], selected_llm, selected_embedding, temperature, top_k, file_path, persist_path)
    st.text(response)

# Show additional information
st.markdown("""
**Notes:**
- Please upload your knowledge files first; otherwise, the system will parse the default knowledge base.
- Database initialization might take some time. Please be patient.
- If any exceptions occur, they will be displayed in the input box.
""")

if __name__ == "__main__":
    st.run()

