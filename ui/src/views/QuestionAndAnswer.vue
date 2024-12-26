<template>
  <div class="flex flex-col h-[calc(100vh-60px)] p-4">
    <!-- 问题列表和创建问题按钮 -->
    <div class="flex justify-between items-center mb-4">
      <div class="flex gap-4">
        <el-input
          v-model="searchQuery"
          placeholder="搜索问题"
          prefix-icon="Search"
          class="w-64"
        />
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
          <el-option
            v-for="status in questionStatuses"
            :key="status.value"
            :label="status.label"
            :value="status.value"
          />
        </el-select>
      </div>
      <el-button type="primary" @click="showCreateQuestionDialog">
        提问
      </el-button>
    </div>

    <!-- 问题列表 -->
    <div class="flex-1 overflow-y-auto bg-white rounded-lg shadow">
      <div v-for="question in filteredQuestions" :key="question.id" class="p-4 border-b hover:bg-gray-50 cursor-pointer" @click="selectQuestion(question)">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <h3 class="text-lg font-medium mb-2">{{ question.title }}</h3>
            <p class="text-gray-600 line-clamp-2">{{ question.content }}</p>
          </div>
          <el-tag :type="getStatusType(question.status)" size="small">
            {{ question.status }}
          </el-tag>
        </div>
        <div class="flex gap-4 mt-2 text-sm text-gray-500">
          <span>提问者：{{ question.user_id }}</span>
          <span>回答数：{{ question.answers?.length || 0 }}</span>
          <span>{{ formatTime(question.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 创建问题对话框 -->
    <el-dialog
      v-model="createQuestionDialogVisible"
      title="提问"
      width="50%"
    >
      <el-form :model="newQuestion" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="newQuestion.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="newQuestion.content"
            type="textarea"
            :rows="4"
            placeholder="请详细描述你的问题"
          />
        </el-form-item>
        <el-form-item label="相关课程">
          <el-select v-model="newQuestion.course_id" placeholder="选择相关课程" clearable>
            <el-option
              v-for="course in courses"
              :key="course.id"
              :label="course.title"
              :value="course.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createQuestionDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createQuestion">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 问题详情对话框 -->
    <el-dialog
      v-if="selectedQuestion"
      v-model="questionDetailDialogVisible"
      :title="selectedQuestion.title"
      width="60%"
    >
      <div class="mb-4">
        <div class="text-gray-600 mb-4">{{ selectedQuestion.content }}</div>
        <div class="flex gap-4 text-sm text-gray-500">
          <span>提问者：{{ selectedQuestion.user_id }}</span>
          <span>{{ formatTime(selectedQuestion.created_at) }}</span>
        </div>
      </div>

      <div class="border-t pt-4">
        <h4 class="font-medium mb-4">回答</h4>
        <div v-if="selectedQuestion.answers?.length" class="space-y-4">
          <div
            v-for="answer in selectedQuestion.answers"
            :key="answer.id"
            class="p-4 bg-gray-50 rounded"
          >
            <div class="mb-2">{{ answer.content }}</div>
            <div class="flex justify-between items-center text-sm">
              <div class="text-gray-500">
                <span>回答者：{{ answer.user_id }}</span>
                <span class="ml-4">{{ formatTime(answer.created_at) }}</span>
              </div>
              <div v-if="answer.is_accepted" class="text-green-500">
                已采纳
              </div>
              <el-button
                v-else-if="selectedQuestion.user_id === currentUserId"
                type="primary"
                size="small"
                @click="acceptAnswer(answer.id)"
              >
                采纳
              </el-button>
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500 text-center py-4">
          暂无回答
        </div>

        <div class="mt-4" v-if="selectedQuestion.status !== 'CLOSED'">
          <el-input
            v-model="newAnswer"
            type="textarea"
            :rows="3"
            placeholder="写下你的回答..."
          />
          <div class="flex justify-end mt-2">
            <el-button type="primary" @click="submitAnswer">
              提交回答
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 状态和数据
const currentUserId = 1 // TODO: 从用户系统获取
const searchQuery = ref('')
const statusFilter = ref('')
const questions = ref([])
const courses = ref([])
const selectedQuestion = ref(null)
const createQuestionDialogVisible = ref(false)
const questionDetailDialogVisible = ref(false)
const newQuestion = ref({
  title: '',
  content: '',
  course_id: null
})
const newAnswer = ref('')

const questionStatuses = [
  { value: 'PENDING', label: '待回答' },
  { value: 'ANSWERED', label: '已回答' },
  { value: 'CLOSED', label: '已关闭' }
]

// 计算属性
const filteredQuestions = computed(() => {
  let result = questions.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(q =>
      q.title.toLowerCase().includes(query) ||
      q.content.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    result = result.filter(q => q.status === statusFilter.value)
  }

  return result
})

// 方法
const loadQuestions = async () => {
  try {
    const response = await axios.get('/api/qa/question')
    questions.value = response.data
  } catch (error) {
    ElMessage.error('加载问题列表失败')
  }
}

const loadCourses = async () => {
  try {
    const response = await axios.get('/api/course')
    courses.value = response.data
  } catch (error) {
    ElMessage.error('加载课程列表失败')
  }
}

const showCreateQuestionDialog = () => {
  newQuestion.value = {
    title: '',
    content: '',
    course_id: null
  }
  createQuestionDialogVisible.value = true
}

const createQuestion = async () => {
  try {
    const formData = new FormData()
    formData.append('title', newQuestion.value.title)
    formData.append('content', newQuestion.value.content)
    formData.append('user_id', currentUserId)
    if (newQuestion.value.course_id) {
      formData.append('course_id', newQuestion.value.course_id)
    }

    await axios.post('/api/qa/question', formData)
    ElMessage.success('提问成功')
    createQuestionDialogVisible.value = false
    loadQuestions()
  } catch (error) {
    ElMessage.error('提问失败')
  }
}

const selectQuestion = async (question) => {
  try {
    const response = await axios.get(`/api/qa/question/${question.id}`)
    selectedQuestion.value = response.data
    questionDetailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载问题详情失败')
  }
}

const submitAnswer = async () => {
  if (!newAnswer.value.trim()) {
    ElMessage.warning('请输入回答内容')
    return
  }

  try {
    const formData = new FormData()
    formData.append('content', newAnswer.value)
    formData.append('user_id', currentUserId)

    await axios.post(`/api/qa/question/${selectedQuestion.value.id}/answers`, formData)
    ElMessage.success('回答成功')
    newAnswer.value = ''
    selectQuestion(selectedQuestion.value)
  } catch (error) {
    ElMessage.error('提交回答失败')
  }
}

const acceptAnswer = async (answerId) => {
  try {
    await axios.put(`/api/qa/answers/${answerId}/accept`)
    ElMessage.success('已采纳回答')
    selectQuestion(selectedQuestion.value)
  } catch (error) {
    ElMessage.error('采纳回答失败')
  }
}

const getStatusType = (status) => {
  const types = {
    'PENDING': 'warning',
    'ANSWERED': 'success',
    'CLOSED': 'info'
  }
  return types[status] || 'default'
}

const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 初始化
loadQuestions()
loadCourses()
</script>
