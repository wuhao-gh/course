<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-6">观看统计</h2>

    <!-- Filter Section -->
    <div class="mb-6 flex items-center gap-4">
      <el-select v-model="selectedCategory" placeholder="选择分类" clearable>
        <el-option
          v-for="cat in categories"
          :key="cat"
          :label="cat"
          :value="cat"
        />
      </el-select>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
      />
    </div>

    <!-- Watch Time Chart -->
    <div class="mb-8">
      <el-card>
        <template #header>
          <div class="flex justify-between items-center">
            <span>用户观看时长统计</span>
            <el-button type="primary" link @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        <div class="h-[400px]" ref="watchTimeChartRef"></div>
      </el-card>
    </div>

    <!-- Summary Charts -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="flex justify-between items-center">
              <span>分类观看时长分布</span>
            </div>
          </template>
          <div class="h-[300px]" ref="pieChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="flex justify-between items-center">
              <span>分类用户数分布</span>
            </div>
          </template>
          <div class="h-[300px]" ref="barChartRef"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Refresh } from '@element-plus/icons-vue'
import request from '@/api/request'

// 状态
const categories = ref(['前端开发', '后端开发', '数据库', 'UI设计', '项目管理'])
const selectedCategory = ref('')
const dateRange = ref('')
const watchStats = ref([])
const categoryStats = ref([])

// 图表引用
const watchTimeChartRef = ref(null)
const pieChartRef = ref(null)
const barChartRef = ref(null)
let watchTimeChart = null
let pieChart = null
let barChart = null

// 格式化时长
const formatDuration = (seconds) => {
  return (seconds / 3600).toFixed(1)
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const params = {}
    if (dateRange.value) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }

    const [overviewData, categoryData] = await Promise.all([
      request.get('/stats/overview', { params }),
      request.get('/stats/category', { params })
    ])

    watchStats.value = overviewData
    categoryStats.value = categoryData
    
    updateCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
    console.error(error)
  }
}

// 刷新数据
const refreshData = () => {
  fetchStats()
}

// 初始化观看时长图表
const initWatchTimeChart = () => {
  if (watchTimeChart) {
    watchTimeChart.dispose()
  }
  
  watchTimeChart = echarts.init(watchTimeChartRef.value)
  
  const users = watchStats.value.map(stat => `用户${stat.user_id}`)
  const allCategories = Array.from(
    new Set(
      watchStats.value.flatMap(stat => 
        Object.keys(stat.duration)
      )
    )
  )
  
  const series = allCategories.map(category => ({
    name: category,
    type: 'bar',
    stack: 'total',
    label: {
      show: true,
      formatter: '{c} h'
    },
    data: watchStats.value.map(stat => 
      formatDuration(stat.duration[category] || 0)
    )
  }))

  watchTimeChart.setOption({
    title: {
      text: '用户观看时长统计',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      top: '10%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: users
    },
    yAxis: {
      type: 'value',
      name: '时长（小时）'
    },
    series
  })
}

// 初始化饼图
const initPieChart = () => {
  if (pieChart) {
    pieChart.dispose()
  }
  
  pieChart = echarts.init(pieChartRef.value)
  
  const data = categoryStats.value.map(stat => ({
    name: stat.category,
    value: formatDuration(stat.total_duration)
  }))

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}h ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })
}

// 初始化柱状图
const initBarChart = () => {
  if (barChart) {
    barChart.dispose()
  }
  
  barChart = echarts.init(barChartRef.value)
  
  const data = categoryStats.value.map(stat => ({
    category: stat.category,
    userCount: stat.user_count,
    avgDuration: formatDuration(stat.avg_duration)
  }))

  barChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['用户数', '平均时长']
    },
    xAxis: {
      type: 'category',
      data: data.map(item => item.category)
    },
    yAxis: [
      {
        type: 'value',
        name: '用户数',
        position: 'left'
      },
      {
        type: 'value',
        name: '平均时长(h)',
        position: 'right'
      }
    ],
    series: [
      {
        name: '用户数',
        type: 'bar',
        data: data.map(item => item.userCount)
      },
      {
        name: '平均时长',
        type: 'line',
        yAxisIndex: 1,
        data: data.map(item => item.avgDuration)
      }
    ]
  })
}

// 更新所有图表
const updateCharts = () => {
  initWatchTimeChart()
  initPieChart()
  initBarChart()
}

// 监听窗口大小变化
const handleResize = () => {
  watchTimeChart?.resize()
  pieChart?.resize()
  barChart?.resize()
}

// 监听筛选条件变化
watch([selectedCategory, dateRange], () => {
  fetchStats()
})

// 组件挂载
onMounted(() => {
  fetchStats()
  window.addEventListener('resize', handleResize)
})

// 组件卸载
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  watchTimeChart?.dispose()
  pieChart?.dispose()
  barChart?.dispose()
})
</script>