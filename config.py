"""
Configuration for Multi-Model AI Platform
Contains model definitions, pricing, and utility functions.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.resolve()
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Model configurations with pricing (costs are per 1K tokens)
MODEL_CONFIGS = {
    "openai": {
        # GPT-5.2 (Released December 2025) - Latest flagship
        "gpt-5.2": {
            "input_cost": 0.00175,
            "output_cost": 0.014,
            "max_tokens": 400000,
            "max_output": 32768,
            "description": "Latest GPT-5.2 flagship model",
            "strengths": ["coding", "agentic", "reasoning", "multimodal", "sota"],
        },
        # GPT-5 Models (Released August 2025)
        "gpt-5-2025-08-07": {
            "input_cost": 0.00125,
            "output_cost": 0.01,
            "max_tokens": 256000,
            "max_output": 32768,
            "description": "GPT-5 flagship model",
            "strengths": ["coding", "agentic", "reasoning", "multimodal"],
        },
        "gpt-5-mini-2025-08-07": {
            "input_cost": 0.001,
            "output_cost": 0.004,
            "max_tokens": 256000,
            "max_output": 16384,
            "description": "GPT-5 Mini - fast and efficient",
            "strengths": ["fast", "efficient", "balanced", "reasoning"],
        },
        "gpt-5-nano-2025-08-07": {
            "input_cost": 0.005,
            "output_cost": 0.015,
            "max_tokens": 256000,
            "max_output": 8192,
            "description": "GPT-5 Nano - lightweight",
            "strengths": ["fast", "lightweight", "quick_tasks"],
        },
        # GPT-4.1 (Released April 2025)
        "gpt-4.1": {
            "input_cost": 0.01,
            "output_cost": 0.03,
            "max_tokens": 1000000,
            "max_output": 32768,
            "description": "GPT-4.1 with 1M context",
            "strengths": ["long_context", "improved_instruction_following"],
        },
        # GPT-4o Family (Stable)
        "gpt-4o": {
            "input_cost": 0.0025,
            "output_cost": 0.01,
            "max_tokens": 128000,
            "max_output": 16384,
            "description": "GPT-4o multimodal",
            "strengths": ["multimodal", "general", "fast"],
        },
        "gpt-4o-mini": {
            "input_cost": 0.000075,
            "output_cost": 0.0003,
            "max_tokens": 128000,
            "max_output": 16384,
            "description": "GPT-4o Mini - fast and affordable",
            "strengths": ["fast", "cheap", "general"],
        },
    },
    "anthropic": {
        # Claude 4.5 Family (Latest - November 2025)
        "claude-opus-4-5-20251101": {
            "input_cost": 0.005,
            "output_cost": 0.025,
            "max_tokens": 200000,
            "max_output": 32768,
            "description": "Claude Opus 4.5 - most capable",
            "strengths": ["coding", "agents", "computer_use", "sota", "agentic"],
        },
        "claude-sonnet-4-5-20250929": {
            "input_cost": 0.003,
            "output_cost": 0.015,
            "max_tokens": 200000,
            "max_output": 64000,
            "description": "Claude Sonnet 4.5 - balanced",
            "strengths": ["coding", "agents", "computer_use"],
        },
        "claude-opus-4-1-20250805": {
            "input_cost": 0.015,
            "output_cost": 0.075,
            "max_tokens": 200000,
            "max_output": 32768,
            "description": "Claude Opus 4.1",
            "strengths": ["coding", "reasoning", "complex_tasks", "agentic"],
        },
        "claude-sonnet-4-20250514": {
            "input_cost": 0.003,
            "output_cost": 0.015,
            "max_tokens": 1000000,
            "max_output": 64000,
            "description": "Claude Sonnet 4 with 1M context",
            "strengths": ["coding", "long_context", "web_development"],
        },
        "claude-opus-4-20250514": {
            "input_cost": 0.015,
            "output_cost": 0.075,
            "max_tokens": 200000,
            "max_output": 32768,
            "description": "Claude Opus 4",
            "strengths": ["complex_reasoning", "coding", "autonomous_work"],
        },
        # Claude 3.5 Haiku (Still Available)
        "claude-3-5-haiku-20241022": {
            "input_cost": 0.001,
            "output_cost": 0.005,
            "max_tokens": 200000,
            "max_output": 8192,
            "description": "Claude 3.5 Haiku - fast and cheap",
            "strengths": ["fast", "cheap", "quick_fixes"],
        },
    },
    "google": {
        # Gemini 3 Family (Latest - December 2025)
        "gemini-3-flash-preview": {
            "input_cost": 0.0005,
            "output_cost": 0.003,
            "max_tokens": 1000000,
            "max_output": 64000,
            "description": "Gemini 3 Flash - ultra fast",
            "strengths": ["ultra_fast", "reasoning", "multimodal", "coding"],
        },
        "gemini-3-pro-preview": {
            "input_cost": 0.002,
            "output_cost": 0.012,
            "max_tokens": 1000000,
            "max_output": 64000,
            "description": "Gemini 3 Pro - highest quality",
            "strengths": ["reasoning", "agentic", "multimodal", "sota"],
        },
        # Gemini 2.5 Family
        "gemini-2.5-flash": {
            "input_cost": 0.000075,
            "output_cost": 0.0003,
            "max_tokens": 1000000,
            "max_output": 8192,
            "description": "Gemini 2.5 Flash",
            "strengths": ["fast", "long_context", "efficient"],
        },
        "gemini-2.5-flash-lite": {
            "input_cost": 0.0000375,
            "output_cost": 0.00015,
            "max_tokens": 1000000,
            "max_output": 8192,
            "description": "Gemini 2.5 Flash Lite - ultra cheap",
            "strengths": ["ultra_fast", "cheap", "high_volume"],
        },
        # Gemini 2.0 Family (Stable)
        "gemini-2.0-flash": {
            "input_cost": 0.000075,
            "output_cost": 0.0003,
            "max_tokens": 1000000,
            "max_output": 8192,
            "description": "Gemini 2.0 Flash - reliable",
            "strengths": ["fast", "reliable", "proven"],
        },
        "gemini-2.0-flash-lite": {
            "input_cost": 0.0000375,
            "output_cost": 0.00015,
            "max_tokens": 1000000,
            "max_output": 8192,
            "description": "Gemini 2.0 Flash Lite",
            "strengths": ["ultra_cheap", "fast", "budget"],
        },
        # Gemini 1.5 (Legacy)
        "gemini-1.5-pro": {
            "input_cost": 0.00125,
            "output_cost": 0.005,
            "max_tokens": 2000000,
            "max_output": 8192,
            "description": "Gemini 1.5 Pro - 2M context",
            "strengths": ["long_context", "multimodal", "reasoning"],
        },
        "gemini-1.5-flash": {
            "input_cost": 0.000075,
            "output_cost": 0.0003,
            "max_tokens": 1000000,
            "max_output": 8192,
            "description": "Gemini 1.5 Flash",
            "strengths": ["fast", "multimodal", "balanced"],
        },
    },
    "xai": {
        # Grok 4 (Latest)
        "grok-4-0709": {
            "input_cost": 0.003,
            "output_cost": 0.015,
            "max_tokens": 256000,
            "max_output": 32768,
            "description": "Grok 4 - most intelligent",
            "strengths": ["reasoning", "tool_use", "search"],
        },
        "grok-4-fast": {
            "input_cost": 0.001,
            "output_cost": 0.003,
            "max_tokens": 2000000,
            "max_output": 32768,
            "description": "Grok 4 Fast - 2M context",
            "strengths": ["ultra_fast", "efficient", "reasoning"],
        },
        "grok-code-fast-1": {
            "input_cost": 0.001,
            "output_cost": 0.003,
            "max_tokens": 256000,
            "max_output": 32768,
            "description": "Grok Code - coding specialized",
            "strengths": ["coding", "agentic", "fast"],
        },
        # Grok 3
        "grok-3": {
            "input_cost": 0.005,
            "output_cost": 0.015,
            "max_tokens": 1000000,
            "max_output": 32768,
            "description": "Grok 3",
            "strengths": ["reasoning", "long_context"],
        },
        "grok-3-mini": {
            "input_cost": 0.001,
            "output_cost": 0.003,
            "max_tokens": 500000,
            "max_output": 16384,
            "description": "Grok 3 Mini",
            "strengths": ["fast", "cheap"],
        },
        # Grok 2 (Legacy)
        "grok-2": {
            "input_cost": 0.002,
            "output_cost": 0.010,
            "max_tokens": 131072,
            "max_output": 32768,
            "description": "Grok 2",
            "strengths": ["reasoning", "general"],
        },
    },
    "deepseek": {
        "deepseek-reasoner": {
            "input_cost": 0.00055,
            "output_cost": 0.00219,
            "max_tokens": 128000,
            "max_output": 8192,
            "description": "DeepSeek Reasoner - chain of thought",
            "strengths": ["reasoning", "chain_of_thought", "math", "algorithms"],
        },
        "deepseek-chat": {
            "input_cost": 0.00027,
            "output_cost": 0.0011,
            "max_tokens": 128000,
            "max_output": 8192,
            "description": "DeepSeek Chat - ultra affordable",
            "strengths": ["ultra_cheap", "coding", "general", "efficient"],
        },
    },
    "groq": {
        # Llama 3.3 70B
        "llama-3.3-70b-versatile": {
            "input_cost": 0.00059,
            "output_cost": 0.00079,
            "max_tokens": 128000,
            "max_output": 32768,
            "description": "Llama 3.3 70B on Groq - ultra fast",
            "strengths": ["ultra_fast", "free_tier", "high_quality", "reasoning"],
        },
        # Llama 3.1
        "llama-3.1-70b-versatile": {
            "input_cost": 0.00059,
            "output_cost": 0.00079,
            "max_tokens": 128000,
            "max_output": 32768,
            "description": "Llama 3.1 70B on Groq",
            "strengths": ["ultra_fast", "free_tier", "coding", "reasoning"],
        },
        "llama-3.1-8b-instant": {
            "input_cost": 0.00005,
            "output_cost": 0.00008,
            "max_tokens": 128000,
            "max_output": 8192,
            "description": "Llama 3.1 8B - fastest",
            "strengths": ["ultra_fast", "ultra_cheap", "free_tier"],
        },
        # Mixtral
        "mixtral-8x7b-32768": {
            "input_cost": 0.00024,
            "output_cost": 0.00024,
            "max_tokens": 32768,
            "max_output": 8192,
            "description": "Mixtral 8x7B MoE",
            "strengths": ["ultra_fast", "free_tier", "balanced", "coding"],
        },
        # Gemma
        "gemma2-9b-it": {
            "input_cost": 0.00020,
            "output_cost": 0.00020,
            "max_tokens": 8192,
            "max_output": 8192,
            "description": "Gemma 2 9B",
            "strengths": ["fast", "efficient", "google_quality"],
        },
    },
}


def calculate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on token usage."""
    try:
        if provider in MODEL_CONFIGS and model in MODEL_CONFIGS[provider]:
            config = MODEL_CONFIGS[provider][model]
            input_cost = (input_tokens / 1000) * config['input_cost']
            output_cost = (output_tokens / 1000) * config['output_cost']
            return input_cost + output_cost
        return 0.0
    except Exception:
        return 0.0


def get_model_max_tokens(provider: str, model: str) -> int:
    """Get the maximum output tokens for a model."""
    try:
        if provider in MODEL_CONFIGS and model in MODEL_CONFIGS[provider]:
            return MODEL_CONFIGS[provider][model].get('max_output', 4096)
        return 4096
    except Exception:
        return 4096


def get_all_models() -> list:
    """Get a flat list of all available models."""
    models = []
    for provider, provider_models in MODEL_CONFIGS.items():
        for model_name, config in provider_models.items():
            models.append({
                'provider': provider,
                'model': model_name,
                'description': config.get('description', ''),
                'max_tokens': config.get('max_tokens', 128000),
                'max_output': config.get('max_output', 4096),
                'input_cost': config.get('input_cost', 0),
                'output_cost': config.get('output_cost', 0),
                'strengths': config.get('strengths', []),
            })
    return models
