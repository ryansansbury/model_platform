/**
 * API Module
 * Handles communication with the backend API
 */

const API = {
    baseUrl: '',

    /**
     * Get available models from the server
     */
    async getModels() {
        try {
            const response = await fetch(`${this.baseUrl}/api/models`);
            if (!response.ok) throw new Error('Failed to fetch models');
            return await response.json();
        } catch (error) {
            console.error('Error fetching models:', error);
            return { models: [], providers: [] };
        }
    },

    /**
     * Send a chat message (streaming)
     */
    async chat(options) {
        const {
            provider,
            model,
            messages,
            temperature = 0.7,
            maxTokens = 4096,
            onChunk,
            onComplete,
            onError
        } = options;

        const apiKeys = Storage.getApiKeys();

        if (!apiKeys[provider]) {
            onError(new Error(`No API key configured for ${provider}. Please add your API key in Settings.`));
            return;
        }

        try {
            const response = await fetch(`${this.baseUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    provider,
                    model,
                    messages,
                    temperature,
                    max_tokens: maxTokens,
                    stream: true,
                    api_keys: apiKeys
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'API request failed');
            }

            // Handle SSE streaming
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let fullResponse = '';
            let metadata = null;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim();

                        if (data === '[DONE]') {
                            onComplete({ response: fullResponse, metadata });
                            return;
                        }

                        try {
                            const parsed = JSON.parse(data);

                            if (parsed.error) {
                                onError(new Error(parsed.error));
                                return;
                            }

                            if (parsed.type === 'metadata') {
                                metadata = parsed;
                            } else if (parsed.content) {
                                fullResponse += parsed.content;
                                onChunk(parsed.content);
                            }
                        } catch (e) {
                            // Ignore parse errors for incomplete chunks
                        }
                    }
                }
            }

            // If we get here without [DONE], complete anyway
            onComplete({ response: fullResponse, metadata });

        } catch (error) {
            console.error('Chat error:', error);
            onError(error);
        }
    },

    /**
     * Send a chat message (non-streaming)
     */
    async chatSync(options) {
        const {
            provider,
            model,
            messages,
            temperature = 0.7,
            maxTokens = 4096
        } = options;

        const apiKeys = Storage.getApiKeys();

        if (!apiKeys[provider]) {
            throw new Error(`No API key configured for ${provider}`);
        }

        const response = await fetch(`${this.baseUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                provider,
                model,
                messages,
                temperature,
                max_tokens: maxTokens,
                stream: false,
                api_keys: apiKeys
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'API request failed');
        }

        return await response.json();
    },

    /**
     * Check server health
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`);
            return response.ok;
        } catch {
            return false;
        }
    }
};

window.API = API;
