<template>
  <div class="flex h-[calc(100vh-60px)]">
    <!-- User List Sidebar -->
    <div class="w-64 border-r bg-gray-50">
      <div class="p-4">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户"
          prefix-icon="Search"
          class="mb-4"
        />
        <div class="overflow-y-auto">
          <div
            v-for="user in filteredUsers"
            :key="user.id"
            :class="[
              'p-3 flex items-center cursor-pointer hover:bg-gray-100 rounded',
              currentUser?.id === user.id ? 'bg-blue-50' : ''
            ]"
            @click="selectUser(user)"
          >
            <el-avatar :size="40" :src="user.avatar">
              {{ user.name.charAt(0) }}
            </el-avatar>
            <div class="ml-3">
              <div class="font-medium">{{ user.name }}</div>
              <div class="text-sm text-gray-500">{{ user.status }}</div>
            </div>
            <div v-if="user.unread" class="ml-auto">
              <el-badge :value="user.unread" class="mr-2" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Chat Header -->
      <div class="p-4 border-b flex items-center">
        <template v-if="currentUser">
          <el-avatar :size="40" :src="currentUser.avatar">
            {{ currentUser.name.charAt(0) }}
          </el-avatar>
          <div class="ml-3">
            <div class="font-medium">{{ currentUser.name }}</div>
            <div class="text-sm text-gray-500">{{ currentUser.status }}</div>
          </div>
        </template>
        <div v-else class="text-gray-500">
          选择一个用户开始聊天
        </div>
      </div>

      <!-- Messages Area -->
      <div class="flex-1 overflow-y-auto p-4" ref="messagesContainer">
        <template v-if="currentUser">
          <div
            v-for="message in currentChat"
            :key="message.id"
            :class="[
              'mb-4 flex',
              message.fromId === myId ? 'justify-end' : 'justify-start'
            ]"
          >
            <div
              :class="[
                'max-w-[70%] rounded-lg p-3',
                message.fromId === myId
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100'
              ]"
            >
              <div class="text-sm mb-1">
                {{ message.fromId === myId ? '我' : currentUser.name }}
              </div>
              <div>{{ message.content }}</div>
              <div class="text-xs mt-1 text-right" :class="[
                message.fromId === myId ? 'text-blue-100' : 'text-gray-500'
              ]">
                {{ formatTime(message.time) }}
              </div>
            </div>
          </div>
        </template>
        <div v-else class="h-full flex items-center justify-center text-gray-500">
          消息将在这里显示
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t p-4">
        <div class="flex">
          <el-input
            v-model="messageInput"
            placeholder="输入消息..."
            :disabled="!currentUser"
            @keyup.enter="sendMessage"
            class="mr-2"
          />
          <el-button
            type="primary"
            :disabled="!currentUser || !messageInput.trim()"
            @click="sendMessage"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

// Mock data
const myId = 'user1'
const users = ref([
  { id: 'user2', name: '张老师', status: '在线', avatar: '', unread: 2 },
  { id: 'user3', name: '李助教', status: '离线', avatar: '', unread: 0 },
  { id: 'user4', name: '王同学', status: '在线', avatar: '', unread: 5 },
])

const messages = ref({
  user2: [
    { id: 1, fromId: 'user2', content: '你好，有什么问题吗？', time: new Date(Date.now() - 3600000) },
    { id: 2, fromId: myId, content: '我想请教一个关于Vue的问题', time: new Date(Date.now() - 1800000) },
  ],
  user3: [
    { id: 1, fromId: 'user3', content: '作业已经批改完成', time: new Date(Date.now() - 86400000) },
  ],
  user4: []
})

const searchQuery = ref('')
const currentUser = ref(null)
const messageInput = ref('')
const messagesContainer = ref(null)

// Computed
const filteredUsers = computed(() => {
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.name.toLowerCase().includes(query) ||
    user.status.toLowerCase().includes(query)
  )
})

const currentChat = computed(() => {
  if (!currentUser.value) return []
  return messages.value[currentUser.value.id] || []
})

// Methods
const selectUser = (user) => {
  currentUser.value = user
  user.unread = 0 // Clear unread count
}

const sendMessage = async () => {
  if (!messageInput.value.trim() || !currentUser.value) return

  const newMessage = {
    id: Date.now(),
    fromId: myId,
    content: messageInput.value,
    time: new Date()
  }

  if (!messages.value[currentUser.value.id]) {
    messages.value[currentUser.value.id] = []
  }
  messages.value[currentUser.value.id].push(newMessage)
  messageInput.value = ''

  // Scroll to bottom after message is added
  await nextTick()
  scrollToBottom()
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// Watch for new messages and scroll to bottom
watch(currentChat, () => {
  nextTick(() => scrollToBottom())
})
</script>