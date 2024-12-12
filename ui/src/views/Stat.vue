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
      />
    </div>
    
    <!-- User Watch Time Table -->
    <el-table 
      :data="filteredWatchStats" 
      stripe 
      class="w-full"
      :default-sort="{ prop: 'totalDuration', order: 'descending' }"
    >
      <el-table-column prop="userName" label="用户" min-width="120" />
      
      <el-table-column 
        v-for="category in categories" 
        :key="category"
        :prop="'duration.' + category"
        :label="category"
        min-width="120"
        sortable
      >
        <template #default="{ row }">
          {{ formatDuration(row.duration[category] || 0) }}
        </template>
      </el-table-column>

      <el-table-column prop="totalDuration" label="总时长" min-width="120" sortable>
        <template #default="{ row }">
          {{ formatDuration(calculateTotalDuration(row.duration)) }}
        </template>
      </el-table-column>
    </el-table>

    <!-- Summary Chart -->
    <div class="mt-8">
      <h3 class="text-xl font-semibold mb-4">分类观看时长分布</h3>
      <div class="h-80">
        <el-row :gutter="20">
          <el-col :span="12">
            <div ref="pieChartRef" class="h-full"></div>
          </el-col>
          <el-col :span="12">
            <div ref="barChartRef" class="h-full"></div>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'

const categories = ['前端开发', '后端开发', '数据库', 'UI设计', '项目管理']
const selectedCategory = ref('')
const dateRange = ref('')

// Mock data for user watch statistics
const watchStats = ref([
  {
    userName: '张三',
    duration: {
      '前端开发': 1800, // 秒
      '后端开发': 2400,
      '数据库': 1200,
      'UI设计': 900,
      '项目管理': 600
    }
  },
  {
    userName: '李四',
    duration: {
      '前端开发': 3600,
      '后端开发': 1800,
      '数据库': 2100,
      'UI设计': 1500,
      '项目管理': 1200
    }
  },
  {
    userName: '王五',
    duration: {
      '前端开发': 2700,
      '后端开发': 3000,
      '数据库': 1800,
      'UI设计': 2400,
      '项目管理': 900
    }
  }
])

// Computed property for filtered data
const filteredWatchStats = computed(() => {
  let result = watchStats.value

  if (selectedCategory.value) {
    result = result.filter(stat => 
      stat.duration[selectedCategory.value] > 0
    )
  }

  return result
})

// Format duration from seconds to hours and minutes
const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}小时${minutes}分钟`
}

// Calculate total duration for a user
const calculateTotalDuration = (durations) => {
  return Object.values(durations).reduce((sum, curr) => sum + curr, 0)
}

// Chart references
const pieChartRef = ref(null)
const barChartRef = ref(null)

// Initialize charts
onMounted(() => {
  const pieChart = echarts.init(pieChartRef.value)
  const barChart = echarts.init(barChartRef.value)

  // Calculate total duration by category
  const categoryData = categories.map(category => ({
    name: category,
    value: watchStats.value.reduce((sum, user) => 
      sum + (user.duration[category] || 0), 0
    )
  }))

  // Pie chart options
  pieChart.setOption({
    title: {
      text: '分类占比',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 秒 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: categoryData,
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

  // Bar chart options
  barChart.setOption({
    title: {
      text: '用户观看时长',
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
    xAxis: {
      type: 'category',
      data: watchStats.value.map(stat => stat.userName)
    },
    yAxis: {
      type: 'value',
      name: '时长（秒）'
    },
    series: categories.map(category => ({
      name: category,
      type: 'bar',
      stack: 'total',
      data: watchStats.value.map(stat => stat.duration[category] || 0)
    }))
  })

  // Handle window resize
  window.addEventListener('resize', () => {
    pieChart.resize()
    barChart.resize()
  })
})
</script>