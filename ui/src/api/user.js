import { get, post } from '@/api/request'

// 用户相关接口
export const userApi = {
  // 登录
  login(data) {
    return post('/auth/login', data)
  },

  // 获取用户信息
  getUserInfo() {
    return get('/user/info')
  },

  // 更新用户信息
  updateUserInfo(data) {
    return post('/user/update', data)
  }
}