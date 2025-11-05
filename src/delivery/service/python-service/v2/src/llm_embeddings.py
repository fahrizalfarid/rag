from sentence_transformers import SentenceTransformer

class LLMEmbeddings():
    def __init__(self, modelpath='intfloat/multilingual-e5-base'):
        self.modelpath = modelpath
        self._load_embedding_model()

    def _load_embedding_model(self):
        try:
            self.model = SentenceTransformer(self.modelpath)
            print("model loaded")
        except FileNotFoundError:
            self.model = None

    def get_embeddings(self, query):
        if self.model is not None:
            emb = self.model.encode(query).tolist()
            return emb
        return [0 for _ in range(768)]
