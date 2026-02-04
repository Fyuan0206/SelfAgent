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

    // Check if user is admin and show admin entry
    checkAdminAccess();

    // Update user info display
    updateUserDisplay();

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const container = document.getElementById('user-menu-container');
        if (container && !container.contains(e.target)) {
            document.getElementById('user-dropdown')?.classList.add('hidden');
        }
    });
});

// =====================================================
// API Communication
// =====================================================

// Check if current user is admin and show admin entry button
async function checkAdminAccess() {
    // First check locally stored user info
    if (typeof Auth !== 'undefined' && Auth.isAdmin()) {
        showAdminEntry();
        return;
    }

    // If not found locally, try to fetch from API
    const token = localStorage.getItem('selfagent_token');
    if (!token) {
        console.log('No token found, admin entry hidden');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const user = await response.json();
            console.log('User info:', user);
            // Show admin entry if user is admin
            if (user.role === 'admin') {
                showAdminEntry();
            }
        }
    } catch (error) {
        console.log('Admin check failed:', error);
    }
}

function showAdminEntry() {
    const adminEntry = document.getElementById('admin-entry');
    if (adminEntry) {
        adminEntry.classList.remove('hidden');
        adminEntry.classList.add('flex');
        console.log('Admin entry shown');
    }
}

// =====================================================
// User Menu Functions
// =====================================================

function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

function updateUserDisplay() {
    // Get user info from localStorage
    const userStr = localStorage.getItem('selfagent_user');
    if (!userStr) return;

    try {
        const user = JSON.parse(userStr);

        // Update avatar letter
        const avatarLetter = document.getElementById('user-avatar-letter');
        if (avatarLetter && user.username) {
            avatarLetter.textContent = user.username.charAt(0).toUpperCase();
        }

        // Update display name
        const displayName = document.getElementById('user-display-name');
        if (displayName) {
            displayName.textContent = user.username || '用户';
        }

        // Update email
        const displayEmail = document.getElementById('user-display-email');
        if (displayEmail) {
            displayEmail.textContent = user.email || '';
        }
    } catch (e) {
        console.log('Failed to parse user info:', e);
    }
}

function logout() {
    // Clear stored credentials
    localStorage.removeItem('selfagent_token');
    localStorage.removeItem('selfagent_user');

    // Redirect to login page
    window.location.href = 'login.html';
}

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
// Voice Recording (Press to Talk)
// =====================================================

let mediaRecorder = null;
let audioChunks = [];
let recordingStartTime = null;
let recordingTimer = null;
let isRecordingCancelled = false;
let touchStartY = null;
let shouldCancelOnSwipe = false;
const SWIPE_CANCEL_THRESHOLD = 80; // pixels to swipe up to cancel

async function startRecording(event) {
    // Prevent default to avoid text selection on long press
    if (event) {
        event.preventDefault();
    }

    // Track touch start position for swipe detection
    if (event && event.touches && event.touches.length > 0) {
        touchStartY = event.touches[0].clientY;
        shouldCancelOnSwipe = false;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        isRecordingCancelled = false;

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            stream.getTracks().forEach(track => track.stop());

            if (!isRecordingCancelled && audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioFile = new File([audioBlob], `recording_${Date.now()}.webm`, { type: 'audio/webm' });
                state.uploadedFile = audioFile;
                showFilePreview(audioFile);
                sendMessage(); // Auto send after recording
            }
        };

        mediaRecorder.start();
        recordingStartTime = Date.now();

        // Show recording overlay
        const overlay = document.getElementById('recording-overlay');
        overlay.classList.remove('hidden');
        document.getElementById('voice-btn').classList.add('bg-red-500');
        updateRecordingOverlayState(false); // Normal state

        // Update timer
        recordingTimer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
            const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const secs = (elapsed % 60).toString().padStart(2, '0');
            document.getElementById('recording-time').textContent = `${mins}:${secs}`;
        }, 100);

    } catch (error) {
        console.error('Failed to start recording:', error);
        showError('无法访问麦克风，请检查权限设置');
    }
}

function handleRecordingTouchMove(event) {
    if (!mediaRecorder || mediaRecorder.state !== 'recording' || touchStartY === null) {
        return;
    }

    const currentY = event.touches[0].clientY;
    const deltaY = touchStartY - currentY; // Positive = swiped up

    if (deltaY > SWIPE_CANCEL_THRESHOLD) {
        shouldCancelOnSwipe = true;
        updateRecordingOverlayState(true); // Cancel state
    } else {
        shouldCancelOnSwipe = false;
        updateRecordingOverlayState(false); // Normal state
    }
}

function updateRecordingOverlayState(isCancelState) {
    const recordingIcon = document.getElementById('recording-icon');
    const statusText = document.getElementById('recording-status');

    if (isCancelState) {
        // Cancel state - show cancel UI
        if (recordingIcon) {
            recordingIcon.classList.remove('bg-red-500');
            recordingIcon.classList.add('bg-gray-500');
        }
        if (statusText) {
            statusText.textContent = '松开取消发送';
            statusText.classList.add('text-red-500');
            statusText.classList.remove('text-gray-500', 'dark:text-gray-400');
        }
    } else {
        // Normal state - show send UI
        if (recordingIcon) {
            recordingIcon.classList.remove('bg-gray-500');
            recordingIcon.classList.add('bg-red-500');
        }
        if (statusText) {
            statusText.textContent = '松开发送 | 按 ESC 取消';
            statusText.classList.remove('text-red-500');
            statusText.classList.add('text-gray-500', 'dark:text-gray-400');
        }
    }
}

function stopRecording(event) {
    if (event) {
        event.preventDefault();
    }

    if (mediaRecorder && mediaRecorder.state === 'recording') {
        // Check if we should cancel due to swipe
        if (shouldCancelOnSwipe) {
            cancelRecording();
            return;
        }

        clearInterval(recordingTimer);
        document.getElementById('recording-overlay').classList.add('hidden');
        document.getElementById('voice-btn').classList.remove('bg-red-500');
        mediaRecorder.stop();
    }

    // Reset touch tracking
    touchStartY = null;
    shouldCancelOnSwipe = false;
}

function cancelRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        isRecordingCancelled = true;
        clearInterval(recordingTimer);
        document.getElementById('recording-overlay').classList.add('hidden');
        document.getElementById('voice-btn').classList.remove('bg-red-500');
        mediaRecorder.stop();
        showError('录音已取消');
    }

    // Reset touch tracking
    touchStartY = null;
    shouldCancelOnSwipe = false;
}

// Handle ESC key to cancel recording
function handleRecordingKeydown(event) {
    if (event.key === 'Escape' && mediaRecorder && mediaRecorder.state === 'recording') {
        cancelRecording();
    }
}

// Handle click on overlay background to cancel recording
function handleOverlayClick(event) {
    // Only cancel if clicking on the overlay background, not the content
    if (event.target.id === 'recording-overlay') {
        cancelRecording();
    }
}

// Handle global mouseup/touchend to stop recording (since overlay covers the button)
function handleGlobalMouseUp(event) {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        stopRecording(event);
    }
}

// Initialize recording event listeners
document.addEventListener('DOMContentLoaded', function() {
    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        // Add touch move listener to the whole document during recording
        document.addEventListener('touchmove', handleRecordingTouchMove, { passive: true });
    }

    // Add ESC key listener
    document.addEventListener('keydown', handleRecordingKeydown);

    // Add global mouseup/touchend listener (for when overlay covers the button)
    document.addEventListener('mouseup', handleGlobalMouseUp);
    document.addEventListener('touchend', handleGlobalMouseUp);

    // Note: We removed the overlay click-to-cancel since mouseup now handles it
});

// =====================================================
// Camera / Video Analysis
// =====================================================

let cameraStream = null;
let cameraAnalysisInterval = null;
let cameraAudioRecorder = null;
let cameraAudioChunks = [];

async function toggleCamera() {
    if (cameraStream) {
        closeCamera();
    } else {
        await openCamera();
    }
}

async function openCamera() {
    try {
        // 同时获取视频和音频
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'user', width: 320, height: 240 },
            audio: true
        });

        const video = document.getElementById('camera-video');
        video.srcObject = cameraStream;

        // 设置音频录制器
        const audioTracks = cameraStream.getAudioTracks();
        if (audioTracks.length > 0) {
            const audioStream = new MediaStream(audioTracks);
            cameraAudioRecorder = new MediaRecorder(audioStream);
            cameraAudioChunks = [];

            cameraAudioRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    cameraAudioChunks.push(e.data);
                }
            };

            // 每2秒收集一次音频数据
            cameraAudioRecorder.start(2000);
        }

        // Show camera window and indicator
        document.getElementById('camera-window').classList.remove('hidden');
        document.getElementById('camera-indicator').classList.remove('hidden');

        // Make camera window draggable
        makeDraggable(document.getElementById('camera-window'), document.getElementById('camera-header'));

        // Start emotion analysis every 2 seconds
        cameraAnalysisInterval = setInterval(analyzeFrame, 2000);

    } catch (error) {
        console.error('Failed to open camera:', error);
        showError('无法访问摄像头，请检查权限设置');
    }
}

function closeCamera() {
    if (cameraAudioRecorder && cameraAudioRecorder.state !== 'inactive') {
        cameraAudioRecorder.stop();
        cameraAudioRecorder = null;
    }
    cameraAudioChunks = [];

    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    if (cameraAnalysisInterval) {
        clearInterval(cameraAnalysisInterval);
        cameraAnalysisInterval = null;
    }

    document.getElementById('camera-window').classList.add('hidden');
    document.getElementById('camera-indicator').classList.add('hidden');
    document.getElementById('camera-video').srcObject = null;
}

async function analyzeFrame() {
    if (!cameraStream) return;

    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth || 320;
    canvas.height = video.videoHeight || 240;
    ctx.drawImage(video, 0, 0);

    // 获取视频帧
    const videoBlob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
    if (!videoBlob) return;

    // 获取音频数据
    let audioBlob = null;
    if (cameraAudioChunks.length > 0) {
        audioBlob = new Blob(cameraAudioChunks, { type: 'audio/webm' });
        cameraAudioChunks = []; // 清空已处理的音频
    }

    try {
        // 发送视频帧分析
        const videoFormData = new FormData();
        videoFormData.append('user_id', USER_ID);
        videoFormData.append('text', '[实时视频分析]');
        videoFormData.append('file', videoBlob, 'frame.jpg');

        const videoResponse = await fetch(API_MULTIMODAL_ENDPOINT, {
            method: 'POST',
            body: videoFormData
        });

        let videoResult = null;
        if (videoResponse.ok) {
            videoResult = await videoResponse.json();
        }

        // 发送音频分析（如果有音频数据）
        let audioResult = null;
        if (audioBlob && audioBlob.size > 0) {
            const audioFormData = new FormData();
            audioFormData.append('user_id', USER_ID);
            audioFormData.append('text', '[实时音频分析]');
            audioFormData.append('file', audioBlob, 'audio.webm');

            const audioResponse = await fetch(API_MULTIMODAL_ENDPOINT, {
                method: 'POST',
                body: audioFormData
            });
            if (audioResponse.ok) {
                audioResult = await audioResponse.json();
            }
        }

        // 解析后端返回的情绪数据
        const videoEmotion = videoResult?.emotion?.name || '未知';
        const videoConf = videoResult?.emotion?.confidence || 0;
        const audioEmotion = audioResult?.emotion?.name || '无音频';
        const audioConf = audioResult?.emotion?.confidence || 0;

        // 综合情绪（取置信度较高的）
        let finalEmotion, finalConf;
        if (audioConf > videoConf && audioResult) {
            finalEmotion = audioEmotion;
            finalConf = audioConf;
        } else {
            finalEmotion = videoEmotion;
            finalConf = videoConf;
        }

        const arousal = videoResult?.emotion?.arousal || audioResult?.emotion?.arousal || 0;

        // 更新 UI
        document.getElementById('camera-emotion').textContent = finalEmotion;
        document.getElementById('camera-confidence').style.width = `${finalConf}%`;
        document.getElementById('camera-conf-text').textContent = `${finalConf.toFixed(0)}%`;
        document.getElementById('camera-arousal').textContent = arousal.toFixed(2);

        // 更新视频/音频分别显示
        const videoText = document.getElementById('camera-video-emotion');
        const audioText = document.getElementById('camera-audio-emotion');
        if (videoText) videoText.textContent = `${videoEmotion} ${videoConf.toFixed(0)}%`;
        if (audioText) audioText.textContent = audioResult ? `${audioEmotion} ${audioConf.toFixed(0)}%` : '无音频';

    } catch (error) {
        console.error('Frame analysis failed:', error);
    }
}

// Make element draggable
function makeDraggable(element, handle) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    handle.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
        element.style.right = "auto";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
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
