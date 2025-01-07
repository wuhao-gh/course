<template>
  <div class="p-4">
    <div class="mb-4">
      <h2 class="text-xl font-bold">我的作业</h2>
    </div>

    <!-- 作业列表 -->
    <el-table :data="homeworkList" border stripe>
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="created_at" label="发布时间" width="180">
        <template #default="{ row }">
          {{ row.created_at }}
        </template>
      </el-table-column>
      <el-table-column prop="deadline" label="截止时间" width="180">
        <template #default="{ row }">
          {{ row.deadline }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button 
            v-if="row.status === 'pending'"
            size="small" 
            type="primary" 
            @click="handleUpload(row)"
          >
            上传答案
          </el-button>
          <el-button
            size="small"
            type="info"
            @click="handleView(row)"
          >
            查看
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 上传答案对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传答案"
      width="500px"
    >
      <el-upload
        class="upload-demo"
        :action="'/api/homework/upload'"
        :headers="{ Authorization: 'Bearer ' + userStore.token }"
        :data="{ homework_id: currentHomework?.id }"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、Word、PPT 等格式文件，单个文件不超过 10MB
          </div>
        </template>
      </el-upload>
    </el-dialog>

    <!-- 查看作业详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="作业详情"
      width="600px"
    >
      <div class="homework-detail">
        <h3 class="text-lg font-bold mb-4">{{ currentHomework?.title }}</h3>
        
        <div class="mb-4">
          <div class="font-bold mb-2">作业要求：</div>
          <div class="whitespace-pre-wrap">{{ currentHomework?.description }}</div>
        </div>

        <template v-if="currentHomework?.answer">
          <div class="mb-4">
            <div class="font-bold mb-2">提交文件：</div>
            <el-link 
              :href="'/api/homework/download/' + currentHomework.answer.file_path"
              type="primary"
              target="_blank"
            >
              {{ currentHomework.answer.file_path }}
            </el-link>
          </div>

          <template v-if="currentHomework.status === 'graded'">
            <div class="mb-4">
              <div class="font-bold mb-2">得分：</div>
              <div class="text-xl text-orange-500">{{ currentHomework.answer.score }}</div>
            </div>

            <div v-if="currentHomework.answer.comment" class="mb-4">
              <div class="font-bold mb-2">评语：</div>
              <div class="whitespace-pre-wrap">{{ currentHomework.answer.comment }}</div>
            </div>
          </template>
        </template>

        <div v-else class="text-gray-500">
          暂未提交答案
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const homeworkList = ref([])
const uploadDialogVisible = ref(false)
const currentHomework = ref(null)
const viewDialogVisible = ref(false)



// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '未完成',
    submitted: '已上传',
    graded: '已打分'
  }
  return statusMap[status] || status
}

// 获取状态标签类型
const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    submitted: 'primary',
    graded: 'success'
  }
  return typeMap[status] || 'info'
}

// 获取作业列表
const fetchHomeworkList = async () => {
  try {
    const response = await request.get('/homework/student')
    homeworkList.value = response
  } catch (error) {
    console.error('获取作业列表失败:', error)
    ElMessage.error('获取作业列表失败')
  }
}

// 上传答案
const handleUpload = (row) => {
  currentHomework.value = row
  uploadDialogVisible.value = true
}

// 上传成功回调
const handleUploadSuccess = () => {
  ElMessage.success('上传成功')
  uploadDialogVisible.value = false
  fetchHomeworkList()
}

// 上传失败回调
const handleUploadError = () => {
  ElMessage.error('上传失败')
}

// 上传前检查
const beforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

// 查看作业详情
const handleView = (row) => {
  currentHomework.value = row
  viewDialogVisible.value = true
}

onMounted(() => {
  fetchHomeworkList()
})
</script>
