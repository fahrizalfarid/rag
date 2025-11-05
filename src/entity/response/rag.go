package response

type RAGResponse struct {
	Content []string `json:"content"`
}

type SemanticSearch struct {
	Content []string `json:"content"`
}

type Embedding struct {
	Chunk     string    `json:"content"`
	Embedding []float32 `json:"embedding"`
}

type EmbeddingResponse struct {
	Chunks []*Embedding `json:"content"`
}

type EmbeddingResponseService struct {
	Query  string    `json:"query"`
	Vector []float32 `json:"vector"`
}
