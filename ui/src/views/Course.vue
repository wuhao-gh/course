<template>
  <div class="p-4">
    <!-- Filter Section -->
    <div class="mb-6">
      <!-- Categories -->
      <div class="mb-4">
        <h3 class="text-lg font-medium mb-2">Categories</h3>
        <div class="flex flex-wrap gap-2">
          <el-tag
            v-for="category in categories"
            :key="category"
            :type="selectedCategory === category ? '' : 'info'"
            class="cursor-pointer"
            @click="selectCategory(category)"
          >
            {{ category }}
          </el-tag>
        </div>
      </div>

      <!-- Tags -->
      <div>
        <h3 class="text-lg font-medium mb-2">Tags</h3>
        <div class="flex flex-wrap gap-2">
          <el-tag
            v-for="tag in tags"
            :key="tag"
            :type="selectedTags.includes(tag) ? '' : 'info'"
            class="cursor-pointer"
            @click="toggleTag(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </div>

    <!-- Video Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <el-card
        v-for="video in filteredVideos"
        :key="video.id"
        class="hover:shadow-lg transition-shadow duration-300"
      >
        <div class="aspect-video relative mb-2">
          <img :src="video.thumbnail" :alt="video.title" class="w-full h-full object-cover rounded">
          <div class="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 text-sm rounded">
            {{ video.duration }}
          </div>
        </div>
        <h3 class="text-lg font-medium mb-1">{{ video.title }}</h3>
        <p class="text-gray-600 text-sm mb-2">{{ video.description }}</p>
        <div class="flex flex-wrap gap-1">
          <el-tag size="small" type="success">{{ video.category }}</el-tag>
          <el-tag
            v-for="tag in video.tags"
            :key="tag"
            size="small"
            type="info"
          >
            {{ tag }}
          </el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Mock data - replace with actual API calls
const categories = ['Programming', 'Design', 'Business', 'Marketing']
const tags = ['Beginner', 'Intermediate', 'Advanced', 'Web', 'Mobile', 'AI', 'UI/UX']
const videos = [
  {
    id: 1,
    title: 'Introduction to Vue.js',
    description: 'Learn the basics of Vue.js framework',
    thumbnail: 'https://picsum.photos/400/225',
    duration: '12:34',
    category: 'Programming',
    tags: ['Beginner', 'Web']
  },
  {
    id: 2,
    title: 'Advanced UI Design',
    description: 'Master modern UI design principles',
    thumbnail: 'https://picsum.photos/400/225',
    duration: '25:10',
    category: 'Design',
    tags: ['Advanced', 'UI/UX']
  },
  // Add more video items as needed
]

const selectedCategory = ref('')
const selectedTags = ref([])

const selectCategory = (category) => {
  selectedCategory.value = selectedCategory.value === category ? '' : category
}

const toggleTag = (tag) => {
  const index = selectedTags.value.indexOf(tag)
  if (index === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

const filteredVideos = computed(() => {
  return videos.filter(video => {
    const categoryMatch = !selectedCategory.value || video.category === selectedCategory.value
    const tagsMatch = selectedTags.value.length === 0 || 
      selectedTags.value.every(tag => video.tags.includes(tag))
    return categoryMatch && tagsMatch
  })
})
</script>