<template>
  <div class="p-4">
    <!-- 总体概览 -->
    <div class="mb-8" v-if="!isStudent">
      <h2 class="text-2xl font-bold mb-4">学习概览</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <el-card v-for="stat in overview" :key="stat.label">
          <div class="text-center">
            <div class="text-3xl font-bold mb-2">{{ stat.value }}</div>
            <div class="text-gray-500">{{ stat.label }}</div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 学习趋势 -->
    <div class="mb-8" v-if="!isStudent">
      <h2 class="text-2xl font-bold mb-4">学习趋势</h2>
      <el-card>
        <div ref="trendChart" class="h-80"></div>
      </el-card>
    </div>

    <!-- 个人学习统计 -->
    <div class="mb-8" v-if="userStore.user">
      <h2 class="text-2xl font-bold mb-4" v-if="isStudent">我的学习</h2>
      <template v-else>
        <h2 class="text-2xl font-bold mb-4">学生学习统计</h2>
        <el-select v-model="selectedStudentId" placeholder="选择学生" class="mb-4">
          <el-option
            v-for="student in studentList"
            :key="student.id"
            :label="student.name"
            :value="student.id"
          />
        </el-select>
      </template>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- 学习数据 -->
        <el-card>
          <template #header>
            <div class="font-bold">学习数据</div>
          </template>
          <div class="space-y-4">
            <div v-for="stat in userStats" :key="stat.label" class="flex justify-between items-center">
              <span class="text-gray-500">{{ stat.label }}</span>
              <span class="font-bold">{{ stat.value }}</span>
            </div>
          </div>
        </el-card>

        <!-- 最近学习 -->
        <el-card class="lg:col-span-2">
          <template #header>
            <div class="font-bold">最近学习</div>
          </template>
          <el-table :data="recentCourses" stripe>
            <el-table-column prop="title" label="课程名称" />
            <el-table-column prop="last_progress" label="学习进度">
              <template #default="{ row }">
                <el-progress :percentage="row.last_progress" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import request from '@/api/request'
import * as echarts from 'echarts'

const router = useRouter()
const userStore = useUserStore()
const trendChart = ref(null)
let chart = null

const isStudent = userStore.isStudent()
const selectedStudentId = ref(null)
const studentList = ref([])

// 总体概览数据
const overviewData = ref({
  total_courses: 0,
  total_learners: 0,
  total_hours: 0,
  completed_courses: 0
})

const overview = computed(() => [
  { label: '总课程数', value: overviewData.value.total_courses },
  { label: '学习人数', value: overviewData.value.total_learners },
  { label: '总学习时长', value: `${overviewData.value.total_hours}小时` },
  { label: '完成课程数', value: overviewData.value.completed_courses }
])

// 用户统计数据
const userStatsData = ref({
  course_count: 0,
  completed_count: 0,
  completion_rate: 0,
  total_time: 0,
  recent_courses: []
})

const userStats = computed(() => [
  { label: '学习课程数', value: userStatsData.value.course_count },
  { label: '完成课程数', value: userStatsData.value.completed_count },
  { label: '完成率', value: `${userStatsData.value.completion_rate}%` },
  { label: '总学习时长', value: `${userStatsData.value.total_time}小时` }
])

const recentCourses = computed(() => userStatsData.value.recent_courses)

// 获取总体概览数据
const fetchOverview = async () => {
  try {
    const res = await request.get('/progress/stats/overview')
    overviewData.value = res
  } catch (error) {
    console.error('获取概览数据失败:', error)
  }
}

// 获取趋势数据并绘制图表
const fetchTrend = async () => {
  try {
    const res = await request.get('/progress/stats/trend')
    renderTrendChart(res)
  } catch (error) {
    console.error('获取趋势数据失败:', error)
  }
}

// 获取学生列表
const fetchStudentList = async () => {
  try {
    const res = await request.get('/auth/students')
    studentList.value = res
    // 自动选择第一个学生
    if (res.length > 0 && !selectedStudentId.value) {
      selectedStudentId.value = res[0].id
    }
  } catch (error) {
    console.error('获取学生列表失败:', error)
  }
}

// 获取用户统计数据
const fetchUserStats = async () => {
  if (!userStore.user) return
  try {
    const userId = isStudent ? userStore.user.id : selectedStudentId.value
    const res = await request.get(`/progress/stats/user/${userId}`)
    userStatsData.value = res
  } catch (error) {
    console.error('获取用户统计数据失败:', error)
  }
}

// 监听选中学生变化
watch(selectedStudentId, () => {
  fetchUserStats()
})

// 绘制趋势图表
const renderTrendChart = (data) => {
  if (!trendChart.value) return

  const dates = [...new Set([
    ...data.daily_learners.map(d => d.date),
    ...data.daily_completions.map(d => d.date)
  ])].sort()

  const learnerData = dates.map(date => {
    const item = data.daily_learners.find(d => d.date === date)
    return item ? item.count : 0
  })

  const completionData = dates.map(date => {
    const item = data.daily_completions.find(d => d.date === date)
    return item ? item.count : 0
  })

  if (!chart) {
    chart = echarts.init(trendChart.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['每日学习人数', '每日完成课程数']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '每日学习人数',
        type: 'line',
        smooth: true,
        data: learnerData
      },
      {
        name: '每日完成课程数',
        type: 'line',
        smooth: true,
        data: completionData
      }
    ]
  }

  chart.setOption(option)
}

// 跳转到课程
const goToCourse = (courseId) => {
  router.push(`/course/${courseId}`)
}

// 监听窗口大小变化，调整图表大小
window.addEventListener('resize', () => {
  if (chart) {
    chart.resize()
  }
})

onMounted(() => {
  fetchOverview()
  fetchTrend()
  if (!isStudent) {
    fetchStudentList()
  } else {
    fetchUserStats()
  }
})
</script>
