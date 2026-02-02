<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isRunning = ref(false)
const phase = ref<'ready' | 'inhale' | 'hold' | 'exhale'>('ready')
const phaseText = ref('准备开始')
const countdown = ref(0)
const circleScale = ref(1)

let timer: number | null = null

const phases = {
  inhale: { duration: 4, text: '吸气', scale: 1.3 },
  hold: { duration: 4, text: '屏息', scale: 1.3 },
  exhale: { duration: 4, text: '呼气', scale: 1 },
}

const startBreathing = () => {
  if (isRunning.value) {
    stopBreathing()
    return
  }

  isRunning.value = true
  runPhase('inhale')
}

const runPhase = (currentPhase: 'inhale' | 'hold' | 'exhale') => {
  phase.value = currentPhase
  const config = phases[currentPhase]
  phaseText.value = config.text
  countdown.value = config.duration
  circleScale.value = config.scale

  timer = window.setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer!)
      // 循环到下一个阶段
      const nextPhase = currentPhase === 'inhale' ? 'hold' :
                        currentPhase === 'hold' ? 'exhale' : 'inhale'
      if (isRunning.value) {
        runPhase(nextPhase)
      }
    }
  }, 1000)
}

const stopBreathing = () => {
  isRunning.value = false
  phase.value = 'ready'
  phaseText.value = '准备开始'
  circleScale.value = 1
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-pink-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex flex-col">
    <!-- 顶部栏 -->
    <div class="flex items-center justify-between px-4 py-3 safe-area-top">
      <van-icon name="arrow-left" size="24" @click="router.back()" />
      <h1 class="text-lg font-semibold text-gray-900 dark:text-white">呼吸练习</h1>
      <div class="w-6"></div>
    </div>

    <!-- 主内容 -->
    <div class="flex-1 flex flex-col items-center justify-center px-8">
      <!-- 呼吸圆圈 -->
      <div class="relative w-48 h-48 mb-8">
        <div
          class="absolute inset-0 rounded-full bg-gradient-to-br from-indigo-400 to-pink-400 opacity-30 transition-transform duration-1000"
          :style="{ transform: `scale(${circleScale})` }"
        ></div>
        <div
          class="absolute inset-4 rounded-full bg-gradient-to-br from-indigo-500 to-pink-500 opacity-50 transition-transform duration-1000"
          :style="{ transform: `scale(${circleScale})` }"
        ></div>
        <div class="absolute inset-0 flex flex-col items-center justify-center">
          <span class="text-2xl font-bold text-gray-700 dark:text-gray-200">{{ phaseText }}</span>
          <span v-if="isRunning" class="text-4xl font-bold text-primary-600 mt-2">{{ countdown }}</span>
        </div>
      </div>

      <!-- 说明文字 -->
      <p class="text-gray-600 dark:text-gray-400 text-center mb-8">
        跟随圆圈的缩放调整呼吸节奏<br/>
        吸气 4 秒 → 屏息 4 秒 → 呼气 4 秒
      </p>

      <!-- 控制按钮 -->
      <van-button
        type="primary"
        size="large"
        round
        block
        class="max-w-xs"
        @click="startBreathing"
      >
        {{ isRunning ? '停止练习' : '开始练习' }}
      </van-button>
    </div>

    <!-- 底部提示 -->
    <div class="px-8 pb-8 safe-area-bottom">
      <div class="glass rounded-xl p-4 text-center">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          💡 深呼吸可以激活副交感神经系统，帮助缓解焦虑和压力
        </p>
      </div>
    </div>
  </div>
</template>
