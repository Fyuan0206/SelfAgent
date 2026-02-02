<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
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
</script>

<template>
  <div class="flex flex-col h-screen pb-14">
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
        <van-button
          icon="photo-o"
          round
          size="small"
          @click="fileInput?.click()"
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
