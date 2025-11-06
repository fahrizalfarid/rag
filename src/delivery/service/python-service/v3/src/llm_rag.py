import pandas as pd
import requests
import ast
from tqdm.auto import tqdm
from typing import List
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
import os
from google import genai



class LLM():
    def __init__(self, dbpath, dfpath, collection_name="law_docs"):
        self.dbpath = dbpath
        self.dfpath = dfpath
        self.collection_name = collection_name
        self.client = genai.Client(api_key="your_key")

        self._load_from_db()

    def _load_from_db(self):
        try:
            connections.connect("default",uri=self.dbpath)
            self.collection = Collection(self.collection_name)
            self.collection.load()
            self.df = pd.read_csv(self.dfpath,sep=",")
            print("database loaded")
        except FileNotFoundError:
            self.collection = None
    

    def _get_context_from_df(self, query, contexts, source_ids):
        # get context from id
        print(source_ids)
        paragraph = self.df.loc[self.df['id'] == source_ids[0], 'context'].values[0].split(".")[:2]

        prompt = f"""Berdasarkan konteks berikut, jawab pertanyaan di bawah ini dengan jelas dan ringkas.
                Jika jawaban tidak ada dalam konteks, katakan "Saya tidak menemukan informasi tersebut dalam konteks."

                Konteks dari vektor database : {"\n".join(contexts)}

                Konteks dari database : {"\n".join(paragraph)}

                Pertanyaan: {query}

                Jawaban:"""
        return prompt
    
    def _retrieve_from_gemini(self, prompt):
        response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
        return response.text

    def Forward(self, query, emb, k=3):
        if self.collection is not None:
            
            contexts = []
            ids = []
            results = self.collection.search(
                data=[emb],
                anns_field="vector",
                limit=k,
                param={"metric_type": "COSINE", "params": {}},
                output_fields=["text", "source_id"],
            )

            for i, hit in enumerate(results[0]):
                context = hit.entity.get("text")
                id = hit.entity.get("source_id")
                contexts.append(context)
                ids.append(id)


            prompt = self._get_context_from_df(query=query, contexts=contexts, source_ids=ids)
            print(prompt)
            response = self._retrieve_from_gemini(prompt=prompt)
            print(response)
            return response
        else:
            return "database was not respond."

