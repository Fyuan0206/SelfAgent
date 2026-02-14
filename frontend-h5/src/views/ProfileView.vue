<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const appStore = useAppStore()
const chatStore = useChatStore()
const authStore = useAuthStore()

const menuItems = [
  { icon: 'bell', title: '通知设置', link: true },
  { icon: 'description', title: '数据导出', link: true },
  { icon: 'shield-o', title: '隐私设置', link: true },
  { icon: 'question-o', title: '帮助与反馈', link: true },
  { icon: 'info-o', title: '关于我们', link: true },
]

const handleLogout = async () => {
  try {
    await showConfirmDialog({ title: '确认退出', message: '确定要退出登录吗？' })
    authStore.logout()
    showToast('已退出登录')
    router.push('/login')
  } catch (e) {}
}
</script>

<template>
  <div class="h-[calc(100vh-96px)] overflow-y-auto px-4 py-4">

    <!-- 用户信息卡片 -->
    <div class="glass rounded-2xl p-6 shadow-lg mb-4 text-center">
      <div class="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 flex items-center justify-center mx-auto mb-3">
        <span class="text-3xl text-white">👤</span>
      </div>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ authStore.user?.username || '用户' }}
      </h2>
      <p class="text-sm text-gray-500">{{ authStore.user?.email || chatStore.userId }}</p>
      <van-tag v-if="authStore.isAdmin" type="primary" class="mt-2">管理员</van-tag>
    </div>

    <!-- 管理员入口 -->
    <div v-if="authStore.isAdmin" class="glass rounded-2xl shadow-lg overflow-hidden mb-4">
      <van-cell
        title="管理后台"
        icon="setting-o"
        is-link
        @click="router.push('/admin')"
      />
    </div>

    <!-- 设置列表 -->
    <div class="glass rounded-2xl shadow-lg overflow-hidden mb-4">
      <van-cell-group>
        <van-cell title="深色模式" center>
          <template #right-icon>
            <van-switch
              :model-value="appStore.isDark"
              size="20"
              @update:model-value="appStore.toggleDark"
            />
          </template>
        </van-cell>
        <van-cell
          v-for="item in menuItems"
          :key="item.title"
          :title="item.title"
          :icon="item.icon"
          :is-link="item.link"
        />
      </van-cell-group>
    </div>

    <!-- 紧急求助热线 -->
    <div class="glass rounded-2xl p-4 shadow-lg bg-red-50 dark:bg-red-900/20">
      <h3 class="font-semibold text-red-700 dark:text-red-400 mb-2">
        <van-icon name="warning-o" class="mr-1" />
        紧急求助热线
      </h3>
      <a href="tel:400-161-9995" class="flex items-center justify-between p-3 bg-white dark:bg-slate-700 rounded-xl">
        <div>
          <p class="font-medium text-gray-900 dark:text-white">全国心理援助热线</p>
          <p class="text-xl font-bold text-red-600">400-161-9995</p>
        </div>
        <van-icon name="phone-o" size="24" color="#ef4444" />
      </a>
    </div>

    <!-- 版本信息 -->
    <p class="text-center text-xs text-gray-400 mt-6">
      Self-Agent H5 v1.0.0
    </p>

    <!-- 退出登录 -->
    <div class="mt-4">
      <van-button
        type="danger"
        plain
        block
        round
        @click="handleLogout"
      >
        退出登录
      </van-button>
    </div>
  </div>
</template>
