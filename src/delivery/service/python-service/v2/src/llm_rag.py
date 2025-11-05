import pandas as pd
import requests
import ast
from tqdm.auto import tqdm
from typing import List
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
import os



class LLM():
    def __init__(self, dbpath, dim=768, collection_name="law_docs"):
        self.db = dbpath
        self.embedding_dim = dim
        self.llm_server_url = 'http://localhost:8081/completion'
        self.collection_name = collection_name

        self._load_from_db()

    def _load_from_db(self):
        try:
            connections.connect("default",uri=self.db)
            self.collection = Collection(self.collection_name)
            self.collection.load()
            print("database loaded")
        except FileNotFoundError:
            self.collection = None
    
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

    
    def Forward(self, query, emb, return_candidate_only=False, k=3):
        if self.collection is not None:
            
            contexts = []
            results = self.collection.search(
                data=[emb],
                anns_field="vector",
                limit=k,
                param={"metric_type": "COSINE", "params": {}},
                output_fields=["text", "source_id"],
            )

            for i, hit in enumerate(results[0]):
                context = hit.entity.get("text") # cut to get 100 char
                contexts.append(context)

            context_text = "\n\n".join(contexts)
            prompt = f"""Berdasarkan konteks berikut, jawab pertanyaan di bawah ini dengan jelas dan ringkas.
            Jika jawaban tidak ada dalam konteks, katakan "Saya tidak menemukan informasi tersebut dalam konteks."

            Konteks:
            {context_text}

            Pertanyaan:
            {query}

            Jawaban:"""
            print(prompt)

            if return_candidate_only:
                return contexts

            response = self._generate_response(prompt=prompt)
            return response
        else:
            return "database was not respond."