<template>
  <div class="p-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold mb-4">{{ homework.title }}</h2>
      
      <div class="bg-gray-50 p-4 rounded-lg">
        <div class="mb-4">
          <h3 class="font-bold mb-2">作业描述</h3>
          <p>{{ homework.description }}</p>
        </div>
        
        <div class="grid grid-cols-3 gap-4">
          <div>
            <span class="text-gray-600">截止日期：</span>
            {{ homework.deadline }}
          </div>
          <div>
            <span class="text-gray-600">状态：</span>
            <el-tag :type="getStatusType(homework.status)" size="small">
              {{ homework.status }}
            </el-tag>
          </div>
          <div>
            <span class="text-gray-600">提交情况：</span>
            {{ homework.submittedCount }}/{{ homework.totalCount }}
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6">
      <h3 class="text-xl font-bold mb-4">答案列表</h3>
      <el-table :data="answerList" stripe>
        <el-table-column prop="studentName" label="学生���名" />
        <el-table-column prop="submitTime" label="提交时间" />
        <el-table-column prop="score" label="分数" width="100">
          <template #default="{ row }">
            <span v-if="row.score">{{ row.score }}分</span>
            <span v-else class="text-gray-400">未打分</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small"
              @click="viewAnswer(row)"
            >
              查看答案
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const homework = ref({})
const answerList = ref([])

onMounted(async () => {
  // 这里应该调用API获取作业详情和答案列表
  // 以下为mock数据
  homework.value = {
    id: route.params.id,
    title: 'JavaScript 基础作业',
    description: '完成基础语法练习',
    status: '进行中',
    submittedCount: 15,
    totalCount: 30,
    deadline: '2024-12-20 23:59:59'
  }
  
  answerList.value = [
    {
      id: 1,
      studentName: '张三',
      submitTime: '2024-12-19 14:30:00',
      score: 95
    },
    {
      id: 2,
      studentName: '李四',
      submitTime: '2024-12-19 15:20:00',
      score: null
    }
  ]
})

const getStatusType = (status) => {
  const types = {
    '未开始': 'info',
    '进行中': 'warning',
    '已结束': 'success'
  }
  return types[status] || 'info'
}

const viewAnswer = (answer) => {
  // 实现查看答案的逻辑
  console.log('查看答案:', answer)
}
</script> 