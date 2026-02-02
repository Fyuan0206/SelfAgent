// =====================================================
// Self-Agent Frontend Application
// 连接到后端 SelfAgent (CAMEL-AI)
// =====================================================

// API 配置
const API_BASE_URL = window.location.origin; // 自动使用当前域名
const API_ENDPOINT = `${API_BASE_URL}/api/chat`;
const API_MULTIMODAL_ENDPOINT = `${API_BASE_URL}/api/chat/multimodal`;

// 用户ID (可以存储在 localStorage)
const USER_ID = localStorage.getItem('selfagent_user_id') || 'user_web_' + Date.now();
localStorage.setItem('selfagent_user_id', USER_ID);

// Global state
const state = {
    messages: [],
    currentEmotion: null,
    isBreathing: false,
    uploadedFile: null,
    darkMode: false,
    isProcessing: false
};

// =====================================================
// Initialization
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize dark mode
    if (localStorage.getItem('darkMode') === 'true' ||
        (!localStorage.getItem('darkMode') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        state.darkMode = true;
        document.documentElement.classList.add('dark');
    }

    // Initialize emotion chart
    initEmotionChart();

    // Focus on input
    document.getElementById('message-input').focus();

    // Check API health
    checkAPIHealth();
});

// =====================================================
// API Communication
// =====================================================

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        console.log('API Health Check:', data);

        if (!data.agent_initialized) {
            showWarning('Agent 尚未初始化，请检查 .env 配置');
        }
    } catch (error) {
        console.error('API Health check failed:', error);
        showError('无法连接到服务器，请确保后端已启动');
    }
}

async function sendMessageToBackend(message, file = null) {
    try {
        state.isProcessing = true;

        let response;

        if (file) {
            // 多模态请求
            const formData = new FormData();
            formData.append('user_id', USER_ID);
            formData.append('text', message || '');
            formData.append('file', file);

            response = await fetch(API_MULTIMODAL_ENDPOINT, {
                method: 'POST',
                body: formData
            });
        } else {
            // 普通文本请求
            response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: USER_ID,
                    text: message
                })
            });
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.success) {
            // 隐藏打字指示器
            hideTypingIndicator();

            // 添加 AI 响应到界面
            addMessageToUI('assistant', data.response);

            // 更新情绪状态（如果响应中包含情绪信息）
            // TODO: 从响应中解析情绪信息并更新界面
        } else {
            throw new Error(data.response || '请求失败');
        }

    } catch (error) {
        hideTypingIndicator();
        console.error('Error sending message:', error);

        // 显示错误消息
        const errorMsg = `抱歉，发生了错误：${error.message}`;
        addMessageToUI('assistant', errorMsg);
        showError(errorMsg);

    } finally {
        state.isProcessing = false;
    }
}

// =====================================================
// Chat Functions
// =====================================================

function sendMessage() {
    if (state.isProcessing) {
        showWarning('请等待当前消息处理完成');
        return;
    }

    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message && !state.uploadedFile) return;

    // 添加用户消息到 UI
    addMessageToUI('user', message, state.uploadedFile);

    // 清空输入
    input.value = '';
    input.style.height = 'auto';
    const fileToUpload = state.uploadedFile;
    clearFile();

    // 显示打字指示器
    showTypingIndicator();

    // 发送到后端
    sendMessageToBackend(message, fileToUpload);
}

function addMessageToUI(type, content, file = null) {
    const container = document.getElementById('messages-container');
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start gap-3 message-enter ${type === 'user' ? 'flex-row-reverse' : ''}`;

    const time = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });

    if (type === 'user') {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center flex-shrink-0 shadow">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
            </div>
            <div class="flex-1">
                <div class="bg-gradient-to-br from-indigo-500 to-pink-500 rounded-2xl rounded-tr-sm p-4 shadow-sm text-white max-w-[80%] ml-auto">
                    ${content ? `<p class="whitespace-pre-wrap">${escapeHtml(content)}</p>` : ''}
                    ${file ? `<div class="mt-2 flex items-center gap-2 bg-white/20 rounded-lg p-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
                        </svg>
                        <span class="text-xs">${file.name}</span>
                    </div>` : ''}
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 mr-2 block text-right">${time}</span>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center flex-shrink-0 shadow">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
            </div>
            <div class="flex-1">
                <div class="bg-white dark:bg-slate-700 rounded-2xl rounded-tl-sm p-4 shadow-sm max-w-[80%]">
                    ${content ? `<p class="text-gray-800 dark:text-gray-100 whitespace-pre-wrap">${escapeHtml(content)}</p>` : ''}
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-2">${time}</span>
            </div>
        `;
    }

    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;

    // Store in state
    state.messages.push({ type, content, file, time });
}

function showTypingIndicator() {
    const container = document.getElementById('messages-container');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'flex items-start gap-3 message-enter';
    typingDiv.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center flex-shrink-0 shadow">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
            </svg>
        </div>
        <div class="bg-white dark:bg-slate-700 rounded-2xl rounded-tl-sm p-4 shadow-sm">
            <div class="flex gap-1">
                <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-dot"></div>
                <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-dot"></div>
                <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-dot"></div>
            </div>
        </div>
    `;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function clearChat() {
    if (!confirm('确定要清空聊天记录吗？')) return;

    const container = document.getElementById('messages-container');
    container.innerHTML = `
        <div class="flex items-start gap-3 message-enter">
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center flex-shrink-0 shadow">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
            </div>
            <div class="flex-1">
                <div class="bg-white dark:bg-slate-700 rounded-2xl rounded-tl-sm p-4 shadow-sm">
                    <p class="text-gray-800 dark:text-gray-100">聊天记录已清空。我们重新开始吧！</p>
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400 mt-1 ml-2">刚刚</span>
            </div>
        </div>
    `;
    state.messages = [];
}

// =====================================================
// Dark Mode Toggle
// =====================================================

function toggleDarkMode() {
    state.darkMode = !state.darkMode;
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', state.darkMode);
    updateChartColors();
}

// =====================================================
// Emotion Functions
// =====================================================

function quickEmotion(emotion) {
    const input = document.getElementById('message-input');
    const messages = {
        '开心': '我今天感觉很开心！',
        '焦虑': '我最近感到很焦虑，有点担心。',
        '难过': '我今天心情不太好，有点难过。',
        '愤怒': '我现在很生气，有些事情让我很不满。',
        '疲惫': '我感觉很疲惫，很累，没有精神。'
    };
    input.value = messages[emotion] || emotion;
    input.focus();
}

// =====================================================
// File Upload
// =====================================================

function handleAudioUpload(event) {
    const file = event.target.files[0];
    if (file) {
        state.uploadedFile = file;
        showFilePreview(file);
    }
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        state.uploadedFile = file;
        showFilePreview(file);
    }
}

function showFilePreview(file) {
    const preview = document.getElementById('file-preview');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');

    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    preview.classList.remove('hidden');
}

function clearFile() {
    state.uploadedFile = null;
    document.getElementById('audio-input').value = '';
    document.getElementById('image-input').value = '';
    document.getElementById('file-preview').classList.add('hidden');
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// =====================================================
// Breathing Exercise
// =====================================================

function startBreathing() {
    if (state.isBreathing) return;

    state.isBreathing = true;
    const circle = document.getElementById('breathing-circle');
    const text = document.getElementById('breathing-text');

    const cycle = async () => {
        text.textContent = '吸气';
        circle.style.transition = 'transform 4s ease-in-out';
        circle.style.transform = 'scale(1.5)';
        await sleep(4000);

        text.textContent = '保持';
        await sleep(2000);

        text.textContent = '呼气';
        circle.style.transform = 'scale(1)';
        await sleep(4000);

        text.textContent = '保持';
        await sleep(2000);

        if (state.isBreathing) {
            cycle();
        } else {
            text.textContent = '完成';
            circle.style.transform = 'scale(1)';
        }
    };

    cycle();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// =====================================================
// Modal Functions
// =====================================================

function showCrisisModal() {
    document.getElementById('crisis-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function hideCrisisModal() {
    document.getElementById('crisis-modal').classList.add('hidden');
    document.body.style.overflow = '';
}

function showModal(type) {
    if (type === 'breathing') {
        document.getElementById('breathing-modal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(type) {
    if (type === 'breathing') {
        state.isBreathing = false;
        document.getElementById('breathing-modal').classList.add('hidden');
        document.body.style.overflow = '';
    }
}

// =====================================================
// Emotion Chart
// =====================================================

function initEmotionChart() {
    const ctx = document.getElementById('emotionChart');
    if (!ctx) return;

    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 160);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

    window.emotionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            datasets: [{
                label: '情绪指数',
                data: [65, 72, 68, 75, 70, 82, 78],
                borderColor: '#6366f1',
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: state.darkMode ? '#94a3b8' : '#64748b',
                        font: { size: 10 }
                    }
                },
                y: {
                    display: false,
                    min: 0,
                    max: 100
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function updateChartColors() {
    if (!window.emotionChart) return;

    const isDark = state.darkMode;
    const textColor = isDark ? '#94a3b8' : '#64748b';

    window.emotionChart.options.scales.x.ticks.color = textColor;
    window.emotionChart.update();
}

// =====================================================
// Utility Functions
// =====================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

// =====================================================
// Notification System
// =====================================================

function showWarning(message) {
    console.warn('Warning:', message);
    // TODO: Show toast notification
}

function showError(message) {
    console.error('Error:', message);
    // TODO: Show toast notification
}

function showSuccess(message) {
    console.log('Success:', message);
    // TODO: Show toast notification
}
