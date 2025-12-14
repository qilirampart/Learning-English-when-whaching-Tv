<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6 flex items-center justify-between">
      <h2 class="text-xl font-bold text-slate-900">复习训练</h2>
      <span class="text-sm text-slate-500 font-medium">{{ currentIndex + 1 }} / {{ reviewQueue.length }}</span>
    </div>

    <div v-if="!loading && reviewQueue.length === 0" class="text-center py-20 bg-white/60 backdrop-blur rounded-3xl border border-white shadow-sm">
      <div class="text-6xl mb-4">🎉</div>
      <h3 class="text-2xl font-bold text-slate-900 mb-2">太棒了！全部完成！</h3>
      <p class="text-slate-500">今日待复习单词已全部完成。</p>
      <button @click="$router.push('/dashboard')" class="mt-6 px-6 py-2 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/30">返回首页</button>
    </div>

    <div v-else-if="currentWord" class="relative perspective-1000">

      <div class="w-full bg-white rounded-3xl shadow-xl shadow-indigo-500/10 border border-slate-100 overflow-hidden min-h-[400px] flex flex-col items-center justify-center p-8 transition-all duration-500 text-center relative">

        <div v-if="!showAnswer" class="animate-fade-in-up">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 block">单词</span>
          <h1 class="text-5xl font-black text-slate-900 mb-4">{{ currentWord.word }}</h1>
          <button @click="showAnswer = true" class="mt-8 px-8 py-3 bg-indigo-50 text-indigo-600 font-bold rounded-xl hover:bg-indigo-100 transition-colors">
            点击显示答案
          </button>
        </div>

        <div v-else class="w-full animate-fade-in text-left">
           <div class="text-center border-b border-slate-100 pb-6 mb-6">
              <h1 class="text-4xl font-black text-slate-900 mb-2">{{ currentWord.word }}</h1>
              <p class="text-slate-500 font-serif text-lg italic">{{ currentWord.phonetic }}</p>
           </div>

           <div class="space-y-4 px-4">
              <div>
                 <span class="text-xs font-bold text-slate-400 uppercase">释义</span>
                 <p class="text-xl font-medium text-slate-800">{{ currentWord.translation }}</p>
              </div>

              <div v-if="currentWord.definition" class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                 <span class="text-xs font-bold text-slate-400 uppercase">英文释义</span>
                 <p class="text-slate-600 text-sm mt-1">{{ currentWord.definition }}</p>
              </div>

              <div v-if="currentWord.learning_plan?.word_id" class="mt-4">
                 <span class="text-xs font-bold text-indigo-400 uppercase">语境</span>
                 <p class="text-sm text-slate-500 mt-1 italic">
                    "来自剧集..." (API需补充context字段)
                 </p>
              </div>
           </div>
        </div>
      </div>

      <div v-if="showAnswer" class="flex gap-4 mt-6 animate-fade-in-up">
        <button @click="submitReview(false)" class="flex-1 py-3 bg-red-50 text-red-600 font-bold rounded-xl border border-red-100 hover:bg-red-100 transition-colors">
          忘记了
        </button>
        <button @click="submitReview(true)" class="flex-1 py-3 bg-green-50 text-green-600 font-bold rounded-xl border border-green-100 hover:bg-green-100 transition-colors">
          记住了
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import request from '../utils/request';

const reviewQueue = ref([]);
const currentIndex = ref(0);
const loading = ref(true);
const showAnswer = ref(false);

const currentWord = computed(() => reviewQueue.value[currentIndex.value]);

const fetchTodayPlan = async () => {
  loading.value = true;
  try {
    const res = await request.get('/learning/today');
    reviewQueue.value = res.data.words || [];
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const submitReview = async (isCorrect) => {
  const word = currentWord.value;
  try {
    // POST /api/learning/review
    await request.post('/learning/review', {
      word_id: word.id,
      is_correct: isCorrect,
      time_spent: 5 // 简化的时间记录
    });

    // 切换到下一个
    showAnswer.value = false;
    if (currentIndex.value < reviewQueue.value.length) {
      currentIndex.value++;
    }
  } catch (e) {
    alert('提交失败');
  }
};

onMounted(fetchTodayPlan);
</script>
