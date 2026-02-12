import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const isDark = ref(false)
  const showCrisisModal = ref(false)

  const toggleDark = () => {
    isDark.value = !isDark.value
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('darkMode', isDark.value ? 'true' : 'false')
  }

  const initDarkMode = () => {
    const saved = localStorage.getItem('darkMode')
    if (saved === 'true') {
      isDark.value = true
      document.documentElement.classList.add('dark')
    }
  }

  const openCrisisModal = () => {
    showCrisisModal.value = true
  }

  const closeCrisisModal = () => {
    showCrisisModal.value = false
  }

  return {
    isDark,
    showCrisisModal,
    toggleDark,
    initDarkMode,
    openCrisisModal,
    closeCrisisModal,
  }
})
