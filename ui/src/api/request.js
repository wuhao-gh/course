import axios from 'axios'
import { ElMessage } from "element-plus"
import router from '@/router'
import { useUserStore } from '@/stores/user'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.log(error)
    const { response } = error
    if (response) {
      // 根据状态码处理错误
      switch (response.status) {
        case 401:
          // 未授权，清除 token 并跳转到登录页
          const userStore = useUserStore()
          userStore.clearToken()
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('没有权限访问该资源')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(response.data?.message || '未知错误')
      }
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

// 封装 GET 请求
export function get(url, params, config = {}) {
  return request.get(url, { params, ...config })
}

// 封装 POST 请求
export function post(url, data, config = {}) {
  return request.post(url, data, config)
}

// 封装 PUT 请求
export function put(url, data, config = {}) {
  return request.put(url, data, config)
}

// 封装 DELETE 请求
export function del(url, config = {}) {
  return request.delete(url, config)
}

export default request
