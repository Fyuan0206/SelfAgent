<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const hotlines = [
  {
    name: '全国心理援助热线',
    number: '400-161-9995',
    desc: '24小时服务',
    primary: true,
  },
  {
    name: '北京危机干预热线',
    number: '010-82951332',
    desc: '24小时服务',
    primary: false,
  },
  {
    name: '希望24热线',
    number: '400-161-9995',
    desc: '全国服务',
    primary: false,
  },
]

const reminders = [
  '您不是一个人',
  '这种感觉会过去',
  '请给自己一个机会',
  '专业帮助可以带来改变',
]
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-red-50 via-white to-pink-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex flex-col">
    <!-- 顶部栏 -->
    <div class="flex items-center justify-between px-4 py-3 safe-area-top">
      <van-icon name="cross" size="24" @click="router.back()" />
      <h1 class="text-lg font-semibold text-gray-900 dark:text-white">危机干预支持</h1>
      <div class="w-6"></div>
    </div>

    <!-- 主内容 -->
    <div class="flex-1 px-4 py-6">
      <!-- 警示图标 -->
      <div class="text-center mb-6">
        <div class="w-20 h-20 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mx-auto mb-4">
          <van-icon name="warning-o" size="40" color="#ef4444" />
        </div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-2">我们非常关心您的安全</h2>
        <p class="text-gray-600 dark:text-gray-400">请立即寻求专业帮助</p>
      </div>

      <!-- 热线列表 -->
      <div class="space-y-3 mb-6">
        <a
          v-for="hotline in hotlines"
          :key="hotline.number"
          :href="`tel:${hotline.number}`"
          :class="[
            'block p-4 rounded-2xl transition-transform active:scale-98',
            hotline.primary
              ? 'bg-red-500 text-white shadow-lg'
              : 'glass border border-gray-200 dark:border-gray-700'
          ]"
        >
          <div class="flex items-center justify-between">
            <div>
              <p :class="['font-semibold', hotline.primary ? 'text-white' : 'text-gray-900 dark:text-white']">
                {{ hotline.name }}
              </p>
              <p :class="['text-2xl font-bold mt-1', hotline.primary ? 'text-white' : 'text-red-600']">
                {{ hotline.number }}
              </p>
              <p :class="['text-sm mt-1', hotline.primary ? 'text-red-100' : 'text-gray-500']">
                {{ hotline.desc }}
              </p>
            </div>
            <div :class="[
              'w-12 h-12 rounded-full flex items-center justify-center',
              hotline.primary ? 'bg-white/20' : 'bg-red-100 dark:bg-red-900/30'
            ]">
              <van-icon name="phone-o" size="24" :color="hotline.primary ? 'white' : '#ef4444'" />
            </div>
          </div>
          <van-button
            v-if="hotline.primary"
            block
            round
            class="mt-4 !bg-white !text-red-500 !border-0"
          >
            立即拨打
          </van-button>
        </a>
      </div>

      <!-- 重要提醒 -->
      <div class="glass rounded-2xl p-4 bg-indigo-50 dark:bg-indigo-900/20">
        <h3 class="font-semibold text-indigo-900 dark:text-indigo-300 mb-3">
          💜 重要提醒
        </h3>
        <ul class="space-y-2">
          <li
            v-for="reminder in reminders"
            :key="reminder"
            class="flex items-start gap-2 text-sm text-indigo-700 dark:text-indigo-400"
          >
            <span>•</span>
            <span>{{ reminder }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="px-4 pb-6 safe-area-bottom">
      <van-button
        block
        round
        size="large"
        @click="router.back()"
      >
        返回聊天
      </van-button>
    </div>
  </div>
</template>
