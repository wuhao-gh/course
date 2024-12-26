import request from './request'

export function login(username, password) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)

  return request({
    url: '/auth/token',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function register(username, password) {
  return request({
    url: '/register',
    method: 'post',
    data: { username, password }
  })
}
