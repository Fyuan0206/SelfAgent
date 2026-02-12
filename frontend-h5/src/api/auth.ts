import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Token management
const TOKEN_KEY = 'selfagent_token'
const USER_KEY = 'selfagent_user'

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export const getStoredUser = (): User | null => {
  const user = localStorage.getItem(USER_KEY)
  return user ? JSON.parse(user) : null
}

export const setStoredUser = (user: User): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

// Add auth header to requests
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Types
export interface User {
  id: number
  email: string
  username: string
  role: 'admin' | 'member' | 'user'
  is_active: boolean
  is_verified: boolean
  daily_quota?: number
  daily_used?: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  user: User
}

// API functions
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/login', data)
  setToken(response.data.access_token)
  setStoredUser(response.data.user)
  return response.data
}

export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/register', data)
  setToken(response.data.access_token)
  setStoredUser(response.data.user)
  return response.data
}

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me')
  setStoredUser(response.data)
  return response.data
}

export const logout = (): void => {
  removeToken()
}

export const isLoggedIn = (): boolean => {
  return !!getToken()
}

export const isAdmin = (): boolean => {
  const user = getStoredUser()
  return user?.role === 'admin'
}

export default api
