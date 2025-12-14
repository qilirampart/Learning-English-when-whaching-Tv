<template>
  <div v-if="loading" class="flex justify-center py-20">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
  </div>

  <div v-else>
    <div class="mb-8 animate-fade-in-up">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h1 class="text-3xl font-extrabold text-slate-900">
            Hi, {{ user?.username || 'Learner' }} <span class="animate-pulse">✨</span>
          </h1>
          <p class="text-slate-500 mt-1">今天准备攻克哪部美剧?</p>
        </div>
      </div>

      <!-- 查询单词搜索框 -->
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-white p-6 shadow-sm">
        <div class="flex gap-3">
          <div class="relative flex-1">
            <input
              v-model="queryWord"
              @keyup.enter="handleQueryWord"
              type="text"
              placeholder="输入单词查询释义..."
              class="w-full pl-10 pr-4 py-3 rounded-xl bg-white border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm text-lg"
            >
            <span class="absolute left-3 top-4 text-slate-400">🔍</span>
          </div>
          <button
            @click="handleQueryWord"
            :disabled="!queryWord || queryLoading"
            class="px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-indigo-500/30"
          >
            <span v-if="queryLoading" class="animate-spin inline-block mr-2 border-2 border-white border-t-transparent rounded-full w-4 h-4"></span>
            {{ queryLoading ? '查询中...' : '查询' }}
          </button>
        </div>

        <!-- 查询结果 -->
        <div v-if="queryResult" class="mt-6 p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="text-2xl font-black text-slate-900">{{ queryResult.word }}</h3>
              <p class="text-slate-500 font-serif italic">{{ queryResult.phonetic || '/.../' }}</p>
            </div>
            <button
              @click="viewWordDetail"
              class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-bold hover:bg-indigo-700 transition-all"
            >
              查看详情
            </button>
          </div>
          <div class="space-y-3">
            <div>
              <span class="text-xs font-bold text-slate-500 uppercase">释义</span>
              <p class="text-lg font-medium text-slate-800 mt-1">{{ queryResult.translation }}</p>
            </div>
            <div v-if="queryResult.definition" class="pt-3 border-t border-indigo-200">
              <span class="text-xs font-bold text-slate-500 uppercase">英文释义</span>
              <p class="text-sm text-slate-600 mt-1">{{ queryResult.definition }}</p>
            </div>
            <div v-if="queryResult.examples && queryResult.examples.length > 0" class="pt-3 border-t border-indigo-200">
              <span class="text-xs font-bold text-slate-500 uppercase">例句</span>
              <div v-for="(example, idx) in queryResult.examples" :key="idx" class="mt-2 p-3 bg-white rounded-lg">
                <p class="text-sm text-slate-700">{{ example.sentence }}</p>
                <p class="text-xs text-slate-500 mt-1">{{ example.translation }}</p>
              </div>
            </div>
          </div>
          <div class="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-green-700 text-sm flex items-center gap-2">
              <span class="text-lg">✓</span>
              已自动保存到单词本
            </p>
          </div>
        </div>

        <!-- 查询错误提示 -->
        <div v-if="queryError" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl">
          <p class="text-red-600 text-sm">{{ queryError }}</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 auto-rows-[minmax(180px,auto)]">

      <div class="md:col-span-2 md:row-span-2 relative rounded-3xl overflow-hidden group cursor-pointer shadow-xl shadow-indigo-500/20">
        <img src="https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=2070&auto=format&fit=crop" class="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" alt="Cover">
        <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/60 to-transparent"></div>

        <div class="relative z-10 flex flex-col h-full justify-between p-8">
          <div class="flex justify-between items-start">
            <span class="bg-white/20 backdrop-blur-md border border-white/20 text-white text-xs font-bold px-3 py-1 rounded-full uppercase">当前焦点</span>
          </div>
          <div>
            <h2 class="text-4xl font-bold text-white mb-2 tracking-tight">英语学习</h2>
            <p class="text-slate-300 text-sm mb-6">
               今日查询 {{ stats.today_queries }} 次 • 已掌握 {{ stats.mastered }} 个
            </p>

            <div class="space-y-2">
              <div class="flex justify-between text-xs font-medium text-slate-300">
                <span>总体进度 ({{ stats.mastered }}/{{ stats.total_words }})</span>
                <span>{{ masteryPercentage }}%</span>
              </div>
              <div class="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden backdrop-blur-sm">
                <div class="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full shadow-[0_0_10px_rgba(167,139,250,0.5)]" :style="{ width: masteryPercentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm hover:shadow-lg transition-all group flex flex-col justify-center">
        <div class="flex justify-between items-start mb-4">
          <div class="w-12 h-12 rounded-2xl bg-orange-100 text-orange-600 flex items-center justify-center text-xl shadow-inner">🔥</div>
          <span class="text-xs font-bold text-slate-400 bg-slate-100 px-2 py-1 rounded">待复习</span>
        </div>
        <div class="text-3xl font-black text-slate-900">{{ stats.to_review || 0 }}</div>
        <div class="text-slate-500 text-sm mt-1 group-hover:text-orange-600 transition-colors">个单词等待复习</div>
        <button v-if="stats.to_review > 0" @click="$router.push('/learning')" class="mt-4 text-sm text-blue-600 font-bold hover:underline">开始复习 &rarr;</button>
      </div>

      <div class="bg-gradient-to-br from-violet-600 to-fuchsia-600 rounded-3xl p-6 shadow-lg shadow-violet-500/30 text-white relative overflow-hidden group cursor-pointer" @click="$router.push('/ai')">
        <div class="absolute -right-4 -top-4 w-24 h-24 bg-white/20 rounded-full blur-xl group-hover:bg-white/30 transition-all"></div>
        <div class="relative z-10 h-full flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-2">
              <span class="text-sm font-bold text-violet-100 uppercase">AI 助手</span>
            </div>
            <h3 class="text-xl font-bold leading-tight">台词看不懂?<br>一键深度解析。</h3>
          </div>
          <button class="bg-white text-violet-600 px-4 py-2 rounded-xl text-sm font-bold mt-4 shadow-lg hover:scale-105 transition-transform w-fit">
            问问 AI &rarr;
          </button>
        </div>
      </div>

      <div class="col-span-1 md:col-span-3 lg:col-span-4 flex justify-center">
        <div class="w-full md:w-2/3 lg:w-1/2 bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm flex flex-col justify-between">
           <div>
              <h3 class="font-bold text-slate-900">7天学习趋势</h3>
              <p class="text-xs text-slate-400">过去7天的活动情况</p>
           </div>
           <div class="flex items-end justify-between h-32 mt-4 gap-2">
              <div v-for="(count, idx) in stats.weekly_trend || []" :key="idx" class="w-full bg-indigo-100 rounded-t-lg relative group h-full flex flex-col justify-end">
                  <div
                      class="w-full bg-indigo-500 rounded-t-lg transition-all duration-500 hover:bg-indigo-600"
                      :style="{ height: Math.min((count / (maxTrend + 1)) * 100, 100) + '%' }"
                  ></div>
                  <span class="text-[10px] text-center text-slate-400 mt-1 absolute -bottom-5 left-0 right-0">D-{{7-idx}}</span>
              </div>
           </div>
        </div>
      </div>

      <div class="col-span-1 md:col-span-3 lg:col-span-4 flex justify-center">
        <div class="w-full md:w-2/3 lg:w-1/2 bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm">
        <div class="flex justify-between items-center mb-6">
          <h3 class="font-bold text-slate-900 text-lg">最近收录</h3>
          <span @click="$router.push('/library')" class="text-xs text-blue-600 font-medium cursor-pointer hover:underline">查看全部</span>
        </div>

        <div class="space-y-3">
          <div v-for="word in recentWords" :key="word.id" class="flex items-center justify-between p-3 rounded-2xl hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all cursor-pointer group">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm">
                 Lv.{{ word.learning_plan?.mastery_level || 0 }}
              </div>
              <div>
                <div class="font-bold text-slate-900 text-lg group-hover:text-blue-600 transition-colors">{{ word.word }}</div>
                <div class="text-xs text-slate-400">{{ word.translation }}</div>
              </div>
            </div>
            <span v-if="word.tv_shows && word.tv_shows.length" class="px-3 py-1 rounded-full bg-slate-100 text-slate-500 text-xs font-bold truncate max-w-[100px]">
                {{ word.tv_shows[0] }}
            </span>
          </div>

          <div v-if="recentWords.length === 0" class="text-center text-slate-400 py-4 text-sm">
              暂无查词记录,快去添加吧
          </div>
        </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import request from '../utils/request';

const auth = useAuthStore();
const router = useRouter();
const user = computed(() => auth.user);
const loading = ref(true);

const stats = ref({});
const recentWords = ref([]);

// 查询单词相关状态
const queryWord = ref('');
const queryResult = ref(null);
const queryError = ref('');
const queryLoading = ref(false);

// 计算掌握进度百分比
const masteryPercentage = computed(() => {
    if (!stats.value.total_words) return 0;
    return Math.round((stats.value.mastered / stats.value.total_words) * 100);
});

// 计算趋势图最大值用于归一化高度
const maxTrend = computed(() => {
    if(!stats.value.weekly_trend) return 10;
    return Math.max(...stats.value.weekly_trend, 10);
});

// 查询单词
const handleQueryWord = async () => {
  if (!queryWord.value.trim()) return;

  queryLoading.value = true;
  queryError.value = '';
  queryResult.value = null;

  try {
    // 调用查询接口 POST /api/words/query (会自动保存到单词本)
    const res = await request.post('/words/query', {
      word: queryWord.value.trim()
    });

    queryResult.value = res.data;

    // 刷新最近收录列表
    const listRes = await request.get('/words/list', {
      params: { page: 1, page_size: 4, order_by: 'time' }
    });
    recentWords.value = listRes.data.items;

    // 刷新统计数据
    const statsRes = await request.get('/statistics/overview');
    stats.value = statsRes.data;
  } catch (error) {
    queryError.value = error.response?.data?.message || error.message || '查询失败,请稍后重试';
  } finally {
    queryLoading.value = false;
  }
};

// 查看单词详情
const viewWordDetail = () => {
  if (!queryResult.value) return;
  router.push(`/words/${queryResult.value.id}`);
};

onMounted(async () => {
  try {
    // 并行请求后端数据
    const [statsRes, listRes] = await Promise.all([
      request.get('/statistics/overview'),       // 获取统计
      request.get('/words/list', { params: { page: 1, page_size: 4, order_by: 'time' } }) // 获取最近单词
    ]);

    stats.value = statsRes.data;
    recentWords.value = listRes.data.items;
  } catch (error) {
    console.error('Failed to fetch dashboard data', error);
  } finally {
    loading.value = false;
  }
});
</script>
