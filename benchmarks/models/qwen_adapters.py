import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from benchmarks.models.openai_adapters import BaseAsyncOpenAIAdapter

load_dotenv()


class AsyncQwenAdapter(BaseAsyncOpenAIAdapter):
    def __init__(self, model, base_url=None, api_key=None):
        base_url = base_url or "http://localhost:11434/v1"
        api_key = api_key or os.environ.get("QWEN_API_KEY", "qwen")
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        super().__init__(client, model)
