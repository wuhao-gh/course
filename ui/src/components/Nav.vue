<template>
  <nav class="fixed top-0 left-0 right-0 h-15 bg-white shadow-sm z-1000">
    <div class="max-w-1200px h-full mx-auto px-5 flex items-center justify-center">
      <div class="flex gap-12 items-center justify-center">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="text-gray-600 font-500 no-underline transition duration-200 hover:text-gray-800 text-lg"
        >
          {{ item.name }}
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
const menuItems = [
  { name: '课程资料', path: '/' },
  { name: '练习', path: '/practice' },
  { name: '学习统计', path: '/stat' },
  { name: '作业管理', path: '/homework' },
  { name: '问答', path: '/questionAndAnswer' },
  { name: '系统管理', path: '/admin' }
]
</script>

<style scoped>
/* Removed styles as they are now handled by UnoCSS utility classes */
</style>