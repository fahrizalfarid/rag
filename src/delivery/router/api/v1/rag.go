package v1

import (
	"github.com/fahrizalfarid/rag/src/entity/request"
	"github.com/fahrizalfarid/rag/src/model"
	"github.com/fahrizalfarid/rag/src/util"
	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
)

type ragDelivery struct {
	RagUsecase model.RAGUsecase
	Validator  *validator.Validate
}

func NewRagDelivery(f *fiber.App, ragUsecase model.RAGUsecase) {
	handler := &ragDelivery{
		RagUsecase: ragUsecase,
		Validator:  validator.New(),
	}

	v1 := f.Group("/api/v1")

	f.Static("/", "/path/code/src/delivery/router/api/v1/public")
	v1.Post("/llm/completion", handler.TextGeneration)
	v1.Post("/llm/semantic-search", handler.SemanticSearch)
}

func (b *ragDelivery) Validate(v any) error {
	return b.Validator.Struct(v)
}

func (r *ragDelivery) TextGeneration(c *fiber.Ctx) error {
	var request *request.RagRequest

	if err := c.BodyParser(&request); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(util.BadRequest(err.Error()))
	}

	if err := r.Validate(request); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(util.BadRequest(err.Error()))
	}

	ctx := c.UserContext()
	data, err := r.RagUsecase.LLM(ctx, request)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(util.BadRequest(err.Error()))
	}

	return c.Status(fiber.StatusOK).JSON(util.SuccessResponse(data))
}

func (r *ragDelivery) SemanticSearch(c *fiber.Ctx) error {
	var request *request.SemanticSearch

	if err := c.BodyParser(&request); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(util.BadRequest(err.Error()))
	}

	if err := r.Validate(request); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(util.BadRequest(err.Error()))
	}

	if request.K == 0 || request.K < 0 {
		request.K = 3
	}

	ctx := c.UserContext()
	data, err := r.RagUsecase.SemanticSearch(ctx, request)
	if err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(util.BadRequest(err.Error()))
	}

	return c.Status(fiber.StatusOK).JSON(util.SuccessResponse(data))
}
