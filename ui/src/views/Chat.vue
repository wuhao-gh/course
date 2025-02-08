<template>
  <div class="flex h-[calc(100vh-60px)] p-4 gap-4">
    <!-- 左侧用户列表 -->
    <div class="w-64 bg-white rounded-lg shadow flex flex-col">
      <!-- 搜索框 -->
      <div class="p-4 border-b">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户..."
          prefix-icon="Search"
          clearable
        />
      </div>
      <!-- 用户列表 -->
      <div class="flex-1 overflow-y-auto">
        <div
          v-for="user in filteredUsers"
          :key="user.id"
          :class="[
            'p-4 hover:bg-gray-50 cursor-pointer flex items-center gap-3',
            selectedUser?.id === user.id ? 'bg-gray-50' : ''
          ]"
          @click="selectUser(user)"
        >
          <el-avatar :size="40" :src="user.avatar">{{ user.name?.charAt(0) }}</el-avatar>
          <div class="flex-1 min-w-0">
            <div class="font-medium truncate">{{ user.name }}</div>
            <div class="text-sm text-gray-500 truncate">{{ user.email }}</div>
          </div>
          <div v-if="user.unreadCount" class="bg-primary text-white text-xs rounded-full px-2 py-1">
            {{ user.unreadCount }}
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="flex-1 bg-white rounded-lg shadow flex flex-col">
      <!-- 聊天标题 -->
      <div class="p-4 border-b flex items-center" v-if="selectedUser">
        <el-avatar :size="32" :src="selectedUser.avatar" class="mr-3">
          {{ selectedUser.name?.charAt(0) }}
        </el-avatar>
        <div>
          <div class="font-medium">{{ selectedUser.name }}</div>
          <div class="text-sm text-gray-500">{{ selectedUser.status || '在线' }}</div>
        </div>
      </div>

      <!-- 聊天消息区域 -->
      <div class="flex-1 p-4 overflow-y-auto" ref="messageContainer">
        <template v-if="selectedUser">
          <div v-for="message in currentMessages" :key="message.timestamp"
               :class="['mb-4', message.from_user === currentUser.id ? 'flex flex-row-reverse' : 'flex']">
            <div :class="['max-w-[70%] rounded-lg p-3',
                         message.from_user === currentUser.id ? 'bg-primary text-white' : 'bg-gray-100']">
              <div class="test-base">{{ message.content }}</div>
              <div class="text-xs mt-1 text-gray-500">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="h-full flex items-center justify-center text-gray-400">
            请选择一个联系人开始聊天
          </div>
        </template>
      </div>

      <!-- 输入区域 -->
      <div class="border-t p-4" v-if="selectedUser">
        <div class="flex gap-4">
          <el-input
            v-model="messageInput"
            placeholder="输入消息..."
            type="textarea"
            :rows="3"
            @keyup.enter.native="sendMessage"
          />
          <el-button type="primary" @click="sendMessage" :disabled="!messageInput.trim()">
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { getAllUsers } from '../api/auth'
import { getChatMessages } from '../api/chat'

const userStore = useUserStore()
const currentUser = userStore.user
const messages = ref([])
const messageInput = ref('')
const messageContainer = ref(null)
const ws = ref(null)
const users = ref([])
const searchQuery = ref('')
const selectedUser = ref(null)

// 过滤用户列表
const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user =>
    user.name?.toLowerCase().includes(query) ||
    user.email?.toLowerCase().includes(query)
  )
})

// 获取当前对话的消息
const currentMessages = computed(() => {
  if (!selectedUser.value) return []
  return messages.value.filter(msg =>
    (msg.from_user === currentUser.id && msg.to_user === selectedUser.value.id) ||
    (msg.from_user === selectedUser.value.id && msg.to_user === currentUser.id)
  )
})

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await getAllUsers()
    users.value = response.filter(user => user.id !== currentUser.id)
    // 默认选择第一个用户
    if (users.value.length > 0) {
      selectUser(users.value[0])
    }
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

// 加载历史消息
const loadChatHistory = async (userId) => {
  const chatMessages = await getChatMessages(userId)
  messages.value = chatMessages
  scrollToBottom()
}

// 选择用户
const selectUser = async (user) => {
  selectedUser.value = user
  // 清除未读消息计数
  if (user.unreadCount) {
    user.unreadCount = 0
  }
  // 加载与该用户的聊天记录
  await loadChatHistory(user.id)
}

// 连接 WebSocket
const connectWebSocket = () => {
  // ws.value = new WebSocket(`ws://localhost:8000/api/chat/ws/${currentUser.id}`)
  ws.value = new WebSocket(`wss://course.wuhao.dev/api/chat/ws/${currentUser.id}`)

  ws.value.onmessage = (event) => {
    const message = JSON.parse(event.data)
    messages.value.push(message)

    // 如果是私聊消息且不是当前选中的用户，增加未读计数
    if (message.to_user === currentUser.id && message.from_user !== selectedUser.value?.id) {
      const sender = users.value.find(u => u.id === message.from_user)
      if (sender) {
        sender.unreadCount = (sender.unreadCount || 0) + 1
      }
    }

    scrollToBottom()
  }

  ws.value.onclose = () => {
    console.log('WebSocket closed')
  }

  ws.value.onerror = (error) => {
    console.error('WebSocket error:', error)
    ElMessage.warning('聊天连接已断开，正在重新连接...')
    setTimeout(connectWebSocket, 1000)
  }
}

// 发送消息
const sendMessage = () => {
  if (!messageInput.value.trim() || !selectedUser.value) return

  const message = {
    type: 'message',
    content: messageInput.value,
    timestamp: new Date().toISOString(),
    to_user: selectedUser.value.id,
    from_user: currentUser.id
  }

  // 先添加到本地消息列表
  messages.value.push(message)

  // 发送到服务器
  ws.value.send(JSON.stringify(message))
  messageInput.value = ''
  scrollToBottom()
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 格式化时间
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleTimeString()
}

onMounted(() => {
  loadUsers()
  connectWebSocket()
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.message-container {
  scrollbar-width: thin;
  scrollbar-color: rgba(155, 155, 155, 0.5) transparent;
}

.message-container::-webkit-scrollbar {
  width: 6px;
}

.message-container::-webkit-scrollbar-track {
  background: transparent;
}

.message-container::-webkit-scrollbar-thumb {
  background-color: rgba(155, 155, 155, 0.5);
  border-radius: 3px;
}

.bg-primary {
  background-color: #409eff;
}
</style>
