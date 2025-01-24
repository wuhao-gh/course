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

      <el-table-column prop="created_at" label="发布时间" width="160">
        <template #default="{ row }">
          <span>{{ formatDate(row.created_at) }}</span>
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
            <h3 class="font-bold mb-2">发布时间</h3>
            <p>{{ formatDate(currentExercise.created_at) }}</p>
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
            :rows="6"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { formatDate } from '../utils/date'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { UploadFilled } from '@element-plus/icons-vue'
import request from '@/api/request'

const exercises = ref([])

// 获取练习列表
const fetchExercises = async () => {
  try {
    const data = await request.get('/practice')
    exercises.value = data
  } catch (error) {
    ElMessage.error('获取练习列表失败')
    console.error(error)
  }
}

// 在组件挂载时获取练习列表
onMounted(() => {
  fetchExercises()
})

const detailVisible = ref(false)
const currentExercise = ref(null)

const showDetail = async (exercise) => {
  try {
    const data = await request.get(`/practice/${exercise.id}`)
    currentExercise.value = data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取练习详情失败')
    console.error(error)
  }
}

// 下载文件
const downloadFile = async (file) => {
  try {
    const response = await request.get(`/practice/file/${file.id}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', file.file_name)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载文件失败')
    console.error(error)
  }
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
    { required: true, message: '请输入答案', trigger: 'blur' }
  ]
}

const showUploadDialog = (exercise) => {
  currentExercise.value = exercise
  uploadForm.value = {
    answer: '',
    files: []
  }
  uploadDialogVisible.value = true
}

const handleFileChange = (file) => {
  uploadForm.value.files.push(file.raw)
}

const handleFileRemove = (file) => {
  const index = uploadForm.value.files.findIndex(f => f === file.raw)
  if (index !== -1) {
    uploadForm.value.files.splice(index, 1)
  }
}

const submitAnswer = async () => {
  if (!uploadFormRef.value) return

  try {
    await uploadFormRef.value.validate()

    const formData = new FormData()
    formData.append('answer', uploadForm.value.answer)

    uploadForm.value.files.forEach(file => {
      formData.append('files', file)
    })

    await request.post(`/practice/${currentExercise.value.id}/submit`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    ElMessage.success('提交成功')
    uploadDialogVisible.value = false
    fetchExercises() // 刷新列表
  } catch (error) {
    if (error.name === 'ValidationError') {
      ElMessage.error('请填写必要信息')
    } else {
      ElMessage.error('提交失败')
      console.error(error)
    }
  }
}
</script>
