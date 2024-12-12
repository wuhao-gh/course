<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">作业管理</h2>
      <el-button type="primary" @click="showUploadDialog">
        发布作业
      </el-button>
    </div>

    <!-- Homework List -->
    <el-table :data="homeworkList" stripe class="w-full">
      <el-table-column prop="title" label="标题" min-width="180">
        <template #default="{ row }">
          <router-link 
            :to="`/homework/${row.id}`" 
            class="text-blue-500 cursor-pointer hover:text-blue-700"
          >
            {{ row.title }}
          </router-link>
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="上传人数" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.submittedCount }}/{{ row.totalCount }}</span>
        </template>
      </el-table-column>

      <el-table-column label="打分人数" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.gradedCount }}/{{ row.submittedCount }}</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- Upload Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="发布作业"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入作业标题" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            rows="4"
            placeholder="请输入作业描述"
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
        
        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker
            v-model="form.deadline"
            type="datetime"
            placeholder="选择截止日期"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            :disabled-date="disabledDate"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelUpload">取消</el-button>
          <el-button type="primary" @click="submitForm(formRef)">
            发布
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Mock data
const homeworkList = ref([
  {
    id: 1,
    title: 'JavaScript 基础作业',
    description: '完成基础语法练习',
    status: '进行中',
    submittedCount: 15,
    totalCount: 30,
    gradedCount: 10,
    deadline: '2024-12-20 23:59:59'
  },
  {
    id: 2,
    title: 'Vue 组件开发作业',
    description: '创建一个可复用的组件',
    status: '未开始',
    submittedCount: 0,
    totalCount: 30,
    gradedCount: 0,
    deadline: '2024-12-25 23:59:59'
  }
])

const dialogVisible = ref(false)
const formRef = ref(null)
const form = ref({
  title: '',
  description: '',
  deadline: '',
  files: []
})

// Form validation rules
const rules = {
  title: [
    { required: true, message: '请输入作业标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入作业描述', trigger: 'blur' }
  ],
  deadline: [
    { required: true, message: '请选择截止日期', trigger: 'change' }
  ]
}

// Methods
const showUploadDialog = () => {
  dialogVisible.value = true
}

const handleFileChange = (file) => {
  form.value.files.push(file)
}

const handleFileRemove = (file) => {
  const index = form.value.files.indexOf(file)
  if (index !== -1) {
    form.value.files.splice(index, 1)
  }
}

const disabledDate = (time) => {
  return time.getTime() < Date.now()
}

const cancelUpload = () => {
  ElMessageBox.confirm(
    '确认取消发布作业？已填写的内容将会丢失',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      dialogVisible.value = false
      resetForm()
    })
    .catch(() => {})
}

const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    deadline: '',
    files: []
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const submitForm = async (formEl) => {
  if (!formEl) return
  
  await formEl.validate((valid) => {
    if (valid) {
      // Mock API call
      const newHomework = {
        id: Date.now(),
        title: form.value.title,
        description: form.value.description,
        status: '未开始',
        submittedCount: 0,
        totalCount: 30,
        gradedCount: 0,
        deadline: form.value.deadline
      }
      
      homeworkList.value.unshift(newHomework)
      ElMessage.success('作业发布成功')
      dialogVisible.value = false
      resetForm()
    }
  })
}

const getStatusType = (status) => {
  const types = {
    '未开始': 'info',
    '进行中': 'warning',
    '已结束': 'success'
  }
  return types[status] || 'info'
}
</script>