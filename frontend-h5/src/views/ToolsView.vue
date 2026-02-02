<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const quickTools = [
  { icon: '🫁', name: '呼吸练习', desc: '放松身心', color: 'bg-indigo-100', route: '/breathing' },
  { icon: '📝', name: '情绪日记', desc: '记录感受', color: 'bg-pink-100', route: '' },
  { icon: '🧪', name: 'DBT技能', desc: '专业指导', color: 'bg-purple-100', route: '' },
  { icon: '📈', name: '情绪趋势', desc: '数据分析', color: 'bg-teal-100', route: '/emotion' },
]

const dbtModules = [
  { icon: '🛡️', name: '痛苦耐受', desc: 'TIPP, STOP, ACCEPTS 等技能', skills: 8 },
  { icon: '💚', name: '情绪调节', desc: 'PLEASE, 反向行动等技能', skills: 6 },
  { icon: '🤝', name: '人际效能', desc: 'DEAR MAN, GIVE, FAST 等技能', skills: 5 },
  { icon: '🧘', name: '正念练习', desc: '观察, 投入, 非评判等技能', skills: 4 },
]

const navigateTo = (route: string) => {
  if (route) {
    router.push(route)
  }
}
</script>

<template>
  <div class="min-h-screen pb-16 px-4 pt-4">
    <h1 class="text-xl font-bold text-gray-900 dark:text-white mb-4">快速工具</h1>

    <!-- 快速工具网格 -->
    <div class="grid grid-cols-2 gap-3 mb-6">
      <div
        v-for="tool in quickTools"
        :key="tool.name"
        :class="['glass rounded-2xl p-4 shadow-lg cursor-pointer active:scale-95 transition-transform', tool.color]"
        @click="navigateTo(tool.route)"
      >
        <div class="text-3xl mb-2">{{ tool.icon }}</div>
        <h3 class="font-semibold text-gray-900">{{ tool.name }}</h3>
        <p class="text-xs text-gray-600">{{ tool.desc }}</p>
      </div>
    </div>

    <!-- DBT 技能模块 -->
    <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-3">DBT 技能模块</h2>
    <div class="glass rounded-2xl shadow-lg overflow-hidden">
      <van-cell-group>
        <van-cell
          v-for="module in dbtModules"
          :key="module.name"
          :title="module.name"
          :label="module.desc"
          is-link
        >
          <template #icon>
            <div class="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center mr-3">
              <span class="text-xl">{{ module.icon }}</span>
            </div>
          </template>
          <template #value>
            <van-tag type="primary" plain>{{ module.skills }}个技能</van-tag>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 紧急求助入口 -->
    <div class="mt-6">
      <van-button
        type="danger"
        block
        round
        size="large"
        class="crisis-pulse"
        @click="router.push('/crisis')"
      >
        <van-icon name="warning-o" class="mr-2" />
        紧急求助
      </van-button>
    </div>
  </div>
</template>
