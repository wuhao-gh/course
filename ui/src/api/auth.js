import request from './request'

export const login = async (username, password) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  const data = await request({
    url: '/auth/token',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return {
    token: data.access_token,
    tokenType: data.token_type,
    expiresIn: data.expires_in
  }
}

export const getCurrentUser = async () => {
  return await request({
    url: '/auth/user/me',
    method: 'get'
  })
}

export const logout = async () => {
  await request({
    url: '/auth/logout',
    method: 'post'
  })
}

export function getAllUsers() {
  return request({
    url: '/auth/user',
    method: 'get'
  })
}

export function register(username, password) {
  return request({
    url: '/register',
    method: 'post',
    data: { username, password }
  })
}
