<template>
  <div class="min-h-screen relative overflow-hidden bg-slate-50 font-sans text-slate-800">

    <div class="fixed inset-0 -z-10 pointer-events-none">
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
      <div class="absolute top-0 right-[20%] w-[400px] h-[400px] bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
      <div class="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>
    </div>

    <nav class="sticky top-0 z-50 bg-white/70 backdrop-blur-xl border-b border-white/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center gap-2 cursor-pointer" @click="$router.push('/')">
            <div class="w-8 h-8 bg-gradient-to-br from-violet-600 to-indigo-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="15" x="2" y="7" rx="2" ry="2"/><polyline points="17 2 12 7 7 2"/></svg>
            </div>
            <span class="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">单词助手</span>
          </div>

          <div class="hidden md:flex space-x-1 items-center bg-slate-100/50 p-1 rounded-full border border-slate-200/50 backdrop-blur-sm">
            <router-link to="/dashboard" active-class="bg-white text-slate-900 shadow-sm" class="px-5 py-1.5 rounded-full text-sm font-semibold text-slate-500 transition-all">仪表盘</router-link>
            <router-link to="/library" active-class="bg-white text-slate-900 shadow-sm" class="px-5 py-1.5 rounded-full text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">单词库</router-link>
            <router-link to="/learning" active-class="bg-white text-slate-900 shadow-sm" class="px-5 py-1.5 rounded-full text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">学习计划</router-link>
          </div>

          <div class="flex items-center space-x-4">
            <button @click="logout" class="text-sm text-slate-500 hover:text-red-600 font-medium">退出</button>
            <div class="h-9 w-9 rounded-full bg-gradient-to-tr from-pink-400 to-orange-400 p-[2px]">
               <div class="h-full w-full rounded-full bg-white flex items-center justify-center font-bold text-slate-600 text-xs">User</div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
