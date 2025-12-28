"""
API Clients for Multi-Model AI Platform
Handles API calls to OpenAI, Anthropic, Google, xAI, DeepSeek, and Groq.
"""

import os
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator

from config import calculate_cost, get_model_max_tokens

logger = logging.getLogger(__name__)


class APIClient:
    """Unified API client for all providers."""

    def __init__(self, api_keys: Dict[str, str] = None):
        """
        Initialize with API keys.

        Args:
            api_keys: Dict mapping provider names to API keys
        """
        self.api_keys = api_keys or {}

    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        return self.api_keys.get(provider)

    def _is_reasoning_model(self, model: str) -> bool:
        """Check if model is an OpenAI reasoning model that doesn't support temperature."""
        reasoning_prefixes = ('o1', 'o3')
        model_lower = model.lower()
        return any(model_lower.startswith(prefix) or f'/{prefix}' in model_lower for prefix in reasoning_prefixes)

    async def call_openai(self, model: str, messages: List[Dict],
                          temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Call OpenAI API."""
        api_key = self.get_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not provided")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
        }

        # Reasoning models (o1, o3) don't support temperature parameter
        if not self._is_reasoning_model(model):
            data["temperature"] = temperature

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                result = await response.json()

                if response.status != 200:
                    error_msg = result.get('error', {}).get('message', str(result))
                    raise Exception(f"OpenAI API error: {error_msg}")

                return {
                    "response": result["choices"][0]["message"]["content"],
                    "input_tokens": result["usage"]["prompt_tokens"],
                    "output_tokens": result["usage"]["completion_tokens"],
                    "model": result.get("model", model),
                }

    async def stream_openai(self, model: str, messages: List[Dict],
                            temperature: float = 0.7, max_tokens: int = 4096) -> AsyncGenerator[str, None]:
        """Stream from OpenAI API."""
        api_key = self.get_key('openai')
        if not api_key:
            raise ValueError("OpenAI API key not provided")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": messages,
            "max_completion_tokens": max_tokens,
            "stream": True,
        }

        # Reasoning models (o1, o3) don't support temperature parameter
        if not self._is_reasoning_model(model):
            data["temperature"] = temperature

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    error = await response.json()
                    raise Exception(f"OpenAI API error: {error}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            import json
                            chunk = json.loads(data_str)
                            delta = chunk.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue

    async def call_anthropic(self, model: str, messages: List[Dict],
                             temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Call Anthropic API."""
        api_key = self.get_key('anthropic')
        if not api_key:
            raise ValueError("Anthropic API key not provided")

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Extract system message
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_messages,
        }

        if system_content:
            data["system"] = system_content

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                result = await response.json()

                if response.status != 200:
                    error_msg = result.get('error', {}).get('message', str(result))
                    raise Exception(f"Anthropic API error: {error_msg}")

                response_text = ""
                for block in result.get("content", []):
                    if block["type"] == "text":
                        response_text += block["text"]

                return {
                    "response": response_text,
                    "input_tokens": result["usage"]["input_tokens"],
                    "output_tokens": result["usage"]["output_tokens"],
                    "model": result.get("model", model),
                }

    async def stream_anthropic(self, model: str, messages: List[Dict],
                               temperature: float = 0.7, max_tokens: int = 4096) -> AsyncGenerator[str, None]:
        """Stream from Anthropic API."""
        api_key = self.get_key('anthropic')
        if not api_key:
            raise ValueError("Anthropic API key not provided")

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # Extract system message
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_messages,
            "stream": True,
        }

        if system_content:
            data["system"] = system_content

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    error = await response.json()
                    raise Exception(f"Anthropic API error: {error}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        try:
                            import json
                            event = json.loads(line[6:])
                            if event.get('type') == 'content_block_delta':
                                delta = event.get('delta', {})
                                if delta.get('type') == 'text_delta':
                                    yield delta.get('text', '')
                        except json.JSONDecodeError:
                            continue

    async def call_google(self, model: str, messages: List[Dict],
                          temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Call Google Gemini API."""
        api_key = self.get_key('google')
        if not api_key:
            raise ValueError("Google API key not provided")

        # Convert messages to Google format
        contents = []
        system_instruction = ""

        for msg in messages:
            if msg['role'] == 'system':
                system_instruction = msg['content']
            elif msg['role'] == 'user':
                contents.append({'role': 'user', 'parts': [{'text': msg['content']}]})
            elif msg['role'] == 'assistant':
                contents.append({'role': 'model', 'parts': [{'text': msg['content']}]})

        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        if system_instruction:
            payload['systemInstruction'] = {'parts': [{'text': system_instruction}]}

        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}'

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                result = await response.json()

                if response.status != 200:
                    error_msg = result.get('error', {}).get('message', str(result))
                    raise Exception(f"Google API error: {error_msg}")

                if 'candidates' not in result or not result['candidates']:
                    raise Exception("No response from Google API")

                candidate = result['candidates'][0]
                if 'content' not in candidate or 'parts' not in candidate['content']:
                    raise Exception("Empty response from Google API")

                response_text = candidate['content']['parts'][0]['text']
                usage = result.get('usageMetadata', {})

                return {
                    "response": response_text,
                    "input_tokens": usage.get('promptTokenCount', 0),
                    "output_tokens": usage.get('candidatesTokenCount', 0),
                    "model": model,
                }

    async def stream_google(self, model: str, messages: List[Dict],
                            temperature: float = 0.7, max_tokens: int = 4096) -> AsyncGenerator[str, None]:
        """Stream from Google Gemini API."""
        api_key = self.get_key('google')
        if not api_key:
            raise ValueError("Google API key not provided")

        # Convert messages to Google format
        contents = []
        system_instruction = ""

        for msg in messages:
            if msg['role'] == 'system':
                system_instruction = msg['content']
            elif msg['role'] == 'user':
                contents.append({'role': 'user', 'parts': [{'text': msg['content']}]})
            elif msg['role'] == 'assistant':
                contents.append({'role': 'model', 'parts': [{'text': msg['content']}]})

        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens
            }
        }

        if system_instruction:
            payload['systemInstruction'] = {'parts': [{'text': system_instruction}]}

        url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}'

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status != 200:
                    error = await response.json()
                    raise Exception(f"Google API error: {error}")

                buffer = ""
                async for chunk in response.content:
                    buffer += chunk.decode('utf-8')
                    # Google streams JSON array chunks
                    while True:
                        try:
                            import json
                            # Try to parse complete JSON objects
                            if buffer.strip().startswith('['):
                                buffer = buffer.strip()[1:]
                            if buffer.strip().startswith(','):
                                buffer = buffer.strip()[1:]
                            if buffer.strip().startswith(']'):
                                break

                            # Find complete JSON object
                            depth = 0
                            end_idx = -1
                            for i, c in enumerate(buffer):
                                if c == '{':
                                    depth += 1
                                elif c == '}':
                                    depth -= 1
                                    if depth == 0:
                                        end_idx = i + 1
                                        break

                            if end_idx > 0:
                                obj_str = buffer[:end_idx]
                                buffer = buffer[end_idx:]
                                obj = json.loads(obj_str)

                                candidates = obj.get('candidates', [])
                                if candidates:
                                    content = candidates[0].get('content', {})
                                    parts = content.get('parts', [])
                                    for part in parts:
                                        if 'text' in part:
                                            yield part['text']
                            else:
                                break
                        except json.JSONDecodeError:
                            break

    async def call_xai(self, model: str, messages: List[Dict],
                       temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Call xAI Grok API."""
        api_key = self.get_key('xai')
        if not api_key:
            raise ValueError("xAI API key not provided")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                result = await response.json()

                if response.status != 200:
                    raise Exception(f"xAI API error: {result}")

                return {
                    "response": result['choices'][0]['message']['content'],
                    "input_tokens": result['usage']['prompt_tokens'],
                    "output_tokens": result['usage']['completion_tokens'],
                    "model": result.get('model', model),
                }

    async def call_deepseek(self, model: str, messages: List[Dict],
                            temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Call DeepSeek API."""
        api_key = self.get_key('deepseek')
        if not api_key:
            raise ValueError("DeepSeek API key not provided")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                result = await response.json()

                if response.status != 200:
                    raise Exception(f"DeepSeek API error: {result}")

                return {
                    "response": result['choices'][0]['message']['content'],
                    "input_tokens": result['usage']['prompt_tokens'],
                    "output_tokens": result['usage']['completion_tokens'],
                    "model": result.get('model', model),
                }

    async def call_groq(self, model: str, messages: List[Dict],
                        temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Call Groq API."""
        api_key = self.get_key('groq')
        if not api_key:
            raise ValueError("Groq API key not provided")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                result = await response.json()

                if response.status != 200:
                    if response.status == 429:
                        raise Exception("Groq rate limit exceeded. Please wait and try again.")
                    raise Exception(f"Groq API error: {result}")

                return {
                    "response": result['choices'][0]['message']['content'],
                    "input_tokens": result['usage']['prompt_tokens'],
                    "output_tokens": result['usage']['completion_tokens'],
                    "model": result.get('model', model),
                }

    async def call(self, provider: str, model: str, messages: List[Dict],
                   temperature: float = 0.7, max_tokens: int = None) -> Dict[str, Any]:
        """
        Unified API call method.

        Args:
            provider: Provider name (openai, anthropic, google, xai, deepseek, groq)
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation
            max_tokens: Maximum output tokens (uses model default if not specified)

        Returns:
            Dict with response, input_tokens, output_tokens, cost, model
        """
        if max_tokens is None:
            max_tokens = get_model_max_tokens(provider, model)

        # Route to appropriate provider
        if provider == 'openai':
            result = await self.call_openai(model, messages, temperature, max_tokens)
        elif provider == 'anthropic':
            result = await self.call_anthropic(model, messages, temperature, max_tokens)
        elif provider == 'google':
            result = await self.call_google(model, messages, temperature, max_tokens)
        elif provider == 'xai':
            result = await self.call_xai(model, messages, temperature, max_tokens)
        elif provider == 'deepseek':
            result = await self.call_deepseek(model, messages, temperature, max_tokens)
        elif provider == 'groq':
            result = await self.call_groq(model, messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Calculate cost
        cost = calculate_cost(provider, model, result['input_tokens'], result['output_tokens'])
        result['cost'] = cost

        return result

    async def stream(self, provider: str, model: str, messages: List[Dict],
                     temperature: float = 0.7, max_tokens: int = None) -> AsyncGenerator[str, None]:
        """
        Unified streaming method.

        Args:
            provider: Provider name
            model: Model name
            messages: List of message dicts
            temperature: Temperature for generation
            max_tokens: Maximum output tokens

        Yields:
            Text chunks as they arrive
        """
        if max_tokens is None:
            max_tokens = get_model_max_tokens(provider, model)

        if provider == 'openai':
            async for chunk in self.stream_openai(model, messages, temperature, max_tokens):
                yield chunk
        elif provider == 'anthropic':
            async for chunk in self.stream_anthropic(model, messages, temperature, max_tokens):
                yield chunk
        elif provider == 'google':
            async for chunk in self.stream_google(model, messages, temperature, max_tokens):
                yield chunk
        else:
            # For providers without streaming, fall back to non-streaming
            result = await self.call(provider, model, messages, temperature, max_tokens)
            yield result['response']


def call_api(provider: str, model: str, messages: List[Dict],
             api_keys: Dict[str, str], **params) -> Dict[str, Any]:
    """
    Synchronous wrapper for API calls.

    Args:
        provider: Provider name
        model: Model name
        messages: List of message dicts
        api_keys: Dict mapping provider names to API keys
        **params: Additional parameters (temperature, max_tokens)

    Returns:
        Dict with response, tokens, cost
    """
    client = APIClient(api_keys)

    async def _call():
        return await client.call(
            provider, model, messages,
            temperature=params.get('temperature', 0.7),
            max_tokens=params.get('max_tokens')
        )

    return asyncio.run(_call())
