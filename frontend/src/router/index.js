import { createRouter, createWebHistory } from 'vue-router';
import AppLayout from '../layouts/AppLayout.vue';
import LoginView from '../views/LoginView.vue';
import DashboardView from '../views/DashboardView.vue';
import LibraryView from '../views/LibraryView.vue';
import LearningView from '../views/LearningView.vue';
import AIView from '../views/AIView.vue';
import WordDetailView from '../views/WordDetailView.vue';

const routes = [
  {
    path: '/login',
    component: LoginView,
    meta: { public: true }
  },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      { path: 'library', component: LibraryView },
      { path: 'learning', component: LearningView }, // 学习计划/复习
      { path: 'ai', component: AIView },
      { path: 'words/:id', component: WordDetailView } // 单词详情页
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 简单的路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  if (!to.meta.public && !token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
