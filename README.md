# Multi-Model AI Platform

An open-source, lightweight multi-model AI chat interface supporting 6 major AI providers with 35+ models.

## Features

- **Multi-Model Support**: Chat with 35+ models from OpenAI, Anthropic, Google, xAI, DeepSeek, and Groq
- **Streaming Responses**: Real-time token streaming via Server-Sent Events (SSE)
- **Conversation History**: Conversations persist locally using IndexedDB
- **Privacy-First**: API keys stored only in your browser, never sent to the server
- **Code Highlighting**: Syntax highlighting for code blocks via Prism.js
- **Markdown Support**: Basic formatting (bold, italic, code blocks, inline code)
- **Mobile-Responsive**: Works on desktop and mobile devices
- **Dark/Light Theme**: Toggle between themes for comfortable viewing
- **PWA Support**: Install as a standalone app on your device
- **Keyboard Shortcuts**: Quick access to common actions

## Supported Providers & Models

| Provider | Models |
|----------|--------|
| **OpenAI** | GPT-5.2, GPT-5, GPT-5 Mini, GPT-5 Nano, GPT-4.1, GPT-4o, GPT-4o-mini |
| **Anthropic** | Claude Opus 4.5, Claude Sonnet 4.5, Claude Opus 4.1, Claude Sonnet 4, Claude Opus 4, Claude 3.5 Haiku |
| **Google** | Gemini 3 Flash, Gemini 3 Pro, Gemini 2.5 Flash, Gemini 2.5 Flash Lite, Gemini 2.0 Flash, Gemini 2.0 Flash Lite, Gemini 1.5 Pro, Gemini 1.5 Flash |
| **xAI** | Grok 4, Grok 4 Fast, Grok Code Fast, Grok 3, Grok 3 Mini, Grok 2 |
| **DeepSeek** | DeepSeek Reasoner, DeepSeek Chat |
| **Groq** | Llama 3.3 70B, Llama 3.1 70B, Llama 3.1 8B, Mixtral 8x7B, Gemma2 9B |

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ryansansbury/model_platform.git
   cd model_platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**

   Navigate to `http://localhost:8000`

6. **Add your API keys**

   Click the Settings icon and enter your API keys for the providers you want to use.

## API Keys

You'll need API keys from the providers you want to use:

| Provider | Get API Key |
|----------|-------------|
| OpenAI | https://platform.openai.com/api-keys |
| Anthropic | https://console.anthropic.com/settings/keys |
| Google | https://aistudio.google.com/app/apikey |
| xAI | https://console.x.ai/ |
| DeepSeek | https://platform.deepseek.com/api_keys |
| Groq | https://console.groq.com/keys |

**Security Note**: API keys are stored locally in your browser. They are never sent to or stored on the server.

## Deployment

### Railway

1. Fork this repository
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repository
4. Deploy (Railway auto-detects the Procfile)

### Other Platforms

The app is a standard Flask application and can be deployed to:
- Heroku
- Render
- Fly.io
- Any platform supporting Python/Flask

## Project Structure

```
model_platform/
├── app.py              # Flask application with API endpoints
├── config.py           # Model configurations & pricing
├── api_clients.py      # Unified API client for all 6 providers
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment configuration
├── static/
│   ├── index.html      # Main HTML with settings modal
│   ├── manifest.json   # PWA manifest
│   ├── favicon.svg     # App favicon
│   ├── js/
│   │   ├── app.js      # Main application logic & UI
│   │   ├── api.js      # API communication & streaming
│   │   └── storage.js  # IndexedDB & localStorage management
│   ├── css/
│   │   └── styles.css  # All styles with dark/light themes
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
└── routes/
    └── __init__.py
```

## Technology Stack

- **Backend**: Python 3.8+, Flask, aiohttp, Flask-CORS, Flask-Limiter
- **Frontend**: Vanilla JavaScript, IndexedDB, localStorage
- **Styling**: Custom CSS with CSS Variables (dark/light themes)
- **Libraries**: Lucide Icons, Prism.js (syntax highlighting)
- **Deployment**: Gunicorn (WSGI server)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open model selector |
| `Cmd/Ctrl + N` | New conversation |
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `Escape` | Close popups |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/api/models` | GET | List all available models grouped by provider |
| `/api/chat` | POST | Send messages (supports streaming via SSE) |
| `/api/health` | GET | Health check endpoint |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.
