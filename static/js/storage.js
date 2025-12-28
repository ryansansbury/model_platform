/**
 * Storage Module
 * Handles browser-based storage for conversations and settings using IndexedDB
 */

const Storage = {
    DB_NAME: 'MultiModelAI',
    DB_VERSION: 1,
    db: null,

    /**
     * Initialize IndexedDB
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.DB_NAME, this.DB_VERSION);

            request.onerror = () => reject(request.error);

            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Conversations store
                if (!db.objectStoreNames.contains('conversations')) {
                    const convStore = db.createObjectStore('conversations', { keyPath: 'id' });
                    convStore.createIndex('createdAt', 'createdAt', { unique: false });
                }

                // Messages store
                if (!db.objectStoreNames.contains('messages')) {
                    const msgStore = db.createObjectStore('messages', { keyPath: 'id' });
                    msgStore.createIndex('conversationId', 'conversationId', { unique: false });
                    msgStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    },

    /**
     * Generate a unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },

    // =========================================================================
    // CONVERSATIONS
    // =========================================================================

    /**
     * Get all conversations
     */
    async getConversations() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readonly');
            const store = transaction.objectStore('conversations');
            const request = store.getAll();

            request.onsuccess = () => {
                const conversations = request.result || [];
                // Sort by most recent
                conversations.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
                resolve(conversations);
            };

            request.onerror = () => reject(request.error);
        });
    },

    /**
     * Get a single conversation
     */
    async getConversation(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readonly');
            const store = transaction.objectStore('conversations');
            const request = store.get(id);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    },

    /**
     * Create a new conversation
     */
    async createConversation(title = 'New Conversation') {
        const conversation = {
            id: this.generateId(),
            title,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            messageCount: 0
        };

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readwrite');
            const store = transaction.objectStore('conversations');
            const request = store.add(conversation);

            request.onsuccess = () => resolve(conversation);
            request.onerror = () => reject(request.error);
        });
    },

    /**
     * Update a conversation
     */
    async updateConversation(id, updates) {
        const conversation = await this.getConversation(id);
        if (!conversation) return null;

        const updated = {
            ...conversation,
            ...updates,
            updatedAt: new Date().toISOString()
        };

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readwrite');
            const store = transaction.objectStore('conversations');
            const request = store.put(updated);

            request.onsuccess = () => resolve(updated);
            request.onerror = () => reject(request.error);
        });
    },

    /**
     * Delete a conversation and its messages
     */
    async deleteConversation(id) {
        // Delete messages first
        const messages = await this.getMessages(id);
        for (const msg of messages) {
            await this.deleteMessage(msg.id);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readwrite');
            const store = transaction.objectStore('conversations');
            const request = store.delete(id);

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    },

    /**
     * Delete all conversations
     */
    async deleteAllConversations() {
        const conversations = await this.getConversations();
        for (const conv of conversations) {
            await this.deleteConversation(conv.id);
        }
        return true;
    },

    // =========================================================================
    // MESSAGES
    // =========================================================================

    /**
     * Get messages for a conversation
     */
    async getMessages(conversationId) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['messages'], 'readonly');
            const store = transaction.objectStore('messages');
            const index = store.index('conversationId');
            const request = index.getAll(conversationId);

            request.onsuccess = () => {
                const messages = request.result || [];
                messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                resolve(messages);
            };

            request.onerror = () => reject(request.error);
        });
    },

    /**
     * Add a message
     */
    async addMessage(conversationId, role, content, metadata = {}) {
        const message = {
            id: this.generateId(),
            conversationId,
            role,
            content,
            timestamp: new Date().toISOString(),
            ...metadata
        };

        await new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['messages'], 'readwrite');
            const store = transaction.objectStore('messages');
            const request = store.add(message);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });

        // Update conversation
        const messages = await this.getMessages(conversationId);
        await this.updateConversation(conversationId, {
            messageCount: messages.length,
            lastMessage: content.substring(0, 100)
        });

        return message;
    },

    /**
     * Delete a message
     */
    async deleteMessage(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['messages'], 'readwrite');
            const store = transaction.objectStore('messages');
            const request = store.delete(id);

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    },

    // =========================================================================
    // API KEYS (localStorage with basic obfuscation)
    // =========================================================================

    /**
     * Save API keys
     */
    saveApiKeys(keys) {
        // Basic encoding (not true encryption, but prevents casual viewing)
        const encoded = btoa(JSON.stringify(keys));
        localStorage.setItem('api_keys', encoded);
    },

    /**
     * Get API keys
     */
    getApiKeys() {
        try {
            const encoded = localStorage.getItem('api_keys');
            if (!encoded) return {};
            return JSON.parse(atob(encoded));
        } catch {
            return {};
        }
    },

    /**
     * Get a specific API key
     */
    getApiKey(provider) {
        const keys = this.getApiKeys();
        return keys[provider] || null;
    },

    /**
     * Check if any API keys are set
     */
    hasApiKeys() {
        const keys = this.getApiKeys();
        return Object.values(keys).some(k => k && k.length > 0);
    },

    // =========================================================================
    // SETTINGS
    // =========================================================================

    /**
     * Save a setting
     */
    saveSetting(key, value) {
        localStorage.setItem(`setting_${key}`, JSON.stringify(value));
    },

    /**
     * Get a setting
     */
    getSetting(key, defaultValue = null) {
        try {
            const value = localStorage.getItem(`setting_${key}`);
            return value ? JSON.parse(value) : defaultValue;
        } catch {
            return defaultValue;
        }
    },

    /**
     * Get current model
     */
    getCurrentModel() {
        return this.getSetting('currentModel', {
            provider: 'anthropic',
            model: 'claude-sonnet-4-20250514'
        });
    },

    /**
     * Save current model
     */
    saveCurrentModel(provider, model) {
        this.saveSetting('currentModel', { provider, model });
    },

    /**
     * Get theme
     */
    getTheme() {
        return this.getSetting('theme', 'dark');
    },

    /**
     * Save theme
     */
    saveTheme(theme) {
        this.saveSetting('theme', theme);
    }
};

// Initialize on load
window.Storage = Storage;
