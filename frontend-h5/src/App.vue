<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from './stores/app'

const route = useRoute()
const appStore = useAppStore()

const showTabBar = computed(() => !route.meta.hideTabBar)

onMounted(() => {
  appStore.initDarkMode()
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-pink-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
    <router-view />

    <!-- 底部导航栏 -->
    <van-tabbar v-if="showTabBar" route class="safe-area-bottom">
      <van-tabbar-item to="/" icon="chat-o">聊天</van-tabbar-item>
      <van-tabbar-item to="/emotion" icon="chart-trending-o">情绪</van-tabbar-item>
      <van-tabbar-item to="/tools" icon="apps-o">工具</van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
:deep(.van-tabbar) {
  --van-tabbar-item-active-color: #6366f1;
}
</style>
