<template>
  <nav class="fixed top-0 left-0 right-0 h-15 bg-white shadow-sm z-1000">
    <div class="w-full h-full px-5 flex items-center">
      <!-- 导航菜单 -->
      <div class="flex-1 flex justify-center">
        <el-menu
          :default-active="route.path"
          mode="horizontal"
          :ellipsis="false"
          class="border-none"
          router
        >
          <el-menu-item
            v-for="item in menuItems"
            :key="item.path"
            :index="item.path"
          >
            {{ item.name }}
          </el-menu-item>
        </el-menu>
      </div>
      
      <!-- 用户头像 -->
      <div class="fixed right-5">
        <el-dropdown trigger="hover" @command="handleCommand">
          <div class="flex items-center cursor-pointer">
            <el-avatar :size="32" :src="userStore.avatar || defaultAvatar" />
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout" divided>
                <div class="flex items-center gap-2">
                  <el-icon><Switch /></el-icon>
                  退出登录
                </div>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { Switch } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const stuMenu = [
  { name: '课程资料', path: '/' },
  { name: '练习', path: '/practice' },
  { name: '作业', path: '/homework' },
  { name: '学习统计', path: '/stat' },
  { name: '问答', path: '/chat' }
]

const teacherMenu = [
  { name: '课程资料', path: '/' },
  { name: '练习管理', path: '/practiceManage' },
  { name: '作业管理', path: '/homeworkManage' },
  { name: '学习统计', path: '/stat' },
  { name: '问答', path: '/chat' },
  { name: '系统管理', path: '/admin' }
]
const menuItems = userStore.isStudent() ? stuMenu : teacherMenu

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await userStore.clearUserInfo()
      ElMessage.success('退出登录成功')
      router.push('/login')
    } catch (error) {
      ElMessage.error('退出登录失败')
    }
  }
}
</script>

<style scoped>
:deep(.el-menu) {
  --el-menu-hover-bg-color: var(--el-fill-color-light);
}

:deep(.el-menu--horizontal .el-menu-item) {
  height: 60px;
  line-height: 60px;
  font-size: 1rem;
}
</style>
