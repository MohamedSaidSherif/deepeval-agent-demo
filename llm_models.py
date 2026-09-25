"""Single source of truth for every LLM / embedding model name used in the project."""
from enum import StrEnum


class LLMModel(StrEnum):
    # OpenAI
    GPT_4O = "gpt-4o"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"

    # Anthropic
    CLAUDE_SONNET_4_6 = "claude-sonnet-4-6"

    # Ollama (local)
    GPT_OSS = "gpt-oss"
    QWEN_2_5_CODER = "qwen2.5-coder:latest"
