"""
Multi-Model AI Platform
A lightweight, open-source multi-model AI chat interface.
"""

import os
import json
import time
import asyncio
import logging
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import MODEL_CONFIGS, get_all_models, calculate_cost
from api_clients import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')

# CORS configuration
CORS(app, origins=['*'], supports_credentials=True)

# Rate limiting (in-memory)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://"
)

# Disable caching for development
@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    return response


# =============================================================================
# STATIC FILE SERVING
# =============================================================================

@app.route('/')
def serve_index():
    """Serve the main application."""
    return send_from_directory('static', 'index.html')


@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files."""
    return send_from_directory('static/js', filename)


@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files."""
    return send_from_directory('static/css', filename)


@app.route('/icons/<path:filename>')
def serve_icons(filename):
    """Serve icon files."""
    return send_from_directory('static/icons', filename)


@app.route('/manifest.json')
def serve_manifest():
    """Serve PWA manifest."""
    return send_from_directory('static', 'manifest.json')


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/models', methods=['GET'])
def get_models():
    """Return list of available models."""
    return jsonify({
        'models': get_all_models(),
        'providers': list(MODEL_CONFIGS.keys())
    })


@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    """
    Main chat endpoint.

    Expected JSON body:
    {
        "provider": "openai",
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": false,
        "api_keys": {
            "openai": "sk-...",
            "anthropic": "sk-ant-..."
        }
    }
    """
    try:
        start_time = time.time()
        data = request.json

        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        provider = data.get('provider')
        model = data.get('model')
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens')
        stream = data.get('stream', False)
        api_keys = data.get('api_keys', {})

        # Validate required fields
        if not provider:
            return jsonify({'error': 'Provider is required'}), 400
        if not model:
            return jsonify({'error': 'Model is required'}), 400
        if not messages:
            return jsonify({'error': 'Messages are required'}), 400
        if provider not in api_keys:
            return jsonify({'error': f'API key for {provider} is required'}), 400

        # Create API client
        client = APIClient(api_keys)

        if stream:
            # Streaming response
            def generate():
                async def stream_response():
                    full_response = ""
                    try:
                        async for chunk in client.stream(
                            provider, model, messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        ):
                            full_response += chunk
                            yield f"data: {json.dumps({'content': chunk})}\n\n"

                        # Send final metadata
                        response_time = time.time() - start_time
                        # Estimate tokens (rough approximation)
                        input_tokens = sum(len(m.get('content', '')) for m in messages) // 4
                        output_tokens = len(full_response) // 4
                        cost = calculate_cost(provider, model, input_tokens, output_tokens)

                        metadata = {
                            'type': 'metadata',
                            'provider': provider,
                            'model': model,
                            'input_tokens': input_tokens,
                            'output_tokens': output_tokens,
                            'cost': cost,
                            'response_time': response_time
                        }
                        yield f"data: {json.dumps(metadata)}\n\n"
                        yield "data: [DONE]\n\n"

                    except Exception as e:
                        logger.error(f"Streaming error: {e}")
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"

                # Run async generator synchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    agen = stream_response()
                    while True:
                        try:
                            chunk = loop.run_until_complete(agen.__anext__())
                            yield chunk
                        except StopAsyncIteration:
                            break
                finally:
                    loop.close()

            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )

        else:
            # Non-streaming response
            async def make_call():
                return await client.call(
                    provider, model, messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            result = asyncio.run(make_call())
            response_time = time.time() - start_time

            return jsonify({
                'response': result['response'],
                'provider': provider,
                'model': result.get('model', model),
                'input_tokens': result['input_tokens'],
                'output_tokens': result['output_tokens'],
                'cost': result['cost'],
                'response_time': response_time
            })

    except Exception as e:
        logger.error(f"Chat error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    return jsonify({
        'error': 'Rate limit exceeded. Please slow down.',
        'retry_after': e.description
    }), 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Multi-Model AI Platform")
    print("=" * 50)
    print("\n  Starting server...")
    print("  Open http://localhost:8000 in your browser")
    print("\n  Supported providers:")
    for provider in MODEL_CONFIGS.keys():
        print(f"    - {provider}")
    print("\n" + "=" * 50 + "\n")

    app.run(
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
        host='0.0.0.0',
        port=int(os.getenv('PORT', 8000))
    )
