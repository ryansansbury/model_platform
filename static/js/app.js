/**
 * Main Application
 * Multi-Model AI Platform
 */

const App = {
    // State
    models: [],
    currentModel: null,
    currentConversation: null,
    isStreaming: false,

    // DOM Elements
    elements: {},

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Multi-Model AI Platform...');

        // Cache DOM elements
        this.cacheElements();

        // Initialize storage
        await Storage.init();

        // Load theme
        this.loadTheme();

        // Load models
        await this.loadModels();

        // Load saved model
        this.loadCurrentModel();

        // Load conversations
        await this.loadConversations();

        // Set up event listeners
        this.setupEventListeners();

        // Hide loading screen
        this.hideLoading();

        // Initialize icons
        if (window.lucide) {
            lucide.createIcons();
        }

        console.log('App initialized');
    },

    /**
     * Cache DOM elements for quick access
     */
    cacheElements() {
        this.elements = {
            loadingScreen: document.getElementById('loadingScreen'),
            chatInput: document.getElementById('chatInput'),
            sendBtn: document.getElementById('sendBtn'),
            chatMessages: document.getElementById('chatMessages'),
            emptyState: document.getElementById('emptyState'),
            modelSelectorBtn: document.getElementById('modelSelectorBtn'),
            currentModelDisplay: document.getElementById('currentModelDisplay'),
            modelSelectorPopup: document.getElementById('modelSelectorPopup'),
            modelList: document.getElementById('modelList'),
            modelSearchInput: document.getElementById('modelSearchInput'),
            modelPopupCloseBtn: document.getElementById('modelPopupCloseBtn'),
            conversationList: document.getElementById('conversationList'),
            newChatBtn: document.getElementById('newChatBtn'),
            clearAllBtn: document.getElementById('clearAllBtn'),
            settingsBtn: document.getElementById('settingsBtn'),
            settingsModal: document.getElementById('settingsModal'),
            modelIndicator: document.getElementById('modelIndicator'),
            scrollToBottomBtn: document.getElementById('scrollToBottomBtn'),
            sidebar: document.getElementById('sidebar'),
            sidebarOverlay: document.getElementById('sidebarOverlay'),
            mobileMenuBtn: document.getElementById('mobileMenuBtn'),
            themeToggleBtn: document.getElementById('themeToggleBtn'),
            themeIcon: document.getElementById('themeIcon')
        };
    },

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Send message
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());
        this.elements.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        this.elements.chatInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        // Model selector
        this.elements.modelSelectorBtn.addEventListener('click', () => this.toggleModelSelector());
        this.elements.modelPopupCloseBtn.addEventListener('click', () => this.closeModelSelector());
        this.elements.modelSearchInput.addEventListener('input', (e) => this.filterModels(e.target.value));

        // Close model selector on outside click
        document.addEventListener('click', (e) => {
            if (!this.elements.modelSelectorPopup.contains(e.target) &&
                !this.elements.modelSelectorBtn.contains(e.target)) {
                this.closeModelSelector();
            }
        });

        // New chat
        this.elements.newChatBtn.addEventListener('click', () => this.newConversation());

        // Clear all
        this.elements.clearAllBtn.addEventListener('click', () => this.clearAllConversations());

        // Settings
        this.elements.settingsBtn.addEventListener('click', () => this.openSettings());

        // Scroll to bottom
        this.elements.scrollToBottomBtn.addEventListener('click', () => this.scrollToBottom());
        this.elements.chatMessages.addEventListener('scroll', () => this.checkScrollPosition());

        // Mobile menu
        this.elements.mobileMenuBtn.addEventListener('click', () => this.toggleSidebar());
        this.elements.sidebarOverlay.addEventListener('click', () => this.closeSidebar());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape to close popups
            if (e.key === 'Escape') {
                this.closeModelSelector();
                this.closeSettings();
                this.closeSidebar();
            }

            // Cmd/Ctrl + K for model selector
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                this.toggleModelSelector();
            }

            // Cmd/Ctrl + N for new chat
            if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
                e.preventDefault();
                this.newConversation();
            }
        });
    },

    /**
     * Hide loading screen
     */
    hideLoading() {
        this.elements.loadingScreen.classList.add('hidden');
    },

    // =========================================================================
    // THEME
    // =========================================================================

    loadTheme() {
        const theme = Storage.getTheme();
        document.documentElement.setAttribute('data-theme', theme);
        this.updateThemeIcon(theme);
    },

    updateThemeIcon(theme) {
        if (this.elements.themeIcon) {
            this.elements.themeIcon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
            if (window.lucide) lucide.createIcons();
        }
    },

    // =========================================================================
    // MODELS
    // =========================================================================

    async loadModels() {
        const data = await API.getModels();
        this.models = data.models || [];
        this.renderModelList();
    },

    loadCurrentModel() {
        const saved = Storage.getCurrentModel();
        const model = this.models.find(m =>
            m.provider === saved.provider && m.model === saved.model
        );

        if (model) {
            this.selectModel(model.provider, model.model, false);
        } else if (this.models.length > 0) {
            // Default to first model
            this.selectModel(this.models[0].provider, this.models[0].model, false);
        }
    },

    renderModelList(filter = '') {
        const filterLower = filter.toLowerCase();

        // Group by provider
        const grouped = {};
        for (const model of this.models) {
            if (filter && !model.model.toLowerCase().includes(filterLower) &&
                !model.provider.toLowerCase().includes(filterLower) &&
                !model.description.toLowerCase().includes(filterLower)) {
                continue;
            }

            if (!grouped[model.provider]) {
                grouped[model.provider] = [];
            }
            grouped[model.provider].push(model);
        }

        let html = '';
        for (const [provider, models] of Object.entries(grouped)) {
            html += `<div class="model-group">
                <div class="model-group-title">${provider}</div>`;

            for (const model of models) {
                const isSelected = this.currentModel?.provider === model.provider &&
                                   this.currentModel?.model === model.model;
                html += `
                    <div class="model-option ${isSelected ? 'selected' : ''}"
                         onclick="App.selectModel('${model.provider}', '${model.model}')">
                        <span class="model-option-name">${model.model}</span>
                        <span class="model-option-description">${model.description}</span>
                    </div>`;
            }

            html += '</div>';
        }

        this.elements.modelList.innerHTML = html || '<div class="model-option">No models found</div>';
    },

    selectModel(provider, model, save = true) {
        this.currentModel = { provider, model };

        const modelInfo = this.models.find(m => m.provider === provider && m.model === model);
        const displayName = model.split('/').pop();

        this.elements.currentModelDisplay.textContent = displayName;

        if (save) {
            Storage.saveCurrentModel(provider, model);
        }

        this.closeModelSelector();
        this.renderModelList();
    },

    toggleModelSelector() {
        this.elements.modelSelectorPopup.classList.toggle('active');
        if (this.elements.modelSelectorPopup.classList.contains('active')) {
            this.elements.modelSearchInput.focus();
        }
    },

    closeModelSelector() {
        this.elements.modelSelectorPopup.classList.remove('active');
        this.elements.modelSearchInput.value = '';
        this.renderModelList();
    },

    filterModels(query) {
        this.renderModelList(query);
    },

    // =========================================================================
    // CONVERSATIONS
    // =========================================================================

    async loadConversations() {
        const conversations = await Storage.getConversations();
        this.renderConversationList(conversations);
    },

    renderConversationList(conversations) {
        if (conversations.length === 0) {
            this.elements.conversationList.innerHTML = `
                <div style="padding: 20px; text-align: center; color: var(--text-tertiary);">
                    No conversations yet
                </div>`;
            return;
        }

        let html = '';
        for (const conv of conversations) {
            const isActive = this.currentConversation?.id === conv.id;
            html += `
                <div class="conversation-item ${isActive ? 'active' : ''}"
                     onclick="App.loadConversation('${conv.id}')">
                    <div class="conversation-icon">
                        <i data-lucide="message-square"></i>
                    </div>
                    <div class="conversation-info">
                        <div class="conversation-title">${this.escapeHtml(conv.title)}</div>
                        <div class="conversation-preview">${conv.messageCount} messages</div>
                    </div>
                    <button class="conversation-delete" onclick="event.stopPropagation(); App.deleteConversation('${conv.id}')">
                        <i data-lucide="trash-2"></i>
                    </button>
                </div>`;
        }

        this.elements.conversationList.innerHTML = html;

        if (window.lucide) lucide.createIcons();
    },

    async newConversation() {
        const conv = await Storage.createConversation('New Conversation');
        this.currentConversation = conv;

        await this.loadConversations();
        this.clearMessages();
        this.showEmptyState();
        this.closeSidebar();
        this.elements.chatInput.focus();
    },

    async loadConversation(id) {
        const conv = await Storage.getConversation(id);
        if (!conv) return;

        this.currentConversation = conv;
        await this.loadConversations();

        const messages = await Storage.getMessages(id);
        this.renderMessages(messages);

        this.closeSidebar();
    },

    async deleteConversation(id) {
        if (!confirm('Delete this conversation?')) return;

        await Storage.deleteConversation(id);

        if (this.currentConversation?.id === id) {
            this.currentConversation = null;
            this.clearMessages();
            this.showEmptyState();
        }

        await this.loadConversations();
    },

    async clearAllConversations() {
        if (!confirm('Delete all conversations? This cannot be undone.')) return;

        await Storage.deleteAllConversations();
        this.currentConversation = null;
        this.clearMessages();
        this.showEmptyState();
        await this.loadConversations();
    },

    // =========================================================================
    // MESSAGES
    // =========================================================================

    clearMessages() {
        this.elements.chatMessages.innerHTML = `
            <div class="empty-state" id="emptyState">
                <div class="empty-icon">
                    <i data-lucide="message-circle"></i>
                </div>
                <h2>Start a conversation</h2>
                <p>Select a model and enter your message below</p>
            </div>`;
        this.elements.emptyState = document.getElementById('emptyState');
        if (window.lucide) lucide.createIcons();
    },

    showEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'flex';
        }
    },

    hideEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'none';
        }
    },

    renderMessages(messages) {
        this.hideEmptyState();

        let html = '';
        for (const msg of messages) {
            html += this.createMessageHtml(msg.role, msg.content, msg.timestamp);
        }

        this.elements.chatMessages.innerHTML = html;
        if (window.lucide) lucide.createIcons();
        this.scrollToBottom();
    },

    createMessageHtml(role, content, timestamp) {
        const isUser = role === 'user';
        const avatar = isUser ? 'U' : 'AI';
        const roleLabel = isUser ? 'You' : 'Assistant';
        const time = timestamp ? new Date(timestamp).toLocaleTimeString() : '';

        // Parse markdown-like formatting
        const formattedContent = this.formatContent(content);

        return `
            <div class="message ${role}">
                <div class="message-header">
                    <div class="message-avatar">${avatar}</div>
                    <span class="message-role">${roleLabel}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-content">${formattedContent}</div>
            </div>`;
    },

    formatContent(content) {
        if (!content) return '';

        // Escape HTML first
        let formatted = this.escapeHtml(content);

        // Code blocks
        formatted = formatted.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre><code class="language-${lang || 'plaintext'}">${code.trim()}</code></pre>`;
        });

        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Bold
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

        // Italic
        formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');

        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        // Wrap in paragraphs
        formatted = `<p>${formatted}</p>`;

        return formatted;
    },

    addMessage(role, content, timestamp = null) {
        this.hideEmptyState();

        const html = this.createMessageHtml(role, content, timestamp || new Date().toISOString());
        this.elements.chatMessages.insertAdjacentHTML('beforeend', html);

        if (window.lucide) lucide.createIcons();
        this.scrollToBottom();
    },

    updateLastAssistantMessage(content) {
        const messages = this.elements.chatMessages.querySelectorAll('.message.assistant');
        const lastMessage = messages[messages.length - 1];

        if (lastMessage) {
            const contentEl = lastMessage.querySelector('.message-content');
            if (contentEl) {
                contentEl.innerHTML = this.formatContent(content);
            }
        }
    },

    addStreamingIndicator() {
        const html = `
            <div class="message assistant streaming-message">
                <div class="message-header">
                    <div class="message-avatar">AI</div>
                    <span class="message-role">Assistant</span>
                </div>
                <div class="message-content">
                    <div class="streaming-indicator">
                        <div class="streaming-dot"></div>
                        <div class="streaming-dot"></div>
                        <div class="streaming-dot"></div>
                    </div>
                </div>
            </div>`;

        this.elements.chatMessages.insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
    },

    removeStreamingIndicator() {
        const indicator = this.elements.chatMessages.querySelector('.streaming-message');
        if (indicator) {
            indicator.remove();
        }
    },

    // =========================================================================
    // SEND MESSAGE
    // =========================================================================

    async sendMessage() {
        const content = this.elements.chatInput.value.trim();
        if (!content || this.isStreaming) return;

        if (!this.currentModel) {
            alert('Please select a model first');
            return;
        }

        // Check for API key
        const apiKeys = Storage.getApiKeys();
        if (!apiKeys[this.currentModel.provider]) {
            alert(`Please add your ${this.currentModel.provider} API key in Settings`);
            this.openSettings();
            return;
        }

        // Create conversation if needed
        if (!this.currentConversation) {
            this.currentConversation = await Storage.createConversation(
                content.substring(0, 50) + (content.length > 50 ? '...' : '')
            );
            await this.loadConversations();
        } else {
            // Update title if it's still "New Conversation"
            if (this.currentConversation.title === 'New Conversation') {
                await Storage.updateConversation(this.currentConversation.id, {
                    title: content.substring(0, 50) + (content.length > 50 ? '...' : '')
                });
                await this.loadConversations();
            }
        }

        // Clear input
        this.elements.chatInput.value = '';
        this.autoResizeTextarea();

        // Add user message
        this.addMessage('user', content);
        await Storage.addMessage(this.currentConversation.id, 'user', content);

        // Build messages for API
        const messages = await Storage.getMessages(this.currentConversation.id);
        const apiMessages = messages.map(m => ({
            role: m.role,
            content: m.content
        }));

        // Start streaming
        this.isStreaming = true;
        this.elements.sendBtn.disabled = true;
        this.addStreamingIndicator();

        let fullResponse = '';

        await API.chat({
            provider: this.currentModel.provider,
            model: this.currentModel.model,
            messages: apiMessages,
            onChunk: (chunk) => {
                fullResponse += chunk;
                this.removeStreamingIndicator();

                // Check if we already have an assistant message being built
                const messages = this.elements.chatMessages.querySelectorAll('.message.assistant');
                const lastMessage = messages[messages.length - 1];

                if (lastMessage && !lastMessage.classList.contains('complete')) {
                    this.updateLastAssistantMessage(fullResponse);
                } else {
                    this.addMessage('assistant', fullResponse);
                }
            },
            onComplete: async ({ response, metadata }) => {
                this.removeStreamingIndicator();

                // Mark message as complete
                const messages = this.elements.chatMessages.querySelectorAll('.message.assistant');
                const lastMessage = messages[messages.length - 1];
                if (lastMessage) {
                    lastMessage.classList.add('complete');
                }

                // Save to storage
                await Storage.addMessage(
                    this.currentConversation.id,
                    'assistant',
                    response,
                    metadata || {}
                );

                this.isStreaming = false;
                this.elements.sendBtn.disabled = false;
            },
            onError: (error) => {
                this.removeStreamingIndicator();
                this.isStreaming = false;
                this.elements.sendBtn.disabled = false;

                alert(`Error: ${error.message}`);
                console.error('Chat error:', error);
            }
        });
    },

    // =========================================================================
    // SETTINGS
    // =========================================================================

    openSettings() {
        const keys = Storage.getApiKeys();

        document.getElementById('openaiKey').value = keys.openai || '';
        document.getElementById('anthropicKey').value = keys.anthropic || '';
        document.getElementById('googleKey').value = keys.google || '';
        document.getElementById('xaiKey').value = keys.xai || '';
        document.getElementById('deepseekKey').value = keys.deepseek || '';
        document.getElementById('groqKey').value = keys.groq || '';

        this.elements.settingsModal.classList.add('active');
    },

    closeSettings() {
        this.elements.settingsModal.classList.remove('active');
    },

    saveSettings() {
        const keys = {
            openai: document.getElementById('openaiKey').value.trim(),
            anthropic: document.getElementById('anthropicKey').value.trim(),
            google: document.getElementById('googleKey').value.trim(),
            xai: document.getElementById('xaiKey').value.trim(),
            deepseek: document.getElementById('deepseekKey').value.trim(),
            groq: document.getElementById('groqKey').value.trim()
        };

        // Filter out empty keys
        const filteredKeys = {};
        for (const [provider, key] of Object.entries(keys)) {
            if (key) filteredKeys[provider] = key;
        }

        Storage.saveApiKeys(filteredKeys);
        this.closeSettings();
    },

    // =========================================================================
    // UI HELPERS
    // =========================================================================

    autoResizeTextarea() {
        const textarea = this.elements.chatInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    },

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    },

    checkScrollPosition() {
        const { scrollTop, scrollHeight, clientHeight } = this.elements.chatMessages;
        const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

        this.elements.scrollToBottomBtn.style.display =
            distanceFromBottom > 100 ? 'flex' : 'none';
    },

    toggleSidebar() {
        this.elements.sidebar.classList.toggle('open');
        this.elements.sidebarOverlay.classList.toggle('active');
    },

    closeSidebar() {
        this.elements.sidebar.classList.remove('open');
        this.elements.sidebarOverlay.classList.remove('active');
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Global functions for onclick handlers
function toggleTheme() {
    const current = Storage.getTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    Storage.saveTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    App.updateThemeIcon(next);
}

function closeSettings() {
    App.closeSettings();
}

function saveSettings() {
    App.saveSettings();
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

window.App = App;
