import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  emotion?: string
  file?: {
    type: 'audio' | 'image'
    name: string
    url: string
  }
}

export interface EmotionData {
  name: string
  value: number
  color: string
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是你的 AI 情绪伙伴 👋\n\n我可以感知你的情绪并提供支持。你可以：\n• 分享你的感受和想法\n• 发送语音或图片表达情绪\n• 获取 DBT 技能指导',
      timestamp: new Date(),
    }
  ])

  const isLoading = ref(false)
  const currentEmotion = ref<EmotionData>({
    name: '平静',
    value: 0.7,
    color: '#22c55e'
  })

  const userId = ref('user_' + Math.random().toString(36).substr(2, 9))

  const addMessage = (message: Omit<Message, 'id' | 'timestamp'>) => {
    messages.value.push({
      ...message,
      id: Date.now().toString(),
      timestamp: new Date(),
    })
  }

  const clearMessages = () => {
    messages.value = [{
      id: '1',
      role: 'assistant',
      content: '你好！我是你的 AI 情绪伙伴 👋\n\n我可以感知你的情绪并提供支持。',
      timestamp: new Date(),
    }]
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const updateEmotion = (emotion: EmotionData) => {
    currentEmotion.value = emotion
  }

  return {
    messages,
    isLoading,
    currentEmotion,
    userId,
    addMessage,
    clearMessages,
    setLoading,
    updateEmotion,
  }
})
