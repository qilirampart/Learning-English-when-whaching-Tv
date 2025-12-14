<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-slate-50">
    <div class="fixed inset-0 -z-10 pointer-events-none">
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
    </div>

    <div class="w-full max-w-md bg-white/70 backdrop-blur-xl border border-white/50 rounded-3xl shadow-2xl shadow-indigo-500/10 p-8 m-4 transform transition-all">
      <div class="text-center mb-8">
        <div class="w-12 h-12 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="20" height="15" x="2" y="7" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
        </div>
        <h2 class="text-2xl font-bold text-slate-900">{{ isLogin ? '欢迎回来' : '创建账户' }}</h2>
        <p class="text-slate-500 text-sm mt-2">美剧学英语,从这里开始</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">用户名</label>
          <input v-model="form.username" type="text" class="w-full px-4 py-3 rounded-xl bg-white/50 border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all outline-none" required placeholder="请输入用户名">
        </div>

        <div v-if="!isLogin">
          <label class="block text-sm font-medium text-slate-700 mb-1">邮箱</label>
          <input v-model="form.email" type="email" class="w-full px-4 py-3 rounded-xl bg-white/50 border border-slate-200 focus:ring-2 focus:ring-indigo-500 transition-all outline-none" placeholder="name@example.com">
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">密码</label>
          <input v-model="form.password" type="password" class="w-full px-4 py-3 rounded-xl bg-white/50 border border-slate-200 focus:ring-2 focus:ring-indigo-500 transition-all outline-none" required placeholder="••••••••">
        </div>

        <button type="submit" :disabled="loading" class="w-full py-3.5 rounded-xl bg-slate-900 text-white font-bold text-sm shadow-lg shadow-slate-900/20 hover:bg-slate-800 hover:scale-[1.02] active:scale-[0.98] transition-all flex justify-center items-center">
          <span v-if="loading" class="animate-spin mr-2 border-2 border-white border-t-transparent rounded-full w-4 h-4"></span>
          {{ isLogin ? '登录' : '注册' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-slate-500">
          {{ isLogin ? "还没有账户?" : "已有账户?" }}
          <button @click="toggleMode" class="text-indigo-600 font-bold hover:underline ml-1">
            {{ isLogin ? '立即注册' : '立即登录' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import request from '../utils/request';

const router = useRouter();
const authStore = useAuthStore();

const isLogin = ref(true);
const loading = ref(false);
const form = reactive({ username: '', password: '', email: '' });

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  form.username = ''; form.password = ''; form.email = '';
};

const handleSubmit = async () => {
  loading.value = true;
  try {
    if (isLogin.value) {
      // 登录逻辑
      await authStore.login(form.username, form.password);
      router.push('/dashboard');
    } else {
      // 注册逻辑:POST /api/auth/register
      await request.post('/auth/register', form);
      // 注册成功后直接登录或提示切换
      alert('注册成功,请登录');
      isLogin.value = true;
    }
  } catch (error) {
    alert(error.message || '操作失败');
  } finally {
    loading.value = false;
  }
};
</script>
