package model

import (
	"context"

	"github.com/fahrizalfarid/rag/src/entity/request"
	"github.com/fahrizalfarid/rag/src/entity/response"
)

type RAGUsecase interface {
	LLM(ctx context.Context, data *request.RagRequest) (*response.RAGResponse, error)
	SemanticSearch(ctx context.Context, req *request.SemanticSearch) (*response.SemanticSearch, error)
}
