<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { useAppStore } from '@/stores/app'
import { sendTextMessage, sendMultimodalMessage } from '@/api/chat'
import { showToast } from 'vant'

const router = useRouter()
const chatStore = useChatStore()
const appStore = useAppStore()

const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)

// Voice recording state
const isRecording = ref(false)
const recordingTime = ref(0)
const mediaRecorder = ref<MediaRecorder | null>(null)
const audioChunks = ref<Blob[]>([])
let recordingTimer: number | null = null

// Camera state
const isCameraOpen = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)
const cameraStream = ref<MediaStream | null>(null)
const currentEmotion = ref({ name: '分析中...', confidence: 0, videoEmotion: '', audioEmotion: '' })
const cameraAudioRecorder = ref<MediaRecorder | null>(null)
const cameraAudioChunks = ref<Blob[]>([])
let analysisInterval: number | null = null

const emotionTags = [
  { label: '😊 开心', value: '开心', color: 'bg-yellow-100 text-yellow-700' },
  { label: '😰 焦虑', value: '焦虑', color: 'bg-blue-100 text-blue-700' },
  { label: '😢 难过', value: '难过', color: 'bg-gray-100 text-gray-700' },
  { label: '😠 愤怒', value: '愤怒', color: 'bg-red-100 text-red-700' },
]

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Voice recording functions
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.value.push(e.data)
    }

    mediaRecorder.value.onstop = () => {
      stream.getTracks().forEach(track => track.stop())
      if (audioChunks.value.length > 0 && recordingTime.value >= 1) {
        const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
        const audioFile = new File([audioBlob], `voice_${Date.now()}.webm`, { type: 'audio/webm' })
        selectedFile.value = audioFile
        sendMessage()
      }
    }

    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0
    recordingTimer = window.setInterval(() => {
      recordingTime.value++
    }, 1000)
  } catch (e) {
    showToast('无法访问麦克风')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
  }
}

const cancelRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    audioChunks.value = []
    isRecording.value = false
    if (recordingTimer) {
      clearInterval(recordingTimer)
      recordingTimer = null
    }
    showToast('已取消录音')
  }
}

// Camera functions
const openCamera = async () => {
  try {
    // 同时获取视频和音频
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: 320, height: 240 },
      audio: true
    })
    cameraStream.value = stream
    isCameraOpen.value = true

    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.play()
    }

    // 设置音频录制器
    const audioTracks = stream.getAudioTracks()
    if (audioTracks.length > 0) {
      const audioStream = new MediaStream(audioTracks)
      cameraAudioRecorder.value = new MediaRecorder(audioStream)
      cameraAudioChunks.value = []

      cameraAudioRecorder.value.ondataavailable = (e) => {
        if (e.data.size > 0) {
          cameraAudioChunks.value.push(e.data)
        }
      }

      // 每2秒收集一次音频数据
      cameraAudioRecorder.value.start(2000)
    }

    // Start emotion analysis every 2 seconds
    analysisInterval = window.setInterval(analyzeFrame, 2000)
    showToast('摄像头已开启')
  } catch (e) {
    showToast('无法访问摄像头')
    console.error(e)
  }
}

const closeCamera = () => {
  // 停止音频录制
  if (cameraAudioRecorder.value && cameraAudioRecorder.value.state !== 'inactive') {
    cameraAudioRecorder.value.stop()
    cameraAudioRecorder.value = null
  }
  cameraAudioChunks.value = []

  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach(track => track.stop())
    cameraStream.value = null
  }
  if (analysisInterval) {
    clearInterval(analysisInterval)
    analysisInterval = null
  }
  isCameraOpen.value = false
  currentEmotion.value = { name: '分析中...', confidence: 0, videoEmotion: '', audioEmotion: '' }
}

const toggleCamera = () => {
  if (isCameraOpen.value) {
    closeCamera()
  } else {
    openCamera()
  }
}

const analyzeFrame = async () => {
  if (!videoRef.value || !cameraStream.value) return

  try {
    // 获取视频帧
    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth || 320
    canvas.height = videoRef.value.videoHeight || 240
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(videoRef.value, 0, 0)
    }

    const videoBlob = await new Promise<Blob | null>(resolve => {
      canvas.toBlob(resolve, 'image/jpeg', 0.8)
    })

    // 获取音频数据
    let audioBlob: Blob | null = null
    if (cameraAudioChunks.value.length > 0) {
      audioBlob = new Blob(cameraAudioChunks.value, { type: 'audio/webm' })
      cameraAudioChunks.value = [] // 清空已处理的音频
    }

    let videoResult: any = null
    let audioResult: any = null

    if (videoBlob) {
      // 发送视频帧分析
      const videoFile = new File([videoBlob], 'frame.jpg', { type: 'image/jpeg' })
      videoResult = await sendMultimodalMessage(chatStore.userId, '(实时视频分析)', videoFile)
    }

    // 发送音频分析（如果有音频数据）
    if (audioBlob && audioBlob.size > 0) {
      const audioFile = new File([audioBlob], 'audio.webm', { type: 'audio/webm' })
      audioResult = await sendMultimodalMessage(chatStore.userId, '(实时音频分析)', audioFile)
    }

    // 解析后端返回的情绪数据
    const videoEmotion = videoResult?.emotion?.name || '未知'
    const videoConf = videoResult?.emotion?.confidence || 0
    const audioEmotion = audioResult?.emotion?.name || '无音频'
    const audioConf = audioResult?.emotion?.confidence || 0

    // 综合情绪（取置信度较高的）
    let finalEmotion: string
    let finalConf: number
    if (audioConf > videoConf && audioResult) {
      finalEmotion = audioEmotion
      finalConf = audioConf
    } else {
      finalEmotion = videoEmotion
      finalConf = videoConf
    }

    currentEmotion.value = {
      name: finalEmotion,
      confidence: finalConf,
      videoEmotion: `${videoEmotion} ${videoConf.toFixed(0)}%`,
      audioEmotion: audioResult ? `${audioEmotion} ${audioConf.toFixed(0)}%` : '无音频'
    }
  } catch (e) {
    console.error('Analysis failed:', e)
  }
}

const sendMessage = async () => {
  const text = messageInput.value.trim()
  if (!text && !selectedFile.value) return

  // 添加用户消息
  chatStore.addMessage({
    role: 'user',
    content: text || '(发送了文件)',
    file: selectedFile.value ? {
      type: selectedFile.value.type.startsWith('audio') ? 'audio' : 'image',
      name: selectedFile.value.name,
      url: URL.createObjectURL(selectedFile.value)
    } : undefined
  })

  messageInput.value = ''
  chatStore.setLoading(true)
  scrollToBottom()

  try {
    let response
    if (selectedFile.value) {
      response = await sendMultimodalMessage(
        chatStore.userId,
        text,
        selectedFile.value
      )
    } else {
      response = await sendTextMessage({
        user_id: chatStore.userId,
        text: text
      })
    }

    chatStore.addMessage({
      role: 'assistant',
      content: response.response,
      emotion: response.emotion?.name
    })

    if (response.emotion) {
      chatStore.updateEmotion({
        name: response.emotion.name,
        value: response.emotion.intensity,
        color: getEmotionColor(response.emotion.name)
      })
    }
  } catch (error) {
    showToast('发送失败，请重试')
    console.error(error)
  } finally {
    chatStore.setLoading(false)
    selectedFile.value = null
    scrollToBottom()
  }
}

const quickEmotion = (emotion: string) => {
  messageInput.value = `我现在感觉${emotion}`
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    showToast(`已选择: ${target.files[0].name}`)
  }
}

const getEmotionColor = (emotion: string): string => {
  const colors: Record<string, string> = {
    '开心': '#22c55e',
    '平静': '#22c55e',
    '焦虑': '#3b82f6',
    '难过': '#6b7280',
    '愤怒': '#ef4444',
    '恐惧': '#8b5cf6',
  }
  return colors[emotion] || '#6366f1'
}

const formatTime = (date: Date) => {
  return new Date(date).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  scrollToBottom()
})

onUnmounted(() => {
  if (recordingTimer) clearInterval(recordingTimer)
  if (analysisInterval) clearInterval(analysisInterval)
  closeCamera()
})
</script>

<template>
  <div class="flex flex-col h-screen pb-14">
    <!-- 摄像头悬浮窗 -->
    <div
      v-if="isCameraOpen"
      class="fixed top-16 right-2 z-40 bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden"
      style="width: 160px;"
    >
      <div class="flex items-center justify-between px-2 py-1 bg-indigo-500 text-white text-xs">
        <span>实时情绪分析</span>
        <van-icon name="cross" size="14" @click="closeCamera" />
      </div>
      <video
        ref="videoRef"
        class="w-full h-24 object-cover bg-black"
        autoplay
        playsinline
        muted
      ></video>
      <div class="p-2 text-xs">
        <div class="flex items-center justify-between mb-1">
          <span class="text-gray-600 dark:text-gray-400">综合:</span>
          <span class="font-medium text-indigo-600">{{ currentEmotion.name }} {{ currentEmotion.confidence }}%</span>
        </div>
        <div class="w-full bg-gray-200 dark:bg-slate-600 rounded-full h-1.5 mb-1">
          <div
            class="bg-indigo-500 h-1.5 rounded-full transition-all"
            :style="{ width: `${currentEmotion.confidence}%` }"
          ></div>
        </div>
        <div class="text-gray-400 text-[10px]">
          <div>视频: {{ currentEmotion.videoEmotion || '-' }}</div>
          <div>音频: {{ currentEmotion.audioEmotion || '-' }}</div>
        </div>
      </div>
    </div>

    <!-- 顶部栏 -->
    <div class="glass border-b border-gray-200/50 px-4 py-3 safe-area-top">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-full gradient-bg flex items-center justify-center shadow">
            <van-icon name="service-o" color="white" size="20" />
          </div>
          <div>
            <h1 class="text-base font-semibold text-gray-900 dark:text-white">Self-Agent</h1>
            <p class="text-xs text-gray-500">在线 · 随时为您提供支持</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <van-button
            size="small"
            type="danger"
            round
            class="crisis-pulse"
            @click="router.push('/crisis')"
          >
            <van-icon name="warning-o" />
            紧急
          </van-button>
        </div>
      </div>
    </div>

    <!-- 消息区域 -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto px-4 py-4 space-y-4"
    >
      <div
        v-for="message in chatStore.messages"
        :key="message.id"
        class="message-enter"
        :class="message.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
      >
        <!-- AI 消息 -->
        <div v-if="message.role === 'assistant'" class="flex items-start gap-2 max-w-[85%]">
          <div class="w-8 h-8 rounded-full gradient-bg flex items-center justify-center flex-shrink-0">
            <van-icon name="service-o" color="white" size="16" />
          </div>
          <div>
            <div class="bg-white dark:bg-slate-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
              <p class="text-gray-800 dark:text-gray-100 text-sm whitespace-pre-wrap">{{ message.content }}</p>
            </div>
            <span class="text-xs text-gray-400 mt-1 ml-2">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>

        <!-- 用户消息 -->
        <div v-else class="flex items-start gap-2 max-w-[85%] flex-row-reverse">
          <div class="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center flex-shrink-0">
            <van-icon name="user-o" color="white" size="16" />
          </div>
          <div class="text-right">
            <div class="bg-primary-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm">
              <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
              <div v-if="message.file" class="mt-2 text-xs opacity-80">
                📎 {{ message.file.name }}
              </div>
            </div>
            <span class="text-xs text-gray-400 mt-1 mr-2">{{ formatTime(message.timestamp) }}</span>
          </div>
        </div>
      </div>

      <!-- 加载指示器 -->
      <div v-if="chatStore.isLoading" class="flex items-start gap-2">
        <div class="w-8 h-8 rounded-full gradient-bg flex items-center justify-center">
          <van-icon name="service-o" color="white" size="16" />
        </div>
        <div class="bg-white dark:bg-slate-700 rounded-2xl px-4 py-3 shadow-sm">
          <div class="flex gap-1">
            <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
            <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
            <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="glass border-t border-gray-200/50 px-4 py-3">
      <!-- 录音状态覆盖层 -->
      <div
        v-if="isRecording"
        class="fixed inset-0 bg-black/60 z-50 flex flex-col items-center justify-center"
        @touchmove.prevent
      >
        <div class="w-24 h-24 rounded-full bg-red-500 flex items-center justify-center mb-4 animate-pulse">
          <van-icon name="audio" color="white" size="40" />
        </div>
        <p class="text-white text-lg mb-2">正在录音... {{ recordingTime }}s</p>
        <p class="text-white/60 text-sm">松开发送，上滑取消</p>
      </div>

      <!-- 情绪快捷标签 -->
      <div class="flex gap-2 mb-3 overflow-x-auto pb-1">
        <button
          v-for="tag in emotionTags"
          :key="tag.value"
          :class="['flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium', tag.color]"
          @click="quickEmotion(tag.value)"
        >
          {{ tag.label }}
        </button>
      </div>

      <!-- 输入控件 -->
      <div class="flex items-end gap-2">
        <input
          ref="fileInput"
          type="file"
          accept="audio/*,image/*"
          class="hidden"
          @change="handleFileSelect"
        />
        <!-- 语音按钮 -->
        <van-button
          icon="audio"
          round
          size="small"
          :type="isRecording ? 'danger' : 'default'"
          @touchstart.prevent="startRecording"
          @touchend.prevent="stopRecording"
          @mousedown.prevent="startRecording"
          @mouseup.prevent="stopRecording"
          @mouseleave="isRecording && cancelRecording()"
        />
        <!-- 图片按钮 -->
        <van-button
          icon="photo-o"
          round
          size="small"
          @click="fileInput?.click()"
        />
        <!-- 摄像头按钮 -->
        <van-button
          icon="video-o"
          round
          size="small"
          :type="isCameraOpen ? 'success' : 'default'"
          @click="toggleCamera"
        />
        <van-field
          v-model="messageInput"
          type="textarea"
          rows="1"
          autosize
          placeholder="说说你的感受..."
          class="flex-1 !bg-gray-100 dark:!bg-slate-700 !rounded-xl"
          @keydown.enter.exact.prevent="sendMessage"
        />
        <van-button
          type="primary"
          icon="guide-o"
          round
          size="small"
          :loading="chatStore.isLoading"
          @click="sendMessage"
        />
      </div>

      <!-- 文件预览 -->
      <div v-if="selectedFile" class="mt-2 p-2 bg-gray-100 dark:bg-slate-700 rounded-lg flex items-center justify-between">
        <span class="text-sm text-gray-600 dark:text-gray-300 truncate">
          📎 {{ selectedFile.name }}
        </span>
        <van-button size="mini" @click="selectedFile = null">取消</van-button>
      </div>
    </div>
  </div>
</template>
