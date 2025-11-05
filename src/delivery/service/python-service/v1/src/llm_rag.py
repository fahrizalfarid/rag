import pandas as pd
import requests
import ast
from tqdm.auto import tqdm
from typing import List
import os

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings



class LlamaCppServerEmbeddings(Embeddings):
    def __init__(self, url: str, dim = 4096):
        self.url = url
        self.dim = dim

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]
    
    def _embed(self, text: str) -> List[float]:
        try:
            response = requests.post(self.url, json={"content": text},timeout=60*10)
            response.raise_for_status()
            data = response.json()
            # return response.json()[0]['embedding']
            if isinstance(data, list):
                return data[0]['embedding']
            elif isinstance(data, dict) and 'embedding' in data:
                return data['embedding']
        except requests.exceptions.RequestException as e:
            return [0.0] * self.dim

class LLM():
    def __init__(self, dbpath, dim=4096):
        self.embedding_server_url = "http://localhost:8080/embedding"
        self.db = dbpath
        self.embedding_dim = dim
        self.src_text = 'join_text'
        self.llm_server_url = 'http://localhost:8081/completion'
        self._load_from_db()

    def _load_from_db(self):
        try:
            df = pd.read_csv(self.db)
            df['embedding'] = df['embedding'].apply(ast.literal_eval)
            
            texts = df['chunk_text'].tolist()
            embeddings = df['embedding'].tolist()
            
            embeddings_model = LlamaCppServerEmbeddings(url=self.embedding_server_url)
            embeddings = [e if isinstance(e, list) else [0.0] * self.embedding_dim for e in embeddings]
            
            vectorstore = FAISS.from_embeddings(
                text_embeddings=list(zip(texts, embeddings)),
                embedding = embeddings_model,
            )
            self.vectorstore = vectorstore
            self.df = df
            print("database loaded.")
            
        except FileNotFoundError:
            self.vectorstore = None
            self.df = None
    
    def _generate_response(self, prompt):
        payload = {
            "prompt":prompt,
            "n_predict":256, # max token
            # "temperatur":0.7,
            "stop": ["\nUser:", "<|end_of_text|>", "User:", "###"],
        }
        try:
            res = requests.post(self.llm_server_url, json=payload, timeout=60*10)
            answer = res.json()['content']
            return answer.strip()
        except Exception as e:
            return "LLM was not respond."
    
    def Forward(self, query, return_candidate_only=False, k=3):
        if self.vectorstore is not None:
            contexts = []
            retriever = self.vectorstore.as_retriever(
                search_kwargs={'k': k}
            )

            get_relevant_docs = retriever.invoke(query)
            for doc in get_relevant_docs:
                contexts.append(doc.page_content)
                print(doc.page_content)
            
            context_text = "\n\n".join(contexts)
            prompt = f"""Berdasarkan konteks berikut, jawab pertanyaan di bawah ini dengan jelas dan ringkas.
            Jika jawaban tidak ada dalam konteks, katakan "Saya tidak menemukan informasi tersebut dalam konteks."

            Konteks:
            {context_text}

            Pertanyaan:
            {query}

            Jawaban:"""

            if return_candidate_only:
                return contexts

            response = self._generate_response(prompt=prompt)
            return response
        else:
            return "database was not respond."


