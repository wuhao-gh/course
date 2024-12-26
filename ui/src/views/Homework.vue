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

      <el-table-column label="上传人数" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.answer_count }}/{{ row.user_count }}</span>
        </template>
      </el-table-column>

      <el-table-column label="打分人数" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.score_count }}/{{ row.answer_count }}</span>
        </template>
      </el-table-column>
    </el-table>

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
          <el-input v-model="form.title" placeholder="请输入作业标题"/>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              placeholder="请输入作业描述"
          />
        </el-form-item>

        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker v-model="form.deadline" type="date" />
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
import {onMounted, ref} from 'vue'
import {ElMessage} from 'element-plus'
import request from '@/api/request'

// 作业列表
const homeworkList = ref([])

// 获取作业列表
const fetchHomeworkList = async () => {
  try {
    homeworkList.value = await request.get('/homework')
  } catch (error) {
    ElMessage.error('获取作业列表失败')
  }
}

const dialogVisible = ref(false)
const formRef = ref(null)
const form = ref({
  title: '',
  description: '',
  deadline: ''
})

// Form validation rules
const rules = {
  title: [
    {required: true, message: '请输入作业标题', trigger: 'blur'},
    {min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur'}
  ],
  description: [
    {required: true, message: '请输入作业描述', trigger: 'blur'}
  ],
  deadline: [
    {required: true, message: '请选择截止日期', trigger: 'blur'}
  ]
}

// Methods
const showUploadDialog = () => {
  dialogVisible.value = true
}

const cancelUpload = () => {
  dialogVisible.value = false
  resetForm()
}

const resetForm = () => {
  form.value = {
    title: '',
    description: ''
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const submitForm = async (formEl) => {
  if (!formEl) return

  await formEl.validate(async (valid) => {
    if (valid) {
      try {
        await request.post('/homework', form.value)

        ElMessage.success('作业发布成功')
        dialogVisible.value = false
        resetForm()
        // 刷新作业列表
        await fetchHomeworkList()
      } catch (error) {
        ElMessage.error('作业发布失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  await fetchHomeworkList()
})
</script>
