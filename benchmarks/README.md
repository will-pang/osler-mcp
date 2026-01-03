# General Instructions

To run:

```bash
uv run python -m benchmarks.run_eval
```

## Running local models (via Ollama)

### gpt-oss:20b

```bash
# Download base model
ollama pull gpt-oss:20b

## Change context window
cat <<'EOF' > Modelfile.gpt20b
FROM gpt-oss:20b
PARAMETER num_ctx 32768
EOF

## Create model with updated context window
ollama create gpt-oss-20b-ctx32k -f Modelfile.gpt20b

## Optional: Check if model is properly created
ollama list

## Run model
ollama run gpt-oss-20b-ctx32k

## Test
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:20b",
    "messages": [{"role":"user","content":"Say hi"}]
  }'
```

### qwen2.5:7b
```bash
# Download base model
ollama pull qwen2.5:7b

## Change context window
cat <<'EOF' > Modelfile.qwen2_5_7b
FROM qwen2.5:7b
PARAMETER num_ctx 32768
EOF

## Create model with updated context window
ollama create qwen2.5:7b-ctx32k -f Modelfile.qwen2_5_7b

## Optional: Check if model is properly created
ollama list

## Run Model
ollama run qwen2.5:7b-ctx32k
```
