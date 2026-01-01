To run:

# General Instructions

```bash
uv run python -m benchmarks.run_eval
```

## Downloading Open Source Models locally (Ollama)

### gpt-oss:20b

```bash
ollama pull gpt-oss:20b
# quick sanity check (optional)
ollama run gpt-oss:20b

## Change context window
cat <<'EOF' > Modelfile.custom
FROM gpt-oss:20b
PARAMETER num_ctx 32768
EOF

## Create model
ollama create gpt-oss-20b-ctx32k -f Modelfile.custom

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
