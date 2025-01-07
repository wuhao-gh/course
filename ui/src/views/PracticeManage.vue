
<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">练习管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        创建练习
      </el-button>
    </div>

    <!-- Practice List -->
    <el-table :data="practiceList" stripe class="w-full">
      <el-table-column prop="title" label="标题" min-width="180">
        <template #default="{ row }">
          <router-link
              :to="`/practice/${row.id}`"
              class="text-blue-500 cursor-pointer hover:text-blue-700"
          >
            {{ row.title }}
          </router-link>
        </template>
      </el-table-column>

      <el-table-column prop="type" label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.type === '选择题' ? 'success' : 'warning'">
            {{ row.type }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="完成人数" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.completed_count }}/{{ row.total_count }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="avg_score" label="平均分" width="120" align="center" />

      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <el-button-group>
            <el-button type="primary" link @click="editPractice(row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="deletePractice(row)">
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? '编辑练习' : '创建练习'"
        width="700px"
        :close-on-click-modal="false"
    >
      <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入练习标题"/>
        </el-form-item>

        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择练习类型">
            <el-option label="选择题" value="选择题" />
            <el-option label="编程题" value="编程题" />
          </el-select>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              placeholder="请输入练习描述"
          />
        </el-form-item>

        <template v-if="form.type === '选择题'">
          <el-form-item
              v-for="(option, index) in form.options"
              :key="index"
              :label="'选项' + String.fromCharCode(65 + index)"
              :prop="'options.' + index"
              :rules="{ required: true, message: '请输入选项内容', trigger: 'blur' }"
          >
            <div class="flex items-center gap-2">
              <el-input v-model="form.options[index]" placeholder="请输入选项内容" />
              <el-radio v-model="form.answer" :label="index">正确答案</el-radio>
              <el-button type="danger" circle @click="removeOption(index)">
                <el-icon><delete /></el-icon>
              </el-button>
            </div>
          </el-form-item>
          
          <el-button v-if="form.options.length < 6" type="primary" plain @click="addOption">
            添加选项
          </el-button>
        </template>

        <template v-else>
          <el-form-item label="参考答案" prop="reference">
            <el-input
                v-model="form.reference"
                type="textarea"
                :rows="6"
                placeholder="请输入参考答案"
            />
          </el-form-item>
        </template>

      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelDialog">取消</el-button>
          <el-button type="primary" @click="submitForm(formRef)">
            {{ isEdit ? '保存' : '创建' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import request from '@/api/request'

// 练习列表
const practiceList = ref([])

// 获取练习列表
const fetchPracticeList = async () => {
  try {
    practiceList.value = await request.get('/practice')
  } catch (error) {
    ElMessage.error('获取练习列表失败')
  }
}

const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const form = ref({
  title: '',
  type: '',
  description: '',
  options: ['', ''],  // 默认两个选项
  answer: 0,          // 选择题答案
  reference: ''       // 编程题参考答案
})

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入练习标题', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择练习类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入练习描述', trigger: 'blur' }
  ],
  reference: [
    { required: true, message: '请输入参考答案', trigger: 'blur' }
  ]
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogVisible.value = true
}

// 编辑练习
const editPractice = (practice) => {
  isEdit.value = true
  form.value = { ...practice }
  dialogVisible.value = true
}

// 删除练习
const deletePractice = async (practice) => {
  try {
    await ElMessageBox.confirm('确定要删除这个练习吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await request.delete(`/practice/${practice.id}`)
    ElMessage.success('删除成功')
    await fetchPracticeList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 添加选项
const addOption = () => {
  if (form.value.options.length < 6) {
    form.value.options.push('')
  }
}

// 移除选项
const removeOption = (index) => {
  if (form.value.options.length > 2) {
    form.value.options.splice(index, 1)
    // 如果删除的是正确答案，重置答案
    if (form.value.answer === index) {
      form.value.answer = 0
    }
    // 如果删除的选项在正确答案之前，需要调整答案索引
    else if (form.value.answer > index) {
      form.value.answer--
    }
  } else {
    ElMessage.warning('至少需要保留两个选项')
  }
}

// 取消对话框
const cancelDialog = () => {
  dialogVisible.value = false
  resetForm()
}

// 重置表单
const resetForm = () => {
  form.value = {
    title: '',
    type: '',
    description: '',
    options: ['', ''],
    answer: 0,
    reference: ''
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 提交表单
const submitForm = async (formEl) => {
  if (!formEl) return

  await formEl.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await request.put(`/practice/${form.value.id}`, form.value)
          ElMessage.success('更新成功')
        } else {
          await request.post('/practice', form.value)
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        resetForm()
        await fetchPracticeList()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  await fetchPracticeList()
})
</script>