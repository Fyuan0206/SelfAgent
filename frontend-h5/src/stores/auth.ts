import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  getStoredUser,
  isLoggedIn as checkLoggedIn,
  type User,
  type LoginRequest,
  type RegisterRequest
} from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(getStoredUser())
  const isLoading = ref(false)

  const isLoggedIn = computed(() => checkLoggedIn() && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isMember = computed(() => user.value?.role === 'member' || user.value?.role === 'admin')

  const login = async (data: LoginRequest) => {
    isLoading.value = true
    try {
      const response = await apiLogin(data)
      user.value = response.user
      return response
    } finally {
      isLoading.value = false
    }
  }

  const register = async (data: RegisterRequest) => {
    isLoading.value = true
    try {
      const response = await apiRegister(data)
      user.value = response.user
      return response
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    apiLogout()
    user.value = null
  }

  const refreshUser = async () => {
    if (!checkLoggedIn()) return
    try {
      user.value = await getCurrentUser()
    } catch (e) {
      logout()
    }
  }

  return {
    user,
    isLoading,
    isLoggedIn,
    isAdmin,
    isMember,
    login,
    register,
    logout,
    refreshUser
  }
})
