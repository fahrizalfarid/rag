package main

import (
	"runtime"

	"github.com/fahrizalfarid/rag/cmd"
)

func init() {
	runtime.GOMAXPROCS(1)
}

func main() {
	cmd.Execute()
}
