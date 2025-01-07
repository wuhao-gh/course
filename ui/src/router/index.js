import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import Course from '@/views/Course.vue'
import Practice from '@/views/Practice.vue'
import { useUserStore } from '@/stores/user'
import Layout from "@/components/Layout.vue";
import PracticeManage from "@/views/PracticeManage.vue";


// 配置NProgress选项
NProgress.configure({
  easing: 'ease',
  speed: 500,
  showSpinner: false
})

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/',
      component: Layout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '/',
          name: 'home',
          component: Course,
          meta: { requiresAuth: true }
        },
        {
          path: '/practice',
          name: 'practice',
          component: Practice,
          meta: { requiresAuth: true }
        },
        {
          path: '/practiceManage',
          name: 'practiceManage',
          component: PracticeManage,
          meta: { requiresAuth: true }
        },
        {
          path: '/stat',
          name: 'stat',
          component: () => import('@/views/Statistics.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/homework',
          name: 'homework',
          component: () => import('@/views/Homework.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/homeworkManage',
          name: 'homeworkManage',
          component: () => import('@/views/HomeworkManage.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/chat',
          name: 'chat',
          component: () => import('@/views/Chat.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/admin',
          name: 'admin',
          component: () => import('@/views/Admin.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/homework/:id',
          name: 'HomeworkDetail',
          component: () => import('@/views/HomeworkDetail.vue'),
          meta: { requiresAuth: true }
        }
      ]
    },
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  NProgress.start()
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn()) {
    next('/login')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
