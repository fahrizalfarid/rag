package util

import "fmt"

type successRes struct {
	Status  string `json:"status"`
	Message string `json:"message"`
	Data    any    `json:"data"`
}

type failRes struct {
	Status  string   `json:"status"`
	Message any      `json:"message"`
	Data    struct{} `json:"data"`
}

func SuccessResponse(data any) *successRes {
	return &successRes{
		Status:  "Success",
		Message: "Success",
		Data:    data,
	}
}

func SuccesNilsResponse() *successRes {
	return &successRes{
		Status:  "Success",
		Message: "Success",
		Data:    struct{}{},
	}
}

func FailResponseWithId(msg any) *failRes {
	m := fmt.Sprintf("Data with ID %v Not Found", msg)
	return &failRes{
		Status:  "Not Found",
		Message: m,
		Data:    struct{}{},
	}
}

func FailResponse(msg any) *failRes {
	return &failRes{
		Status:  "Error",
		Message: msg,
		Data:    struct{}{},
	}
}

func BadRequest(msg any) *failRes {
	return &failRes{
		Status:  "Bad Request",
		Message: msg,
		Data:    struct{}{},
	}
}
