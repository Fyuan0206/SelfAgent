<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast, showLoadingToast, closeToast } from 'vant'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref<'login' | 'register'>('login')
const email = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')

const handleLogin = async () => {
  if (!email.value || !password.value) {
    showToast('请填写邮箱和密码')
    return
  }

  showLoadingToast({ message: '登录中...', forbidClick: true })
  try {
    await authStore.login({ email: email.value, password: password.value })
    closeToast()
    showToast('登录成功')
    router.push('/')
  } catch (error: any) {
    closeToast()
    showToast(error.response?.data?.detail || '登录失败')
  }
}

const handleRegister = async () => {
  if (!email.value || !username.value || !password.value) {
    showToast('请填写所有必填项')
    return
  }
  if (password.value !== confirmPassword.value) {
    showToast('两次密码输入不一致')
    return
  }

  showLoadingToast({ message: '注册中...', forbidClick: true })
  try {
    await authStore.register({
      email: email.value,
      username: username.value,
      password: password.value
    })
    closeToast()
    showToast('注册成功')
    router.push('/')
  } catch (error: any) {
    closeToast()
    showToast(error.response?.data?.detail || '注册失败')
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex flex-col">
    <!-- Header -->
    <div class="pt-16 pb-8 text-center">
      <div class="w-20 h-20 mx-auto rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center mb-4">
        <van-icon name="service-o" color="white" size="40" />
      </div>
      <h1 class="text-2xl font-bold text-white">Self-Agent</h1>
      <p class="text-white/80 text-sm mt-1">智能情绪支持伙伴</p>
    </div>

    <!-- Form Card -->
    <div class="flex-1 bg-white rounded-t-3xl px-6 pt-6 pb-8">
      <!-- Tabs -->
      <div class="flex mb-6 bg-gray-100 rounded-xl p-1">
        <button
          :class="[
            'flex-1 py-2.5 rounded-lg text-sm font-medium transition-all',
            activeTab === 'login' ? 'bg-white text-indigo-600 shadow' : 'text-gray-500'
          ]"
          @click="activeTab = 'login'"
        >
          登录
        </button>
        <button
          :class="[
            'flex-1 py-2.5 rounded-lg text-sm font-medium transition-all',
            activeTab === 'register' ? 'bg-white text-indigo-600 shadow' : 'text-gray-500'
          ]"
          @click="activeTab = 'register'"
        >
          注册
        </button>
      </div>

      <!-- Login Form -->
      <div v-if="activeTab === 'login'" class="space-y-4">
        <van-field
          v-model="email"
          type="email"
          label="邮箱"
          placeholder="请输入邮箱"
          :border="false"
          class="!bg-gray-50 !rounded-xl"
        />
        <van-field
          v-model="password"
          type="password"
          label="密码"
          placeholder="请输入密码"
          :border="false"
          class="!bg-gray-50 !rounded-xl"
        />
        <van-button
          type="primary"
          block
          round
          size="large"
          class="!mt-6"
          :loading="authStore.isLoading"
          @click="handleLogin"
        >
          登录
        </van-button>
      </div>

      <!-- Register Form -->
      <div v-else class="space-y-4">
        <van-field
          v-model="email"
          type="email"
          label="邮箱"
          placeholder="请输入邮箱"
          :border="false"
          class="!bg-gray-50 !rounded-xl"
        />
        <van-field
          v-model="username"
          label="用户名"
          placeholder="请输入用户名"
          :border="false"
          class="!bg-gray-50 !rounded-xl"
        />
        <van-field
          v-model="password"
          type="password"
          label="密码"
          placeholder="请输入密码"
          :border="false"
          class="!bg-gray-50 !rounded-xl"
        />
        <van-field
          v-model="confirmPassword"
          type="password"
          label="确认密码"
          placeholder="请再次输入密码"
          :border="false"
          class="!bg-gray-50 !rounded-xl"
        />
        <van-button
          type="primary"
          block
          round
          size="large"
          class="!mt-6"
          :loading="authStore.isLoading"
          @click="handleRegister"
        >
          注册
        </van-button>
      </div>

      <!-- Demo Account Hint -->
      <div class="mt-6 text-center text-sm text-gray-400">
        <p>测试账号: admin@selfagent.com / admin123</p>
      </div>
    </div>
  </div>
</template>
