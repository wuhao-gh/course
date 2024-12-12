<template>
  <div class="admin-container p-4">
    <h2 class="text-2xl font-bold mb-4">系统管理</h2>
    
    <!-- User Table -->
    <el-table :data="userList" stripe style="width: 100%">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.status === '激活' ? 'success' : 'danger'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="role" label="角色">
        <template #default="{ row }">
          <el-tag :type="row.role === '教师' ? 'primary' : 'info'">
            {{ row.role }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            修改
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="修改用户信息"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="editForm"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="激活" value="激活" />
            <el-option label="禁用" value="禁用" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option label="教师" value="教师" />
            <el-option label="学生" value="学生" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// Mock user data
const userList = ref([
  {
    id: 1,
    name: '张老师',
    email: 'zhang@example.com',
    status: '激活',
    role: '教师'
  },
  {
    id: 2,
    name: '李同学',
    email: 'li@example.com',
    status: '激活',
    role: '学生'
  },
  {
    id: 3,
    name: '王同学',
    email: 'wang@example.com',
    status: '禁用',
    role: '学生'
  }
])

const dialogVisible = ref(false)
const editForm = ref({
  id: null,
  name: '',
  email: '',
  status: '',
  role: ''
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const handleEdit = (row) => {
  editForm.value = { ...row }
  dialogVisible.value = true
}

const handleSave = () => {
  const index = userList.value.findIndex(user => user.id === editForm.value.id)
  if (index !== -1) {
    userList.value[index] = { ...editForm.value }
    ElMessage.success('修改成功')
    dialogVisible.value = false
  }
}
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>