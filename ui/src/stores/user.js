import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const user = ref(null)
  const tokenExpires = ref(0)

  const setToken = (newToken, expiresIn) => {
    token.value = newToken
    // 将过期秒数转换为过期时间戳
    tokenExpires.value = Date.now() + expiresIn * 1000
  }

  const setUser = (newUser) => {
    user.value = newUser
  }

  const clearToken = () => {
    token.value = ''
    tokenExpires.value = 0
  }

  const clearUserInfo = () => {
    user.value = null
  }

  const isLoggedIn = () => {
    const isLoggedIn = !!token.value && Date.now() < tokenExpires.value
    return isLoggedIn
  }

  const isStudent = () => {
    return user.value?.role === 'student'
  }

  const isTeacher = () => {
    return user.value?.role === 'teacher'
  }

  return { 
    token,
    user,
    tokenExpires,
    setToken,
    setUser,
    clearToken,
    clearUserInfo,
    isLoggedIn,
    isStudent,
    isTeacher
  }
}, {
  persist: true
})
