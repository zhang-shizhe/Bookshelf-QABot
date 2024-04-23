from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from init_llm import init_llm
from get_vectordb import get_vectordb
import sys
import re

class QA_chain():
    '''
    QA chain with out historical conversion
    '''

    # default_template_based on the retrieved results and user query
    default_template_rq = """Use the following context to answer the final question. 
    If you don't know the answer, just say you don't know and don't try to make up the answer. 
    Use a maximum of five sentences. Try to keep your answers concise and to the point. 
    Always end your answer with "Hope my answer helps!"
    {context}
    question: {question}
    correct answer:"""

    def __init__(
            self, model:str, 
            temperature:float=0.0, 
            top_k:int=4,  
            file_path:str=None, 
            persist_path:str=None, 
            api_key:str=None, 
            embedding = "openai",  
            embedding_key = None, 
            template=default_template_rq
            ):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.file_path = file_path
        self.persist_path = persist_path
        self.api_key = api_key
        self.embedding = embedding
        self.embedding_key = embedding_key
        self.template = template

        self.vectordb = get_vectordb(self.file_path, self.persist_path, self.embedding, self.embedding_key)

        self.llm = init_llm(self.model, self.temperature, self.api_key)

        self.qa_chain_prompt = PromptTemplate(input_variables=["context","question"],
                                    template=self.template)
        
        self.retriever = self.vectordb.as_retriever(search_type="similarity",   
                                        search_kwargs={'k': self.top_k}) 
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm,
                                        retriever=self.retriever,
                                        return_source_documents=True,
                                        chain_type_kwargs={"prompt":self.qa_chain_prompt})

    #基于大模型的问答 prompt 使用的默认提示模版
    #default_template_llm = """请回答下列问题:{question}"""
           
    def answer(self, question:str=None, temperature=None, top_k=None):
        """"
        核心方法，调用问答链
        arguments: 
        - question：用户提问
        """

        if len(question) == 0:
            return ""
        
        if temperature == None:
            temperature = self.temperature
            
        if top_k == None:
            top_k = self.top_k

        result = self.qa_chain({"query": question, "temperature": temperature, "top_k": top_k})
        answer = result["result"]
        answer = re.sub(r"\\n", '<br/>', answer)
        return answer   