import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export interface ChatRequest {
  user_id: string
  text: string
}

export interface ChatResponse {
  response: string
  emotion?: {
    name: string
    intensity: number
  }
  risk_level?: string
  dbt_recommendation?: {
    module: string
    skills: string[]
  }
}

// 文本聊天
export const sendTextMessage = async (data: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/chat', data)
  return response.data
}

// 多模态聊天 (音频/图片)
export const sendMultimodalMessage = async (
  userId: string,
  text: string,
  file: File
): Promise<ChatResponse> => {
  const formData = new FormData()
  formData.append('user_id', userId)
  formData.append('text', text)
  formData.append('file', file)

  const response = await api.post<ChatResponse>('/chat/multimodal', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// 健康检查
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health')
  return response.data
}

export default api
