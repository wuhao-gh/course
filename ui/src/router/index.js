import { createRouter, createWebHistory } from 'vue-router'
import Course from '@/views/Course.vue'
import Practice from '@/views/Practice.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Course,
    },
    {
      path: '/practice',
      name: 'practice',
      component: Practice
    },
    {
      path: '/stat',
      name: 'stat',
      component: () => import('@/views/Stat.vue')
    },
    {
      path: '/homework',
      name: 'homework',
      component: () => import('@/views/Homework.vue')
    },
    {
      path: '/questionAndAnswer',
      name: 'questionAndAnswer',
      component: () => import('@/views/QuestionAndAnswer.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/Admin.vue')
    },
    {
      path: '/homework/:id',
      name: 'HomeworkDetail',
      component: () => import('@/views/HomeworkDetail.vue')
    }
  ]
})

export default router
