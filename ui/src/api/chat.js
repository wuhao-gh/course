import request from './request'

export function getChatMessages(userId) {
  return request({
    url: `/chat/messages/${userId}`,
    method: 'get'
  })
}
