<template>
  <div class="p-6">
    <div class="mb-6">
      <h2 class="text-2xl font-bold mb-4">{{ practice.title }}</h2>

      <div class="bg-gray-50 p-4 rounded-lg">
        <div class="mb-4">
          <h3 class="font-bold mb-2">练习描述</h3>
          <p>{{ practice.description }}</p>
        </div>

      </div>
    </div>

    <div class="mt-6">
      <h3 class="text-xl font-bold mb-4">答案列表</h3>
      <el-table :data="answerList" stripe>
        <el-table-column label="学生姓名">
          <template #default="{ row }">
            <span>{{ row.user.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
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

    <!-- 答案详情对话框 -->
    <el-dialog
      v-model="answerDialogVisible"
      title="答案详情"
      width="600px"
    >
      <div v-if="currentAnswer" class="answer-detail">
        <div class="mb-4">
          <div class="font-bold mb-2">学生信息：</div>
          <div>{{ currentAnswer.user.name }}</div>
        </div>

        <div class="mb-4">
          <div class="font-bold mb-2">提交时间：</div>
          <div>{{ currentAnswer.created_at }}</div>
        </div>

        <div class="mb-4">
          <div class="font-bold mb-2">答案文件：</div>
          <el-link 
            :href="'/api/practice/download/' + currentAnswer.file_path"
            type="primary"
            target="_blank"
          >
            {{ currentAnswer.file_path }}
          </el-link>
        </div>

        <el-form ref="scoreForm" :model="scoreForm" label-width="80px">
          <el-form-item label="分数">
            <el-input-number 
              v-model="scoreForm.score" 
              :min="0" 
              :max="100"
            />
          </el-form-item>
          <el-form-item label="评语">
            <el-input 
              v-model="scoreForm.comment"
              type="textarea"
              :rows="4"
              placeholder="请输入评语"
            />
          </el-form-item>
        </el-form>

        <div class="flex justify-center mt-4">
          <el-button type="primary" @click="handleSubmitScore">保存评分</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { formatDate } from '../utils/date'
import request from '@/api/request'

const route = useRoute()
const practice = ref({})
const answerList = ref([])
const answerDialogVisible = ref(false)
const currentAnswer = ref(null)
const scoreForm = ref({
  score: 0,
  comment: ''
})

// 获取练习详情
const fetchPracticeDetail = async () => {
  try {
    const data = await request.get(`/practice/${route.params.id}`)
    practice.value = data
  } catch (error) {
    ElMessage.error('获取练习详情失败')
  }
}

// 获取答案列表
const fetchAnswerList = async () => {
  try {
    answerList.value = await request.get(`/practice/${route.params.id}/answer`)
  } catch (error) {
    ElMessage.error('获取答案列表失败')
  }
}

// 查看答案详情
const viewAnswer = (answer) => {
  console.log(answer)
  currentAnswer.value = answer
  scoreForm.value.score = answer.score ?? 0
  scoreForm.value.comment = answer.comment ?? ''
  answerDialogVisible.value = true
  console.log(scoreForm.value.score)
  console.log(scoreForm.value.comment)
}

// 提交评分
const handleSubmitScore = async () => {
  try {
    await request.post(`/practice/answer/${currentAnswer.value.id}/score`, {
      score: scoreForm.value.score,
      comment: scoreForm.value.comment
    })
    
    ElMessage.success('评分成功')
    answerDialogVisible.value = false
    
    // 刷新答案列表
    await fetchAnswerList()
  } catch (error) {
    ElMessage.error('评分失败')
  }
}

onMounted(async () => {
  await fetchPracticeDetail()
  await fetchAnswerList()
})
</script>
