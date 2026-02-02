import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { title: '聊天', icon: 'chat-o' }
  },
  {
    path: '/emotion',
    name: 'Emotion',
    component: () => import('@/views/EmotionView.vue'),
    meta: { title: '情绪', icon: 'chart-trending-o' }
  },
  {
    path: '/tools',
    name: 'Tools',
    component: () => import('@/views/ToolsView.vue'),
    meta: { title: '工具', icon: 'apps-o' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { title: '我的', icon: 'user-o' }
  },
  {
    path: '/breathing',
    name: 'Breathing',
    component: () => import('@/views/BreathingView.vue'),
    meta: { title: '呼吸练习', hideTabBar: true }
  },
  {
    path: '/crisis',
    name: 'Crisis',
    component: () => import('@/views/CrisisView.vue'),
    meta: { title: '危机干预', hideTabBar: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'Self-Agent'} - 智能情绪支持`
  next()
})

export default router
