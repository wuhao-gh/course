<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-6">练习列表</h2>
    
    <el-table :data="exercises" stripe class="w-full">
      <el-table-column prop="title" label="标题" min-width="180">
        <template #default="{ row }">
          <div class="flex items-center">
            <el-link type="primary" @click="showDetail(row)">
              {{ row.title }}
            </el-link>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="deadline" label="截止日期" width="160">
        <template #default="{ row }">
          <span>{{ formatDate(row.deadline) }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="120" align="center">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :disabled="row.status === '已完成'"
            @click="showUploadDialog(row)"
          >
            上传答案
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailVisible"
      title="练习详情"
      width="600px"
    >
      <template v-if="currentExercise">
        <div class="exercise-detail">
          <div class="mb-4">
            <h3 class="font-bold mb-2">标题</h3>
            <p>{{ currentExercise.title }}</p>
          </div>
          
          <div class="mb-4">
            <h3 class="font-bold mb-2">描述</h3>
            <p class="whitespace-pre-wrap">{{ currentExercise.description }}</p>
          </div>
          
          <div class="mb-4">
            <h3 class="font-bold mb-2">附件</h3>
            <div v-if="currentExercise.files && currentExercise.files.length">
              <div v-for="file in currentExercise.files" :key="file.name" class="mb-2">
                <el-button 
                  type="primary" 
                  link 
                  @click="downloadFile(file)"
                >
                  <el-icon class="mr-1"><Download /></el-icon>
                  {{ file.name }}
                </el-button>
              </div>
            </div>
            <p v-else class="text-gray-500">暂无附件</p>
          </div>
          
          <div class="mb-4">
            <h3 class="font-bold mb-2">截止日期</h3>
            <p>{{ formatDate(currentExercise.deadline) }}</p>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- Upload Dialog -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传答案"
      width="500px"
    >
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadRules"
        label-width="80px"
      >
        <el-form-item label="练习" class="mb-4">
          <span>{{ currentExercise?.title }}</span>
        </el-form-item>

        <el-form-item label="答案" prop="answer">
          <el-input
            v-model="uploadForm.answer"
            type="textarea"
            rows="6"
            placeholder="请输入你的答案"
          />
        </el-form-item>

        <el-form-item label="附件">
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitAnswer">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'

// Mock data - replace with actual API data
const exercises = ref([
  {
    id: 1,
    title: 'JavaScript 基础练习 - 变量和数据类型',
    description: '完成以下练习：\n1. 声明不同类型的变量\n2. 实现基本的类型转换\n3. 使用模板字符串\n4. 理解变量作用域',
    status: '未开始',
    deadline: '2024-12-20 23:59:59',
    files: [
      { name: '练习说明.pdf', url: '/files/js-basics.pdf' },
      { name: '示例代码.js', url: '/files/example.js' }
    ]
  },
  {
    id: 2,
    title: 'Vue.js 组件通信练习',
    description: '实现以下功能：\n1. 父子组件通信\n2. 兄弟组件通信\n3. 使用事件总线\n4. Provide/Inject 使用',
    status: '进行中',
    deadline: '2024-12-25 23:59:59',
    files: [
      { name: '项目模板.zip', url: '/files/vue-template.zip' }
    ]
  },
  {
    id: 3,
    title: 'CSS Flexbox 布局实战',
    description: '完成以下布局：\n1. 导航栏布局\n2. 卡片网格布局\n3. 响应式布局\n4. Flex 对齐方式练习',
    status: '已完成',
    deadline: '2024-12-15 23:59:59',
    files: [
      { name: '设计稿.fig', url: '/files/design.fig' },
      { name: 'HTML模板.html', url: '/files/template.html' }
    ]
  },
  {
    id: 4,
    title: 'Vue Router 导航守卫实践',
    status: '未开始',
    deadline: '2024-12-20 23:59:59',
    files: []
  },
  {
    id: 5,
    title: 'Vuex 状态管理练习',
    status: '已完成',
    deadline: '2024-12-15 23:59:59',
    files: []
  }
])

const detailVisible = ref(false)
const currentExercise = ref(null)

const showDetail = (exercise) => {
  currentExercise.value = exercise
  detailVisible.value = true
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const downloadFile = (file) => {
  // In a real application, this would trigger a file download
  // For now, we'll just show a message
  ElMessage.success(`开始下载文件：${file.name}`)
}

const getStatusType = (status) => {
  const types = {
    '未开始': 'info',
    '进行中': 'warning',
    '已完成': 'success'
  }
  return types[status] || 'info'
}

const uploadDialogVisible = ref(false)
const uploadFormRef = ref(null)
const uploadForm = ref({
  answer: '',
  files: []
})

const uploadRules = {
  answer: [
    { required: true, message: '请输入答案', trigger: 'blur' },
    { min: 10, message: '答案至少10个字符', trigger: 'blur' }
  ]
}

const showUploadDialog = (exercise) => {
  currentExercise.value = exercise
  uploadDialogVisible.value = true
  uploadForm.value = {
    answer: '',
    files: []
  }
}

const handleFileChange = (file) => {
  uploadForm.value.files.push(file)
}

const handleFileRemove = (file) => {
  const index = uploadForm.value.files.indexOf(file)
  if (index !== -1) {
    uploadForm.value.files.splice(index, 1)
  }
}

const submitAnswer = async () => {
  if (!uploadFormRef.value) return
  
  await uploadFormRef.value.validate((valid) => {
    if (valid) {
      // Here you would typically send the data to your backend
      ElMessage.success('答案提交成功！')
      uploadDialogVisible.value = false
      
      // Update exercise status
      if (currentExercise.value) {
        currentExercise.value.status = '已完成'
      }
    }
  })
}
</script>