<template>
  <div class="admin-container p-4">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">系统管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        创建用户
      </el-button>
    </div>

    <!-- 筛选器 -->
    <div class="mb-4 flex gap-4">
      <el-input
        v-model="searchQuery"
        placeholder="搜索用户"
        prefix-icon="Search"
        class="w-64"
        @input="filterUsers"
      />
      <el-select v-model="roleFilter" placeholder="角色筛选" clearable @change="filterUsers">
        <el-option
          v-for="role in roles"
          :key="role.value"
          :label="role.label"
          :value="role.value"
        />
      </el-select>
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="filterUsers">
        <el-option
          v-for="status in statuses"
          :key="status.value"
          :label="status.label"
          :value="status.value"
        />
      </el-select>
    </div>

    <!-- 用户表格 -->
    <el-table :data="filteredUsers" stripe style="width: 100%">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="role" label="角色">
        <template #default="{ row }">
          <el-tag :type="getRoleType(row.role)">
            {{ row.role }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="row.status === '激活' ? 'success' : 'danger'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)" class="mr-2">
            修改
          </el-button>
          <el-button
            :type="row.status === '激活' ? 'danger' : 'success'"
            size="small"
            @click="toggleUserStatus(row)"
          >
            {{ row.status === '激活' ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '修改用户信息' : '创建用户'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option
              v-for="role in roles"
              :key="role.value"
              :label="role.label"
              :value="role.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-select v-model="form.status" style="width: 100%">
            <el-option
              v-for="status in statuses"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 状态
const userList = ref([])
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = ref({
  id: null,
  name: '',
  email: '',
  password: '',
  role: '',
  status: '激活'
})

// 常量
const roles = [
  { value: 'teacher', label: '教师' },
  { value: 'student', label: '学生' }
]

const statuses = [
  { value: '激活', label: '激活' },
  { value: '禁用', label: '禁用' }
]

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 计算属性
const filteredUsers = computed(() => {
  let result = userList.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(user =>
      user.name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }

  if (roleFilter.value) {
    result = result.filter(user => user.role === roleFilter.value)
  }

  if (statusFilter.value) {
    result = result.filter(user => user.status === statusFilter.value)
  }

  return result
})

// 方法
const loadUsers = async () => {
  try {
    const response = await axios.get('/api/user')
    userList.value = response.data
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

const showCreateDialog = () => {
  isEdit.value = false
  form.value = {
    id: null,
    name: '',
    email: '',
    password: '',
    role: '',
    status: '激活'
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    if (isEdit.value) {
      await axios.put(`/api/user/${form.value.id}`, form.value)
      ElMessage.success('修改成功')
    } else {
      await axios.post('/api/user', form.value)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const toggleUserStatus = async (user) => {
  try {
    const newStatus = user.status === '激活' ? '禁用' : '激活'
    const formData = new FormData()
    formData.append('status', newStatus)

    await axios.put(`/api/user/${user.id}`, formData)
    ElMessage.success(`${newStatus}用户成功`)
    loadUsers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const getRoleType = (role) => {
  const types = {
    '教师': 'primary',
    '学生': 'info',
    '管理员': 'warning'
  }
  return types[role] || 'info'
}

const filterUsers = () => {
  // 触发计算属性重新计算
  userList.value = [...userList.value]
}

// 初始化
onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
