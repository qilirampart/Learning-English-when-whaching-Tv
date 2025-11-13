import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/query'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/query',
      name: 'query',
      component: () => import('../views/QueryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/words',
      name: 'words',
      component: () => import('../views/WordsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/learning',
      name: 'learning',
      component: () => import('../views/LearningView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('../views/StatisticsView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果没有初始化用户信息，先初始化
  if (authStore.token && !authStore.user) {
    await authStore.initialize()
  }

  // 需要登录的页面
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，跳转到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath } // 保存原始目标路径，登录后可以跳回
      })
    } else {
      next()
    }
  }
  // 游客页面（登录、注册）
  else if (to.meta.requiresGuest) {
    if (authStore.isAuthenticated) {
      // 已登录，跳转到首页
      next('/')
    } else {
      next()
    }
  }
  // 其他页面
  else {
    next()
  }
})

export default router

