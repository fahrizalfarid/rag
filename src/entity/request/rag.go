package request

type RagRequest struct {
	Content []string `json:"content" validate:"required"`
}

type RagRequestService struct {
	Content []string  `json:"content" validate:"required"`
	Vector  []float32 `json:"vector"`
}

type SemanticSearch struct {
	Content string `json:"content" validate:"required"`
	K       int    `json:"k" validate:"-"`
}

type EmbeddingRequestService struct {
	Content string `json:"content" validate:"required"`
}

type SemanticSearchRequestService struct {
	Query  string    `json:"query" validate:"required"`
	Vector []float32 `json:"vector"`
	K      int       `json:"k" validate:"-"`
}
