# Multi-Model AI Platform

An open-source, lightweight multi-model AI chat interface supporting 6 major AI providers.

## Features

- **Multi-Model Support**: Chat with 20+ models from OpenAI, Anthropic, Google, xAI, DeepSeek, and Groq
- **Streaming Responses**: Real-time token streaming for a smooth chat experience
- **Browser-Based Storage**: Conversations persist locally using IndexedDB
- **Privacy-First**: API keys stored only in your browser, never on the server
- **Mobile-Responsive**: Works great on desktop and mobile devices
- **Dark/Light Theme**: Toggle between themes for comfortable viewing
- **PWA Support**: Install as a standalone app on your device

## Supported Providers & Models

| Provider | Models |
|----------|--------|
| **OpenAI** | GPT-4o, GPT-4o-mini |
| **Anthropic** | Claude Sonnet 4, Claude 3.5 Haiku |
| **Google** | Gemini 2.0 Flash, Gemini 1.5 Pro |
| **xAI** | Grok 2 |
| **DeepSeek** | DeepSeek Chat, DeepSeek Reasoner |
| **Groq** | Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B |

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/platform.git
   cd platform
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

**Security Note**: API keys are stored locally in your browser using base64 encoding. They are never sent to or stored on the server.

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
platform/
├── app.py              # Flask application
├── config.py           # Model configurations
├── api_clients.py      # AI provider API clients
├── requirements.txt    # Python dependencies
├── Procfile            # Deployment configuration
├── static/
│   ├── index.html      # Main HTML
│   ├── manifest.json   # PWA manifest
│   ├── js/
│   │   ├── app.js      # Main application logic
│   │   ├── api.js      # API communication
│   │   └── storage.js  # IndexedDB storage
│   └── css/
│       └── styles.css  # All styles
└── routes/
    └── __init__.py
```

## Technology Stack

- **Backend**: Python, Flask, aiohttp
- **Frontend**: Vanilla JavaScript, IndexedDB
- **Styling**: Custom CSS with CSS Variables
- **Deployment**: Gunicorn

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open model selector |
| `Cmd/Ctrl + N` | New conversation |
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `Escape` | Close popups |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with love using:
- [Flask](https://flask.palletsprojects.com/)
- [Lucide Icons](https://lucide.dev/)
- [Prism.js](https://prismjs.com/)
