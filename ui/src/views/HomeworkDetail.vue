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
            <span class="text-gray-600">提交情况：</span>
            {{ homework.submittedCount }}/{{ homework.totalCount }}
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6">
      <h3 class="text-xl font-bold mb-4">答案列表</h3>
      <el-table :data="answerList" stripe>
        <el-table-column label="学生姓名" >
          <template #default="{ row }">
            <span> {{ row.user.name }} </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" />
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
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const route = useRoute()
const homework = ref({})
const answerList = ref([])

// 获取作业详情
const fetchHomeworkDetail = async () => {
  try {
    const data = await request.get(`/homework/${route.params.id}`)
    homework.value = data
  } catch (error) {
    ElMessage.error('获取作业详情失败')
  }
}

// 获取答案列表
const fetchAnswerList = async () => {
  try {
    answerList.value = await request.get(`/homework/${route.params.id}/answer`)
  } catch (error) {
    ElMessage.error('获取答案列表失败')
  }
}

// 查看答案详情
const viewAnswer = (answer) => {
  // TODO: 实现答案详情查看功能
  console.log('查看答案:', answer)
}

onMounted(async () => {
  await fetchHomeworkDetail()
  await fetchAnswerList()
})
</script>
