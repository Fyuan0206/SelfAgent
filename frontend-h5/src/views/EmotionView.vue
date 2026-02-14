<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, RadarComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useChatStore } from '@/stores/chat'

use([CanvasRenderer, RadarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, RadarComponent])

const chatStore = useChatStore()

// 情绪雷达图配置
const radarOption = ref({
  radar: {
    indicator: [
      { name: '平静', max: 1 },
      { name: '焦虑', max: 1 },
      { name: '悲伤', max: 1 },
      { name: '愤怒', max: 1 },
      { name: '恐惧', max: 1 },
      { name: '开心', max: 1 },
    ],
    radius: '65%',
  },
  series: [{
    type: 'radar',
    data: [{
      value: [0.7, 0.2, 0.1, 0.1, 0.1, 0.5],
      name: '当前情绪',
      areaStyle: {
        color: 'rgba(99, 102, 241, 0.3)'
      },
      lineStyle: {
        color: '#6366f1'
      },
      itemStyle: {
        color: '#6366f1'
      }
    }]
  }]
})

// 情绪趋势图配置
const trendOption = ref({
  grid: {
    left: '10%',
    right: '5%',
    top: '10%',
    bottom: '15%'
  },
  xAxis: {
    type: 'category',
    data: ['一', '二', '三', '四', '五', '六', '日'],
    axisLine: { lineStyle: { color: '#e5e7eb' } },
    axisLabel: { color: '#9ca3af' }
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 1,
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#f3f4f6' } },
    axisLabel: { color: '#9ca3af' }
  },
  series: [{
    data: [0.6, 0.4, 0.7, 0.5, 0.8, 0.6, 0.7],
    type: 'line',
    smooth: true,
    lineStyle: { color: '#6366f1', width: 3 },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(99, 102, 241, 0.3)' },
          { offset: 1, color: 'rgba(99, 102, 241, 0)' }
        ]
      }
    },
    itemStyle: { color: '#6366f1' }
  }]
})

// 最近情绪记录
const recentEmotions = ref([
  { emoji: '😊', name: '平静', time: '今天 14:30', color: 'bg-green-100' },
  { emoji: '😰', name: '焦虑', time: '今天 10:15', color: 'bg-blue-100' },
  { emoji: '😌', name: '放松', time: '昨天 22:00', color: 'bg-purple-100' },
  { emoji: '😢', name: '难过', time: '昨天 15:30', color: 'bg-gray-100' },
])

const getEmotionBadgeColor = (emotion: string) => {
  const colors: Record<string, string> = {
    '平静': 'success',
    '开心': 'success',
    '焦虑': 'primary',
    '难过': 'default',
    '愤怒': 'danger',
  }
  return colors[emotion] || 'primary'
}
</script>

<template>
  <div class="h-[calc(100vh-96px)] overflow-y-auto px-4 py-4">

    <!-- 当前情绪卡片 -->
    <div class="glass rounded-2xl p-4 shadow-lg mb-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-base font-semibold text-gray-900 dark:text-white">当前情绪状态</h2>
        <van-tag :type="getEmotionBadgeColor(chatStore.currentEmotion.name)">
          {{ chatStore.currentEmotion.name }}
        </van-tag>
      </div>
      <div class="h-48">
        <v-chart :option="radarOption" autoresize />
      </div>
      <p class="text-sm text-gray-600 dark:text-gray-400 text-center mt-2">
        情绪强度: {{ (chatStore.currentEmotion.value * 100).toFixed(0) }}%
      </p>
    </div>

    <!-- 情绪趋势 -->
    <div class="glass rounded-2xl p-4 shadow-lg mb-4">
      <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-3">情绪趋势 (最近7天)</h2>
      <div class="h-40">
        <v-chart :option="trendOption" autoresize />
      </div>
    </div>

    <!-- 最近情绪记录 -->
    <div class="glass rounded-2xl p-4 shadow-lg">
      <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-3">最近情绪记录</h2>
      <van-cell-group inset>
        <van-cell
          v-for="(emotion, index) in recentEmotions"
          :key="index"
          :title="emotion.name"
          :label="emotion.time"
          is-link
        >
          <template #icon>
            <div :class="['w-10 h-10 rounded-lg flex items-center justify-center mr-3', emotion.color]">
              <span class="text-lg">{{ emotion.emoji }}</span>
            </div>
          </template>
        </van-cell>
      </van-cell-group>
    </div>
  </div>
</template>
