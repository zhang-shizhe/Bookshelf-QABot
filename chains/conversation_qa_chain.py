from langchain.chains import ConversationalRetrievalChain
from chains.init_llm import init_llm
from chains.get_vectordb import get_vectordb
import re

class Conversation_QA_Chain:
    """"
    QA chain with the ability to memoize historical conversations.
    """
    def __init__(
            self,model:str, 
            temperature:float=0.0, 
            top_k:int=4, 
            chat_history:list=[], 
            file_path:str=None, 
            persist_path:str=None,
            api_key:str=None, 
            embedding="openai",
            embedding_key:str=None
            ):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.chat_history = chat_history
        #self.history_len = history_len
        self.file_path = file_path
        self.persist_path = persist_path
        self.api_key = api_key
        self.embedding = embedding
        self.embedding_key = embedding_key


        self.vectordb = get_vectordb(self.file_path, self.persist_path, self.embedding, self.embedding_key)
        
    
    def clear_chat_history(self):
        "clear history conversion recoreds"
        return self.chat_history.clear()

    
    def keep_recent_n_chat_histroy(self, history_len:int=1):

        n = len(self.chat_history)
        return self.chat_history[n-history_len:]

 
    def answer(self, question:str=None, temperature=None, top_k = 4):
        
        if len(question) == 0:
            return "", self.chat_history
        
        if len(question) == 0:
            return ""
        
        if temperature is None:
            temperature = self.temperature

        if top_k is None:
            top_k = self.top_k

        llm = init_llm(self.model, temperature, self.api_key)

        #self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        retriever = self.vectordb.as_retriever(search_type="similarity",   
                                        search_kwargs={'k': top_k})

        qa = ConversationalRetrievalChain.from_llm(
            llm = llm,
            retriever = retriever
        )
        
        result = qa.invoke({"question": question,"chat_history": self.chat_history})  
        answer =  result['answer']
        answer = re.sub(r"\\n", '<br/>', answer)
        self.chat_history.append((question,answer))

        return self.chat_history 
    
if __name__ == "__main__":
    qa_chain = Conversation_QA_Chain(model="gpt-3.5-turbo", persist_path='vector_db', file_path='data')
    print(qa_chain.answer('what is the height of the tallest man'))
    print(qa_chain.answer('how many planets are there in the universe'))
            















