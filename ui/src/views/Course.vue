<template>
  <div class="p-4">
    <!-- Filter Section -->
    <div class="mb-6 flex justify-between items-center">
      <div>
        <!-- Categories -->
        <div class="mb-4">
          <h3 class="text-lg font-medium mb-2">分类</h3>
          <div class="flex flex-wrap gap-2">
            <el-tag
                v-for="category in categories"
                :key="category"
                :type="selectedCategory === category ? 'success' : 'info'"
                class="cursor-pointer"
                @click="selectCategory(category)"
            >
              {{ category }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- Upload Button -->
      <el-button v-if="!isStudent" type="primary" @click="uploadDialogVisible = true">上传课程</el-button>
    </div>

    <!-- Upload Dialog -->
    <el-dialog
        v-model="uploadDialogVisible"
        title="上传课程"
        width="50%"
    >
      <el-form
          ref="uploadFormRef"
          :model="uploadForm"
          :rules="uploadRules"
          label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="uploadForm.title" placeholder="请输入课程标题"/>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
              v-model="uploadForm.description"
              type="textarea"
              placeholder="请输入课程描述"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select
              v-model="uploadForm.category"
              placeholder="请选择分类"
              filterable
              allow-create
              default-first-option
              @visible-change="handleSelectOpen"
          >
            <el-option
                v-for="category in categories"
                :key="category"
                :label="category"
                :value="category"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="文件" prop="file">
          <el-upload
              class="upload-demo"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              accept="video/*,.pdf"
          >
            <el-icon class="el-icon--upload">
              <upload-filled/>
            </el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="text-gray-400 mt-1">支持视频文件或 PDF 文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeUploadDialog">取消</el-button>
          <el-button type="primary" @click="handleSubmit">提交</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Course Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <el-card
          v-for="course in courses"
          :key="course.id"
          class="hover:shadow-lg transition-shadow duration-300"
      >
        <div class="aspect-video relative mb-2 group cursor-pointer" @click="playVideo(course)">
          <template v-if="course.file_path && isVideo(course.file_path)">
            <video
                :src="'/api/static/' + course.file_path"
                class="w-full h-full object-cover rounded"
                preload="metadata"
            ></video>
            <div class="absolute inset-0 bg-black bg-opacity-40 group-hover:bg-opacity-20 transition-opacity flex items-center justify-center">
              <el-icon class="text-white text-4xl opacity-80 group-hover:opacity-100 transition-opacity">
                <video-play />
              </el-icon>
            </div>
          </template>
          <template v-else>
            <img
                :alt="course.title"
                class="w-full h-full object-cover rounded"
            >
            <div class="absolute inset-0 bg-black bg-opacity-40 group-hover:bg-opacity-20 transition-opacity flex items-center justify-center">
              <el-icon class="text-white text-4xl opacity-80 group-hover:opacity-100 transition-opacity">
                <document />
              </el-icon>
            </div>
          </template>
          <div class="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 text-sm rounded">
            {{ course.duration || '00:00' }}
          </div>
        </div>
        <h3 class="text-lg font-medium mb-1">{{ course.title }}</h3>
        <p class="text-gray-600 text-sm mb-2">{{ course.description }}</p>
        <div class="flex flex-wrap gap-1 mb-2">
          <el-tag size="small" type="success">{{ course.category }}</el-tag>
        </div>
      </el-card>
    </div>
  </div>

  <!-- Video Player Dialog -->
  <el-dialog
      v-model="videoDialogVisible"
      width="80%"
      :title="selectedCourse?.title"
      destroy-on-close
      @close="stopVideo"
  >
    <video
        v-if="selectedCourse?.file_path && isVideo(selectedCourse.file_path)"
        ref="videoPlayer"
        :src="'/api/static/' + selectedCourse.file_path"
        class="w-full"
        controls
        autoplay
        @loadedmetadata="handleVideoLoaded"
        @timeupdate="handleTimeUpdate"
        @ended="handleVideoEnded"
    ></video>
    <iframe
        v-else-if="selectedCourse?.file_path?.endsWith('.pdf')"
        :src="'/api/static/' + selectedCourse.file_path"
        class="w-full h-[80vh]"
        frameborder="0"
    ></iframe>
  </el-dialog>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {ElMessage} from 'element-plus'
import {UploadFilled, VideoPlay, Document} from '@element-plus/icons-vue'
import request from '@/api/request'
import { useUserStore } from '@/stores/user'

// 状态管理
const categories = ref([])  // 将从后端获取
const courses = ref([])
const selectedCategory = ref('')
const uploadDialogVisible = ref(false)
const uploadFormRef = ref(null)

const uploadForm = ref({
  title: '',
  description: '',
  category: '',
  file: null
})

const uploadRules = {
  title: [{required: true, message: '请输入课程标题', trigger: 'blur'}],
  description: [{required: true, message: '请输入课程描述', trigger: 'blur'}],
  category: [{required: true, message: '请选择分类', trigger: 'change'}]
}

// 视频播放相关
const videoDialogVisible = ref(false)
const selectedCourse = ref(null)
const videoPlayer = ref(null)
const userStore = useUserStore()

const isStudent = userStore.isStudent()

const playVideo = async (course) => {
  selectedCourse.value = course
  videoDialogVisible.value = true

  // 获取上次播放进度
  try {
    const progress = await request.get(`/progress/${course.id}`, {
      params: { user_id: userStore.user.id }
    })
    if (progress) {
      // 恢复上次播放位置
      videoPlayer.value.currentTime = progress.current_time
      ElMessage.success(`已恢复至上次播放位置: ${Math.floor(progress.current_time)}秒`)
    }
  } catch (error) {
    console.error('获取播放进度失败:', error)
  }
}

const handleVideoLoaded = () => {
  if (selectedCourse.value && videoPlayer.value) {
    // 恢复上次播放位置
    videoPlayer.value.currentTime = selectedCourse.value.current_time
  }
}

const handleTimeUpdate = () => {
  if (!videoPlayer.value || !selectedCourse.value) return

  // 使用防抖，避免频繁保存
  setTimeout(async () => {
    const currentTime = videoPlayer.value.currentTime
    const duration = videoPlayer.value.duration
    const progress = (currentTime / duration) * 100

    try {
      await request.post('/progress', {
        course_id: selectedCourse.value.id,
        user_id: userStore.user.id,
        progress,
        current_time: currentTime,
        duration,
        is_completed: false
      })
    } catch (error) {
      console.error('保存播放进度失败:', error)
    }
  }, 5000) // 每 5 秒保存一次进度
}

const handleVideoEnded = async () => {
  if (!selectedCourse.value) return

  try {
    await request.post('/progress', {
      course_id: selectedCourse.value.id,
      user_id: userStore.user.id,
      progress: 100,
      current_time: videoPlayer.value.duration,
      duration: videoPlayer.value.duration,
      is_completed: true
    })
    ElMessage.success('课程已完成！')
  } catch (error) {
    console.error('保存播放进度失败:', error)
  }
}

const stopVideo = () => {
  if (videoPlayer.value) {
    videoPlayer.value.pause()
    videoPlayer.value.currentTime = 0
  }
  selectedCourse.value = null
}

// 获取课程列表
const fetchCourses = async () => {

  const params = {}
  if (selectedCategory.value) {
    params.category = selectedCategory.value
  }

  courses.value = await request.get('/course', {params})
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await request.get('/course/categories')
    categories.value = response
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

// 选择分类
const selectCategory = async (category) => {
  selectedCategory.value = selectedCategory.value === category ? '' : category
  await fetchCourses()
}

// 判断文件是否为视频
const isVideo = (filename) => {
  // 获取文件扩展名
  const ext = filename.split('.').pop().toLowerCase()
  // 常见视频格式列表
  const videoExts = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'm4v', 'mkv']
  return videoExts.includes(ext)
}

// 文件上传前检查
const handleFileChange = (file) => {
  const isLt100M = file.size / 1024 / 1024 < 100
  
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过 100MB!')
    return false
  }
  
  const fileName = file.name.toLowerCase()
  const isPdf = fileName.endsWith('.pdf')
  const isVideoFile = isVideo(fileName)
  
  if (!isPdf && !isVideoFile) {
    ElMessage.error('只能上传视频或 PDF 文件!')
    return false
  }
  
  uploadForm.value.file = file.raw
  return true
}

const handleFileRemove = () => {
  uploadForm.value.file = null
}

// 关闭上传对话框
const closeUploadDialog = () => {
  uploadDialogVisible.value = false
  uploadFormRef.value?.resetFields()
  uploadForm.value = {
    title: '',
    description: '',
    category: '',
    file: null
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!uploadFormRef.value) return

  try {
    await uploadFormRef.value.validate()

    const formData = new FormData()
    formData.append('title', uploadForm.value.title)
    formData.append('description', uploadForm.value.description)
    formData.append('category', uploadForm.value.category)

    if (uploadForm.value.file) {
      formData.append('file', uploadForm.value.file)
    }

    await request.post('/course', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    ElMessage.success('课程创建成功')
    closeUploadDialog()
    fetchCourses()
  } catch (error) {
    if (error.name === 'ValidationError') {
      ElMessage.error('请填写必要信息')
    } else {
      ElMessage.error('创建课程失败')
      console.error(error)
    }
  }
}

// 选择框打开时刷新分类列表
const handleSelectOpen = async (visible) => {
  if (visible) {
    await fetchCategories()
  }
}

// 初始化
onMounted(() => {
  fetchCategories()
  fetchCourses()
})
</script>
