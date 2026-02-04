<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast, showLoadingToast, closeToast, showConfirmDialog } from 'vant'
import axios from 'axios'
import { getToken } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('dashboard')
const stats = ref({ total_skills: 0, total_rules: 0, total_modules: 0, active_skills: 0 })
const skills = ref<any[]>([])
const rules = ref<any[]>([])
const users = ref<any[]>([])
const profiles = ref<any[]>([])
const selectedProfile = ref<any>(null)
const showProfileDetail = ref(false)

// Edit dialogs
const showSkillEdit = ref(false)
const showRuleEdit = ref(false)
const showUserEdit = ref(false)
const editingSkill = ref<any>({})
const editingRule = ref<any>({})
const editingUser = ref<any>({})
const isCreating = ref(false)

// Pickers
const showModulePicker = ref(false)
const showRolePicker = ref(false)
const showEmotionPicker = ref(false)
const showOperatorPicker = ref(false)
const showSignalPicker = ref(false)
const showRiskPicker = ref(false)
const currentConditionIndex = ref(-1)

const moduleOptions = [
  { text: '正念', value: '正念' },
  { text: '痛苦耐受', value: '痛苦耐受' },
  { text: '情绪调节', value: '情绪调节' },
  { text: '人际效能', value: '人际效能' },
]
const roleOptions = [
  { text: '管理员', value: 'admin' },
  { text: '会员', value: 'member' },
  { text: '普通用户', value: 'user' },
]
const emotionOptions = [
  { text: '焦虑', value: '焦虑' },
  { text: '悲伤', value: '悲伤' },
  { text: '愤怒', value: '愤怒' },
  { text: '恐惧', value: '恐惧' },
  { text: '空虚感', value: '空虚感' },
  { text: '羞愧', value: '羞愧' },
  { text: '内疚', value: '内疚' },
  { text: '绝望', value: '绝望' },
]
const operatorOptions = [
  { text: '>=', value: '>=' },
  { text: '>', value: '>' },
  { text: '<=', value: '<=' },
  { text: '<', value: '<' },
  { text: '==', value: '==' },
]
const signalOptions = [
  { text: '自伤冲动', value: 'self_harm_impulse' },
  { text: '绝望程度', value: 'despair_level' },
  { text: '激越程度', value: 'agitation_level' },
  { text: '空虚感', value: 'emptiness_level' },
  { text: '羞愧程度', value: 'shame_level' },
]
const riskOptions = [
  { text: '低风险', value: 'LOW' },
  { text: '中风险', value: 'MEDIUM' },
  { text: '高风险', value: 'HIGH' },
  { text: '危机', value: 'CRITICAL' },
]

const onModuleConfirm = ({ selectedOptions }: any) => {
  editingSkill.value.module_name = selectedOptions[0]?.text || ''
  showModulePicker.value = false
}

const onRoleConfirm = ({ selectedOptions }: any) => {
  editingUser.value.role = selectedOptions[0]?.value || 'user'
  showRolePicker.value = false
}

const DBT_ADMIN_KEY = 'dbt-admin-secret-key'

const api = axios.create({ baseURL: '/api' })

// Fetch helpers
const fetchDBT = async (endpoint: string, options: any = {}) => {
  const response = await api({
    url: `/v1/admin${endpoint}`,
    headers: { 'X-Admin-Key': DBT_ADMIN_KEY, ...options.headers },
    ...options
  })
  return response.data
}

const fetchAdmin = async (endpoint: string, options: any = {}) => {
  const response = await api({
    url: `/admin${endpoint}`,
    headers: { Authorization: `Bearer ${getToken()}`, ...options.headers },
    ...options
  })
  return response.data
}

// Load data
const loadDashboard = async () => {
  try {
    stats.value = await fetchDBT('/stats')
  } catch (e) {
    console.error(e)
  }
}

const loadSkills = async () => {
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    skills.value = await fetchDBT('/skills')
  } catch (e: any) {
    showToast('加载失败')
  } finally {
    closeToast()
  }
}

const loadRules = async () => {
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    rules.value = await fetchDBT('/rules')
  } catch (e: any) {
    showToast('加载失败')
  } finally {
    closeToast()
  }
}

const loadUsers = async () => {
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    users.value = await fetchAdmin('/users')
  } catch (e: any) {
    showToast('加载失败')
  } finally {
    closeToast()
  }
}

const loadProfiles = async () => {
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    profiles.value = await fetchDBT('/profiles')
  } catch (e: any) {
    showToast('加载失败')
  } finally {
    closeToast()
  }
}

const viewProfile = async (userId: string) => {
  showLoadingToast({ message: '加载中...', forbidClick: true })
  try {
    selectedProfile.value = await fetchDBT(`/profiles/${encodeURIComponent(userId)}`)
    showProfileDetail.value = true
  } catch (e: any) {
    showToast('加载失败')
  } finally {
    closeToast()
  }
}

// Actions
const toggleSkill = async (skill: any) => {
  try {
    await fetchDBT(`/skills/${skill.id}/toggle`, { method: 'POST' })
    showToast('状态已切换')
    loadSkills()
  } catch (e) {
    showToast('操作失败')
  }
}

const deleteSkill = async (skill: any) => {
  try {
    await showConfirmDialog({ title: '确认删除', message: `确定要删除技能「${skill.name}」吗？` })
    await fetchDBT(`/skills/${skill.id}`, { method: 'DELETE' })
    showToast('删除成功')
    loadSkills()
  } catch (e) {}
}

const toggleRule = async (rule: any) => {
  try {
    await fetchDBT(`/rules/${rule.id}/toggle`, { method: 'POST' })
    showToast('状态已切换')
    loadRules()
  } catch (e) {
    showToast('操作失败')
  }
}

const toggleUser = async (user: any) => {
  try {
    await fetchAdmin(`/users/${user.id}`, {
      method: 'PUT',
      data: { is_active: !user.is_active },
      headers: { 'Content-Type': 'application/json' }
    })
    showToast('状态已切换')
    loadUsers()
  } catch (e) {
    showToast('操作失败')
  }
}

// Edit functions
const openSkillEdit = (skill?: any) => {
  isCreating.value = !skill
  editingSkill.value = skill ? { ...skill } : { name: '', name_en: '', module_name: '正念', description: '', is_active: true }
  showSkillEdit.value = true
}

const saveSkill = async () => {
  try {
    if (isCreating.value) {
      await fetchDBT('/skills', { method: 'POST', data: editingSkill.value, headers: { 'Content-Type': 'application/json' } })
      showToast('创建成功')
    } else {
      await fetchDBT(`/skills/${editingSkill.value.id}`, { method: 'PUT', data: editingSkill.value, headers: { 'Content-Type': 'application/json' } })
      showToast('保存成功')
    }
    showSkillEdit.value = false
    loadSkills()
  } catch (e) {
    showToast('操作失败')
  }
}

const openRuleEdit = (rule?: any) => {
  isCreating.value = !rule
  if (rule) {
    // 深拷贝规则，确保 conditions 结构完整
    editingRule.value = {
      ...rule,
      conditions: {
        emotion_conditions: rule.conditions?.emotion_conditions || [],
        trigger_signals: rule.conditions?.trigger_signals || [],
        arousal: rule.conditions?.arousal || null,
        context_contains: rule.conditions?.context_contains || [],
        risk_level: rule.conditions?.risk_level || [],
      }
    }
    // 初始化关键词文本
    contextKeywordsText.value = (rule.conditions?.context_contains || []).join(', ')
  } else {
    editingRule.value = {
      rule_name: '',
      priority: 50,
      description: '',
      is_active: true,
      conditions: {
        emotion_conditions: [],
        trigger_signals: [],
        arousal: null,
        context_contains: [],
        risk_level: [],
      }
    }
    contextKeywordsText.value = ''
  }
  showRuleEdit.value = true
}

// 规则条件编辑辅助函数
const addEmotionCondition = () => {
  if (!editingRule.value.conditions.emotion_conditions) {
    editingRule.value.conditions.emotion_conditions = []
  }
  editingRule.value.conditions.emotion_conditions.push({ emotion: '焦虑', operator: '>=', value: 0.5 })
}

const removeEmotionCondition = (index: number) => {
  editingRule.value.conditions.emotion_conditions.splice(index, 1)
}

const addTriggerSignal = () => {
  if (!editingRule.value.conditions.trigger_signals) {
    editingRule.value.conditions.trigger_signals = []
  }
  editingRule.value.conditions.trigger_signals.push({ signal: 'agitation_level', operator: '>=', value: 0.4 })
}

const removeTriggerSignal = (index: number) => {
  editingRule.value.conditions.trigger_signals.splice(index, 1)
}

const toggleArousal = () => {
  if (editingRule.value.conditions.arousal) {
    editingRule.value.conditions.arousal = null
  } else {
    editingRule.value.conditions.arousal = { operator: '>=', value: 0.6 }
  }
}

const contextKeywordsText = ref('')
const updateContextKeywords = () => {
  editingRule.value.conditions.context_contains = contextKeywordsText.value
    .split(/[,，\s]+/)
    .filter((k: string) => k.trim())
}

const getSignalLabel = (signal: string) => {
  const opt = signalOptions.find(o => o.value === signal)
  return opt ? opt.text : signal
}

const saveRule = async () => {
  try {
    if (isCreating.value) {
      await fetchDBT('/rules', { method: 'POST', data: editingRule.value, headers: { 'Content-Type': 'application/json' } })
      showToast('创建成功')
    } else {
      await fetchDBT(`/rules/${editingRule.value.id}`, { method: 'PUT', data: editingRule.value, headers: { 'Content-Type': 'application/json' } })
      showToast('保存成功')
    }
    showRuleEdit.value = false
    loadRules()
  } catch (e) {
    showToast('操作失败')
  }
}

const openUserEdit = (user?: any) => {
  isCreating.value = !user
  editingUser.value = user ? { ...user } : { email: '', username: '', password: '', role: 'user', is_active: true }
  showUserEdit.value = true
}

const saveUser = async () => {
  try {
    if (isCreating.value) {
      await fetchAdmin('/users', { method: 'POST', data: editingUser.value, headers: { 'Content-Type': 'application/json' } })
      showToast('创建成功')
    } else {
      const { password, ...updateData } = editingUser.value
      await fetchAdmin(`/users/${editingUser.value.id}`, { method: 'PUT', data: updateData, headers: { 'Content-Type': 'application/json' } })
      showToast('保存成功')
    }
    showUserEdit.value = false
    loadUsers()
  } catch (e) {
    showToast('操作失败')
  }
}

const deleteUser = async (user: any) => {
  try {
    await showConfirmDialog({ title: '确认删除', message: `确定要删除用户「${user.username || user.email}」吗？` })
    await fetchAdmin(`/users/${user.id}`, { method: 'DELETE' })
    showToast('删除成功')
    loadUsers()
  } catch (e) {}
}

const deleteRule = async (rule: any) => {
  try {
    await showConfirmDialog({ title: '确认删除', message: `确定要删除规则「${rule.rule_name}」吗？` })
    await fetchDBT(`/rules/${rule.id}`, { method: 'DELETE' })
    showToast('删除成功')
    loadRules()
  } catch (e) {}
}

const switchTab = (tab: string) => {
  activeTab.value = tab
  if (tab === 'dashboard') loadDashboard()
  else if (tab === 'skills') loadSkills()
  else if (tab === 'rules') loadRules()
  else if (tab === 'users') loadUsers()
  else if (tab === 'profiles') loadProfiles()
}

const roleLabels: Record<string, string> = { admin: '管理员', member: '会员', user: '用户' }

onMounted(() => {
  if (!authStore.isAdmin) {
    showToast('需要管理员权限')
    router.push('/')
    return
  }
  loadDashboard()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <div class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-4 py-4 safe-area-top">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <van-icon name="arrow-left" size="20" @click="router.push('/')" />
          <h1 class="text-lg font-semibold">管理后台</h1>
        </div>
        <van-icon name="setting-o" size="20" />
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white border-b sticky top-0 z-10 overflow-x-auto">
      <div class="flex min-w-max">
        <button
          v-for="tab in [
            { key: 'dashboard', label: '概览' },
            { key: 'skills', label: '技能' },
            { key: 'rules', label: '规则' },
            { key: 'users', label: '用户' },
            { key: 'profiles', label: '画像' }
          ]"
          :key="tab.key"
          :class="[
            'flex-1 min-w-[60px] py-3 text-sm font-medium border-b-2 transition-colors',
            activeTab === tab.key
              ? 'text-indigo-600 border-indigo-600'
              : 'text-gray-500 border-transparent'
          ]"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Dashboard -->
    <div v-if="activeTab === 'dashboard'" class="p-4 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-2xl font-bold text-indigo-600">{{ stats.total_skills }}</p>
          <p class="text-sm text-gray-500">总技能数</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-2xl font-bold text-pink-600">{{ stats.total_rules }}</p>
          <p class="text-sm text-gray-500">总规则数</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-2xl font-bold text-green-600">{{ stats.active_skills }}</p>
          <p class="text-sm text-gray-500">启用技能</p>
        </div>
        <div class="bg-white rounded-xl p-4 shadow-sm">
          <p class="text-2xl font-bold text-purple-600">{{ stats.total_modules }}</p>
          <p class="text-sm text-gray-500">DBT模块</p>
        </div>
      </div>
    </div>

    <!-- Skills List -->
    <div v-if="activeTab === 'skills'" class="p-4">
      <div class="mb-3">
        <van-button type="primary" size="small" icon="plus" @click="openSkillEdit()">新建技能</van-button>
      </div>
      <van-cell-group inset>
        <van-cell
          v-for="skill in skills"
          :key="skill.id"
          :title="skill.name"
          :label="skill.module_name"
          is-link
          @click="openSkillEdit(skill)"
        >
          <template #right-icon>
            <div class="flex items-center gap-2">
              <van-tag :type="skill.is_active ? 'success' : 'default'" size="medium">
                {{ skill.is_active ? '启用' : '禁用' }}
              </van-tag>
              <van-icon name="exchange" @click.stop="toggleSkill(skill)" />
              <van-icon name="delete-o" color="#ee0a24" @click.stop="deleteSkill(skill)" />
            </div>
          </template>
        </van-cell>
        <van-empty v-if="!skills.length" description="暂无技能" />
      </van-cell-group>
    </div>

    <!-- Rules List -->
    <div v-if="activeTab === 'rules'" class="p-4">
      <div class="mb-3">
        <van-button type="primary" size="small" icon="plus" @click="openRuleEdit()">新建规则</van-button>
      </div>
      <van-cell-group inset>
        <van-cell
          v-for="rule in rules"
          :key="rule.id"
          :title="rule.rule_name"
          :label="`优先级: ${rule.priority}`"
          is-link
          @click="openRuleEdit(rule)"
        >
          <template #right-icon>
            <div class="flex items-center gap-2">
              <van-tag :type="rule.is_active ? 'success' : 'default'" size="medium">
                {{ rule.is_active ? '启用' : '禁用' }}
              </van-tag>
              <van-icon name="exchange" @click.stop="toggleRule(rule)" />
              <van-icon name="delete-o" color="#ee0a24" @click.stop="deleteRule(rule)" />
            </div>
          </template>
        </van-cell>
        <van-empty v-if="!rules.length" description="暂无规则" />
      </van-cell-group>
    </div>

    <!-- Users List -->
    <div v-if="activeTab === 'users'" class="p-4">
      <div class="mb-3">
        <van-button type="primary" size="small" icon="plus" @click="openUserEdit()">新建用户</van-button>
      </div>
      <van-cell-group inset>
        <van-cell
          v-for="user in users"
          :key="user.id"
          :title="user.username || user.email"
          :label="user.email"
          is-link
          @click="openUserEdit(user)"
        >
          <template #right-icon>
            <div class="flex items-center gap-2">
              <van-tag type="primary" size="medium">{{ roleLabels[user.role] || user.role }}</van-tag>
              <van-tag :type="user.is_active ? 'success' : 'danger'" size="medium">
                {{ user.is_active ? '启用' : '禁用' }}
              </van-tag>
              <van-icon name="exchange" @click.stop="toggleUser(user)" />
              <van-icon name="delete-o" color="#ee0a24" @click.stop="deleteUser(user)" />
            </div>
          </template>
        </van-cell>
        <van-empty v-if="!users.length" description="暂无用户" />
      </van-cell-group>
    </div>

    <!-- Profiles List -->
    <div v-if="activeTab === 'profiles'" class="p-4">
      <van-cell-group inset>
        <van-cell
          v-for="profile in profiles"
          :key="profile.user_id"
          :title="profile.user_id"
          :label="`互动: ${profile.total_interactions || 0} 次`"
          is-link
          @click="viewProfile(profile.user_id)"
        >
          <template #right-icon>
            <div class="flex items-center gap-2">
              <van-tag type="warning" size="medium">
                危机: {{ profile.crisis_count || 0 }}
              </van-tag>
            </div>
          </template>
        </van-cell>
        <van-empty v-if="!profiles.length" description="暂无用户画像" />
      </van-cell-group>
    </div>

    <!-- Profile Detail Popup -->
    <van-popup
      v-model:show="showProfileDetail"
      position="bottom"
      round
      :style="{ height: '80%' }"
    >
      <div v-if="selectedProfile" class="p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">用户画像详情</h3>
          <van-icon name="cross" size="20" @click="showProfileDetail = false" />
        </div>

        <!-- 基本信息 -->
        <div class="bg-gray-50 rounded-xl p-4 mb-4">
          <h4 class="font-medium mb-2">基本信息</h4>
          <p class="text-sm text-gray-600">用户ID: {{ selectedProfile.user_id }}</p>
          <p class="text-sm text-gray-600">总互动: {{ selectedProfile.total_interactions || 0 }} 次</p>
          <p class="text-sm text-gray-600">危机次数: {{ selectedProfile.crisis_count || 0 }} 次</p>
          <p class="text-sm text-gray-600">干预次数: {{ selectedProfile.intervention_count || 0 }} 次</p>
        </div>

        <!-- 情绪基准线 -->
        <div class="bg-gray-50 rounded-xl p-4 mb-4">
          <h4 class="font-medium mb-3">情绪基准线</h4>
          <div v-if="selectedProfile.emotion_baseline" class="space-y-2">
            <div
              v-for="(value, emotion) in selectedProfile.emotion_baseline"
              :key="emotion"
              class="flex items-center gap-2"
            >
              <span class="text-sm text-gray-600 w-12">{{ emotion }}</span>
              <div class="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-indigo-500 h-2 rounded-full"
                  :style="{ width: `${(value * 100).toFixed(0)}%` }"
                ></div>
              </div>
              <span class="text-xs text-gray-500 w-10">{{ (value * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <p v-else class="text-sm text-gray-400">暂无数据</p>
        </div>

        <!-- 性格画像 -->
        <div class="bg-gray-50 rounded-xl p-4">
          <h4 class="font-medium mb-3">性格画像 (大五人格)</h4>
          <div v-if="selectedProfile.personality" class="space-y-2">
            <div
              v-for="(label, key) in { openness: '开放性', conscientiousness: '尽责性', extraversion: '外向性', agreeableness: '宜人性', neuroticism: '神经质' }"
              :key="key"
              class="flex items-center gap-2"
            >
              <span class="text-sm text-gray-600 w-12">{{ label }}</span>
              <div class="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  class="bg-pink-500 h-2 rounded-full"
                  :style="{ width: `${((selectedProfile.personality[key] || 0.5) * 100).toFixed(0)}%` }"
                ></div>
              </div>
              <span class="text-xs text-gray-500 w-10">{{ ((selectedProfile.personality[key] || 0.5) * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <p v-else class="text-sm text-gray-400">暂无数据</p>
        </div>
      </div>
    </van-popup>

    <!-- Skill Edit Popup -->
    <van-popup v-model:show="showSkillEdit" position="bottom" round :style="{ height: '70%' }">
      <div class="p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">{{ isCreating ? '新建技能' : '编辑技能' }}</h3>
          <van-icon name="cross" size="20" @click="showSkillEdit = false" />
        </div>
        <van-form @submit="saveSkill">
          <van-cell-group inset>
            <van-field v-model="editingSkill.name" label="技能名称" placeholder="请输入技能名称" required />
            <van-field v-model="editingSkill.name_en" label="英文名称" placeholder="请输入英文名称" />
            <van-field v-model="editingSkill.module_name" label="所属模块" placeholder="请选择模块" is-link readonly @click="showModulePicker = true" />
            <van-field v-model="editingSkill.description" label="描述" type="textarea" rows="3" placeholder="请输入技能描述" />
            <van-cell title="启用状态">
              <template #right-icon>
                <van-switch v-model="editingSkill.is_active" />
              </template>
            </van-cell>
          </van-cell-group>
          <div class="mt-4 px-4">
            <van-button type="primary" block native-type="submit">保存</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- Rule Edit Popup -->
    <van-popup v-model:show="showRuleEdit" position="bottom" round :style="{ height: '85%' }">
      <div class="p-4 h-full overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">{{ isCreating ? '新建规则' : '编辑规则' }}</h3>
          <van-icon name="cross" size="20" @click="showRuleEdit = false" />
        </div>
        <van-form @submit="saveRule">
          <!-- 基本信息 -->
          <van-cell-group inset title="基本信息">
            <van-field v-model="editingRule.rule_name" label="规则名称" placeholder="请输入规则名称" required />
            <van-field v-model.number="editingRule.priority" label="优先级" type="digit" placeholder="0-1000，越大越优先" />
            <van-field v-model="editingRule.description" label="描述" type="textarea" rows="2" placeholder="规则描述" />
            <van-cell title="启用状态">
              <template #right-icon>
                <van-switch v-model="editingRule.is_active" />
              </template>
            </van-cell>
          </van-cell-group>

          <!-- 情绪条件 -->
          <van-cell-group inset title="情绪条件" class="mt-3">
            <div v-for="(cond, idx) in editingRule.conditions?.emotion_conditions || []" :key="idx" class="flex items-center gap-2 px-4 py-2 border-b">
              <van-tag type="primary">{{ cond.emotion }}</van-tag>
              <span class="text-sm">{{ cond.operator }}</span>
              <input v-model.number="cond.value" type="number" step="0.1" min="0" max="1" class="w-16 px-2 py-1 border rounded text-sm" />
              <van-icon name="delete-o" color="#ee0a24" @click="removeEmotionCondition(idx)" />
            </div>
            <van-cell is-link @click="addEmotionCondition">
              <template #title>
                <span class="text-indigo-600">+ 添加情绪条件</span>
              </template>
            </van-cell>
          </van-cell-group>

          <!-- 触发信号 -->
          <van-cell-group inset title="触发信号" class="mt-3">
            <div v-for="(sig, idx) in editingRule.conditions?.trigger_signals || []" :key="idx" class="flex items-center gap-2 px-4 py-2 border-b">
              <van-tag type="warning">{{ getSignalLabel(sig.signal) }}</van-tag>
              <span class="text-sm">{{ sig.operator }}</span>
              <input v-model.number="sig.value" type="number" step="0.1" min="0" max="1" class="w-16 px-2 py-1 border rounded text-sm" />
              <van-icon name="delete-o" color="#ee0a24" @click="removeTriggerSignal(idx)" />
            </div>
            <van-cell is-link @click="addTriggerSignal">
              <template #title>
                <span class="text-indigo-600">+ 添加触发信号</span>
              </template>
            </van-cell>
          </van-cell-group>

          <!-- 唤醒度条件 -->
          <van-cell-group inset title="唤醒度条件" class="mt-3">
            <van-cell title="启用唤醒度条件">
              <template #right-icon>
                <van-switch :model-value="!!editingRule.conditions?.arousal" @update:model-value="toggleArousal" />
              </template>
            </van-cell>
            <div v-if="editingRule.conditions?.arousal" class="flex items-center gap-2 px-4 py-2">
              <span class="text-sm">唤醒度</span>
              <select v-model="editingRule.conditions.arousal.operator" class="px-2 py-1 border rounded text-sm">
                <option value=">=">>=</option>
                <option value=">">></option>
                <option value="<="><=</option>
                <option value="<"><</option>
              </select>
              <input v-model.number="editingRule.conditions.arousal.value" type="number" step="0.1" min="0" max="1" class="w-16 px-2 py-1 border rounded text-sm" />
            </div>
          </van-cell-group>

          <!-- 情境关键词 -->
          <van-cell-group inset title="情境关键词" class="mt-3">
            <van-field
              v-model="contextKeywordsText"
              label="关键词"
              placeholder="用逗号分隔，如：人际,关系,朋友"
              @blur="updateContextKeywords"
            />
            <div v-if="editingRule.conditions?.context_contains?.length" class="px-4 py-2 flex flex-wrap gap-1">
              <van-tag v-for="kw in editingRule.conditions.context_contains" :key="kw" type="success" size="medium">{{ kw }}</van-tag>
            </div>
          </van-cell-group>

          <div class="mt-4 px-4 pb-4">
            <van-button type="primary" block native-type="submit">保存</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- User Edit Popup -->
    <van-popup v-model:show="showUserEdit" position="bottom" round :style="{ height: '70%' }">
      <div class="p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">{{ isCreating ? '新建用户' : '编辑用户' }}</h3>
          <van-icon name="cross" size="20" @click="showUserEdit = false" />
        </div>
        <van-form @submit="saveUser">
          <van-cell-group inset>
            <van-field v-model="editingUser.email" label="邮箱" placeholder="请输入邮箱" required :disabled="!isCreating" />
            <van-field v-model="editingUser.username" label="用户名" placeholder="请输入用户名" required />
            <van-field v-if="isCreating" v-model="editingUser.password" label="密码" type="password" placeholder="请输入密码" required />
            <van-field :model-value="roleLabels[editingUser.role] || editingUser.role" label="角色" is-link readonly @click="showRolePicker = true" />
            <van-cell title="启用状态">
              <template #right-icon>
                <van-switch v-model="editingUser.is_active" />
              </template>
            </van-cell>
          </van-cell-group>
          <div class="mt-4 px-4">
            <van-button type="primary" block native-type="submit">保存</van-button>
          </div>
        </van-form>
      </div>
    </van-popup>

    <!-- Module Picker -->
    <van-popup v-model:show="showModulePicker" position="bottom" round>
      <van-picker
        title="选择模块"
        :columns="moduleOptions"
        @confirm="onModuleConfirm"
        @cancel="showModulePicker = false"
      />
    </van-popup>

    <!-- Role Picker -->
    <van-popup v-model:show="showRolePicker" position="bottom" round>
      <van-picker
        title="选择角色"
        :columns="roleOptions"
        @confirm="onRoleConfirm"
        @cancel="showRolePicker = false"
      />
    </van-popup>
  </div>
</template>
