import pandas as pd
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection




def setup_collection(collection_name,first=True):
    connections.connect("default",uri="./milvus_law_qa.db")

    # insert
    fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="source_id", dtype=DataType.INT64),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=embed_dim),
            ]
    schema = CollectionSchema(fields, "tanya_jawab_hukum")
    if first:
        collection = Collection(collection_name, schema)
        return collection
    
    collection = Collection(collection_name)
    return collection


def create_and_save_from_dataframe(df, model, collection, text_column="join_text", chunk_size=200):
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, # 200 - 20, 500-100
            chunk_overlap=0.2*chunk_size,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", " "],
        )
    
    all_chunks = []
    all_embs = []
    all_metadatas = []

    for index, row in tqdm(df.iterrows(), total=len(df), desc="iterating..."):
        text = row[text_column]
        if not isinstance(text, str) or not text.strip():
            continue

        chunks = text_splitter.split_text(text)
        for chunk in tqdm(chunks, desc="chunking..."):
            emb = model.encode(chunk).tolist()
            all_chunks.append(chunk)
            all_embs.append(emb)
            all_metadatas.append(index)
        
    data = [all_metadatas, all_chunks, all_embs]
    collection.insert(data)
    collection.create_index(
            field_name="vector",
            index_params={"metric_type": "COSINE", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
    )
    collection.load()

def search_and_retrieve(model,collection,query,k=3):
    collection.load()
    emb = model.encode(query).tolist()
    print(len(emb))
    results = collection.search(
        data=[emb],
        anns_field="vector",
        limit=k,
        param={"metric_type": "COSINE", "params": {}},
        output_fields=["text", "source_id"],
    )
    contexts = []
    for hit in results[0]:
        contexts.append(hit.entity.get("text"))
        print(hit)
    return contexts


collection_name = "law_docs"
model_name = 'intfloat/multilingual-e5-base'
embed_dim = 768

model = SentenceTransformer(model_name)
collection = setup_collection(collection_name=collection_name, first=True)


source_df = pd.read_csv("law_qa_1000_raw.csv")
create_and_save_from_dataframe(source_df, model=model, collection=collection, chunk_size=500)


collection = setup_collection(collection_name=collection_name, first=False)
query = "korupsi di indonesia"
contexts = search_and_retrieve(model=model, collection=collection,query=query)

