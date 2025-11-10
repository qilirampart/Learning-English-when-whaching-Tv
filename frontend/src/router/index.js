import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/query'
    },
    {
      path: '/query',
      name: 'query',
      component: () => import('../views/QueryView.vue')
    },
    {
      path: '/words',
      name: 'words',
      component: () => import('../views/WordsView.vue')
    },
    {
      path: '/learning',
      name: 'learning',
      component: () => import('../views/LearningView.vue')
    },
    {
      path: '/statistics',
      name: 'statistics',
      component: () => import('../views/StatisticsView.vue')
    }
  ]
})

export default router

