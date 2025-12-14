<template>
  <div>
    <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">单词库</h1>
        <p class="text-slate-500 text-sm">已收录 {{ total }} 个单词</p>
      </div>

      <div class="flex gap-3 w-full md:w-auto">
        <div class="relative flex-1 md:w-64">
          <input v-model="searchQuery" @keyup.enter="handleSearch" type="text" placeholder="搜索单词..." class="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent shadow-sm">
          <span class="absolute left-3 top-3 text-slate-400">🔍</span>
        </div>
        <select v-model="filterShow" @change="fetchWords" class="px-4 py-2.5 rounded-xl bg-white border border-slate-200 text-slate-600 font-medium focus:ring-2 focus:ring-indigo-500">
          <option value="">全部剧集</option>
          <option value="Friends">老友记</option>
          <option value="Breaking Bad">绝命毒师</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="py-10 text-center text-slate-400">加载中...</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      <div v-for="word in words" :key="word.id"
           class="bg-white/80 backdrop-blur-sm border border-white rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group relative overflow-hidden cursor-pointer"
           @click="goToDetail(word.id)">
        <div class="absolute left-0 top-0 bottom-0 w-1.5" :class="getMasteryColor(word.learning_plan?.mastery_level)"></div>

        <div class="pl-3 flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <h3 class="text-xl font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">{{ word.word }}</h3>
              <button
                @click.stop="playPronunciation(word.word)"
                class="w-8 h-8 rounded-full bg-indigo-100 hover:bg-indigo-200 flex items-center justify-center transition-all opacity-0 group-hover:opacity-100"
                title="播放发音"
              >
                <span class="text-lg">🔊</span>
              </button>
            </div>
            <p class="text-slate-400 text-sm font-serif italic mb-2">{{ word.phonetic || '/.../' }}</p>
            <p class="text-slate-600 text-sm line-clamp-1">{{ word.translation }}</p>
          </div>
          <span v-if="word.tv_shows?.[0]" class="px-2 py-1 bg-slate-100 text-slate-500 text-[10px] font-bold uppercase rounded tracking-wider">
            {{ word.tv_shows[0] }}
          </span>
        </div>

        <div class="pl-3 mt-4 pt-3 border-t border-slate-100 flex justify-between items-center">
            <span class="text-xs text-slate-400">查询 {{ word.query_count }} 次</span>
            <span class="text-xs font-bold" :class="getMasteryTextColor(word.learning_plan?.mastery_level)">
                Lv.{{ word.learning_plan?.mastery_level || 0 }}
            </span>
        </div>
      </div>
    </div>

    <div class="mt-8 text-center" v-if="page < totalPages">
      <button @click="loadMore" class="px-6 py-2 bg-white text-slate-600 border border-slate-200 rounded-full text-sm font-medium hover:bg-slate-50 transition-colors">
        加载更多
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '../utils/request';

const router = useRouter();

const words = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const filterShow = ref('');
const page = ref(1);
const total = ref(0);
const totalPages = ref(1);

const fetchWords = async (isLoadMore = false) => {
  if (!isLoadMore) loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: 15,
      filter_show: filterShow.value || undefined,
      keyword: searchQuery.value || undefined
    };

    // 如果有搜索词,调用 search 接口,否则调用 list 接口
    const url = searchQuery.value ? '/words/search' : '/words/list';
    const res = await request.get(url, { params });

    // 适配 API 返回结构差异 (search 返回数组,list 返回 {items, total...})
    let newItems = [];
    if (searchQuery.value) {
        newItems = res.data; // Search returns list
        total.value = newItems.length;
    } else {
        newItems = res.data.items;
        total.value = res.data.total;
        totalPages.value = res.data.pages;
    }

    if (isLoadMore) {
      words.value = [...words.value, ...newItems];
    } else {
      words.value = newItems;
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => { page.value = 1; fetchWords(); };
const loadMore = () => { page.value++; fetchWords(true); };

const getMasteryColor = (level = 0) => {
  if (level >= 5) return 'bg-green-500';
  if (level >= 3) return 'bg-blue-500';
  if (level >= 1) return 'bg-yellow-400';
  return 'bg-slate-300';
};
const getMasteryTextColor = (level = 0) => {
    if (level >= 5) return 'text-green-600';
    if (level >= 3) return 'text-blue-600';
    return 'text-yellow-600';
};

// 跳转到单词详情页
const goToDetail = (wordId) => {
  router.push(`/words/${wordId}`);
};

// 播放发音
const playPronunciation = (word) => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(word);
    utterance.lang = 'en-US';
    utterance.rate = 0.8;
    window.speechSynthesis.speak(utterance);
  } else {
    alert('你的浏览器不支持语音朗读功能');
  }
};

onMounted(() => fetchWords());
</script>
