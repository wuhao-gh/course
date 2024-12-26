import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref({})

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    localStorage.removeItem('token')
  }

  const isLoggedIn = () => {
    return !!token.value
  }

  return { 
    token,
    user,
    setToken,
    clearToken,
    isLoggedIn
  }
})
