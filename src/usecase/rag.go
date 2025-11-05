package usecase

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/fahrizalfarid/rag/src/entity/request"
	"github.com/fahrizalfarid/rag/src/entity/response"
	"github.com/fahrizalfarid/rag/src/infrastructure"
	"github.com/fahrizalfarid/rag/src/model"
)

type ragUsecase struct{}

func NewRAGUsecase() model.RAGUsecase {
	return &ragUsecase{}
}

func (r *ragUsecase) LLM(ctx context.Context, req *request.RagRequest) (*response.RAGResponse, error) {
	t := "llm/completion"
	e := "llm/embedding"

	ctx, cancel := context.WithTimeout(ctx, 2*60*time.Second)
	defer cancel()

	nc, err := infrastructure.NatsConn()
	if err != nil {
		return nil, err
	}
	defer nc.Close()

	// dev
	if strings.Contains(req.Content[0], "no_rag") {
		t = "llm/completion/no_rag"
		req.Content[0] = strings.ReplaceAll(req.Content[0], "no_rag", "")

		payload, err := json.Marshal(&request.RagRequestService{
			Content: req.Content,
			Vector:  nil,
		})
		if err != nil {
			return nil, err
		}

		reply, err := nc.RequestWithContext(ctx, t, payload)
		if err != nil {
			return nil, err
		}
		fmt.Println(reply)

		var res *response.RAGResponse
		_ = json.Unmarshal(reply.Data, &res)

		return res, nil
	}

	payload, err := json.Marshal(&request.EmbeddingRequestService{
		Content: req.Content[0],
	})
	if err != nil {
		return nil, err
	}

	// get embedding
	reply, err := nc.RequestWithContext(ctx, e, payload)
	if err != nil {
		return nil, err
	}

	var embRes *response.EmbeddingResponseService
	_ = json.Unmarshal(reply.Data, &embRes)

	payload, err = json.Marshal(&request.RagRequestService{
		Content: req.Content,
		Vector:  embRes.Vector,
	})
	if err != nil {
		return nil, err
	}

	// get result
	reply, err = nc.RequestWithContext(ctx, t, payload)
	if err != nil {
		return nil, err
	}

	var res *response.RAGResponse
	_ = json.Unmarshal(reply.Data, &res)

	return res, nil
}

func (r *ragUsecase) SemanticSearch(ctx context.Context, req *request.SemanticSearch) (*response.SemanticSearch, error) {
	t := "llm/semantic_search"
	e := "llm/embedding"

	ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
	defer cancel()

	nc, err := infrastructure.NatsConn()
	if err != nil {
		return nil, err
	}
	defer nc.Close()

	payload, err := json.Marshal(&request.EmbeddingRequestService{
		Content: req.Content,
	})
	if err != nil {
		return nil, err
	}

	// get embedding
	reply, err := nc.RequestWithContext(ctx, e, payload)
	if err != nil {
		return nil, err
	}

	var embRes *response.EmbeddingResponseService
	_ = json.Unmarshal(reply.Data, &embRes)

	// get contexts
	payload, err = json.Marshal(&request.SemanticSearchRequestService{
		Query:  req.Content,
		Vector: embRes.Vector,
		K:      req.K,
	})
	if err != nil {
		return nil, err
	}

	reply, err = nc.RequestWithContext(ctx, t, payload)
	if err != nil {
		return nil, err
	}

	var res *response.SemanticSearch
	_ = json.Unmarshal(reply.Data, &res)

	return res, nil
}
