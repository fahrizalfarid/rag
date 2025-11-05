#!/bin/sh
/path/llama.cpp/build/bin/llama-server -m /path/models/starstreak-7b-Q4_K_M.gguf \
--host 0.0.0.0 --port 8081
