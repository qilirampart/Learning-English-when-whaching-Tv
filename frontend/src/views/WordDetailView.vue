<template>
  <div v-if="loading" class="flex justify-center py-20">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
  </div>

  <div v-else-if="word" class="max-w-4xl mx-auto">
    <!-- 单词标题卡片 -->
    <div class="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl p-8 shadow-xl mb-6 text-white">
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <h1 class="text-5xl font-black mb-3">{{ word.word }}</h1>
          <div class="flex items-center gap-4">
            <span class="text-xl font-serif italic text-indigo-100">{{ word.phonetic || '/.../' }}</span>
            <button
              @click="playPronunciation"
              class="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all"
              title="播放发音"
            >
              <span class="text-2xl">🔊</span>
            </button>
          </div>
        </div>
        <div class="text-right">
          <div class="bg-white/20 backdrop-blur-md rounded-xl px-4 py-2 mb-2">
            <div class="text-xs text-indigo-100">掌握等级</div>
            <div class="text-3xl font-bold">Lv.{{ word.learning_plan?.mastery_level || 0 }}</div>
          </div>
          <div class="text-xs text-indigo-100 mt-2">查询 {{ word.query_count || 0 }} 次</div>
        </div>
      </div>
    </div>

    <!-- 中文释义 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm mb-6">
      <h2 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
        <span class="text-2xl">📖</span>
        中文释义
      </h2>
      <p class="text-2xl text-slate-800 font-medium">{{ word.translation }}</p>
    </div>

    <!-- 英文释义 -->
    <div v-if="word.definition" class="bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm mb-6">
      <h2 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
        <span class="text-2xl">📝</span>
        英文释义
      </h2>
      <p class="text-lg text-slate-700 leading-relaxed">{{ word.definition }}</p>
    </div>

    <!-- 例句列表 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm mb-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-bold text-slate-900 flex items-center gap-2">
          <span class="text-2xl">💬</span>
          例句 ({{ examples.length }})
        </h2>
        <button
          @click="showAIDialog = true"
          class="px-4 py-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-xl text-sm font-bold hover:shadow-lg transition-all"
        >
          AI 生成例句
        </button>
      </div>

      <div v-if="examples.length > 0" class="space-y-4">
        <div v-for="(example, idx) in examples" :key="idx"
             class="p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-indigo-200 transition-all">
          <p class="text-slate-800 mb-2 leading-relaxed">{{ example.sentence || example }}</p>
          <p v-if="example.translation" class="text-slate-500 text-sm">{{ example.translation }}</p>
        </div>
      </div>
      <div v-else class="text-center py-8 text-slate-400">
        暂无例句，点击上方按钮使用 AI 生成
      </div>
    </div>

    <!-- 来源标签 -->
    <div v-if="word.tv_shows && word.tv_shows.length > 0"
         class="bg-white/80 backdrop-blur-sm rounded-3xl border border-white p-6 shadow-sm">
      <h2 class="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
        <span class="text-2xl">🎬</span>
        来源
      </h2>
      <div class="flex flex-wrap gap-2">
        <span v-for="show in word.tv_shows" :key="show"
              class="px-4 py-2 bg-indigo-100 text-indigo-700 rounded-full text-sm font-bold">
          {{ show }}
        </span>
      </div>
    </div>

    <!-- AI 生成对话框 -->
    <div v-if="showAIDialog"
         class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
         @click.self="showAIDialog = false">
      <div class="bg-white rounded-3xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-slate-900">AI 生成例句</h3>
          <button @click="showAIDialog = false" class="text-slate-400 hover:text-slate-600">
            <span class="text-2xl">✕</span>
          </button>
        </div>

        <div v-if="aiLoading" class="flex flex-col items-center justify-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p class="text-slate-500">AI 正在生成例句...</p>
        </div>

        <div v-else-if="aiExamples.length > 0" class="space-y-4">
          <p class="text-slate-600 mb-4">AI 为你生成了以下例句，选择你想要添加的：</p>

          <div v-for="(example, idx) in aiExamples.slice(0, 3)" :key="idx"
               class="p-4 rounded-2xl border-2 transition-all cursor-pointer"
               :class="selectedExamples.includes(idx) ? 'border-indigo-500 bg-indigo-50' : 'border-slate-200 hover:border-indigo-300'"
               @click="toggleExample(idx)">
            <div class="flex items-start gap-3">
              <input type="checkbox" :checked="selectedExamples.includes(idx)" class="mt-1">
              <div class="flex-1">
                <p class="text-slate-800 mb-1">{{ example.sentence }}</p>
                <p class="text-slate-500 text-sm">{{ example.translation }}</p>
              </div>
            </div>
          </div>

          <div class="flex gap-3 mt-6">
            <button
              @click="showAIDialog = false"
              class="flex-1 px-6 py-3 border-2 border-slate-200 text-slate-600 rounded-xl font-bold hover:bg-slate-50 transition-all">
              取消
            </button>
            <button
              @click="addSelectedExamples"
              :disabled="selectedExamples.length === 0"
              class="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all">
              添加选中的例句 ({{ selectedExamples.length }})
            </button>
          </div>
        </div>

        <div v-else-if="aiError" class="text-center py-8">
          <p class="text-red-600 mb-4">{{ aiError }}</p>
          <button
            @click="generateAIExamples"
            class="px-6 py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all">
            重试
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-20">
    <p class="text-slate-500 text-lg">单词不存在</p>
    <button @click="$router.push('/dashboard')" class="mt-4 text-indigo-600 font-bold hover:underline">
      返回首页
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '../utils/request';

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const word = ref(null);
const showAIDialog = ref(false);
const aiLoading = ref(false);
const aiExamples = ref([]);
const aiError = ref('');
const selectedExamples = ref([]);

// 解析例句
const examples = computed(() => {
  if (!word.value) return [];

  try {
    if (typeof word.value.examples === 'string') {
      const parsed = JSON.parse(word.value.examples);
      return Array.isArray(parsed) ? parsed : [];
    }
    return Array.isArray(word.value.examples) ? word.value.examples : [];
  } catch (e) {
    return [];
  }
});

// 获取单词详情
const fetchWordDetail = async () => {
  try {
    const wordId = route.params.id;
    const res = await request.get(`/words/${wordId}`);
    word.value = res.data;
  } catch (error) {
    console.error('Failed to fetch word:', error);
  } finally {
    loading.value = false;
  }
};

// 播放发音
const playPronunciation = () => {
  if (!word.value) return;

  // 使用浏览器的 Web Speech API
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(word.value.word);
    utterance.lang = 'en-US';
    utterance.rate = 0.8;
    window.speechSynthesis.speak(utterance);
  } else {
    alert('你的浏览器不支持语音朗读功能');
  }
};

// 生成 AI 例句
const generateAIExamples = async () => {
  aiLoading.value = true;
  aiError.value = '';
  aiExamples.value = [];
  selectedExamples.value = [];

  try {
    const res = await request.post('/ai/examples',
      { word: word.value.word, count: 5 },
      { timeout: 60000 }
    );

    console.log('[AI Examples] Response:', res);

    if (res.data?.examples && Array.isArray(res.data.examples)) {
      aiExamples.value = res.data.examples;
    } else if (res.data?.content) {
      // 如果返回的是文本内容，尝试解析
      try {
        const parsed = JSON.parse(res.data.content);
        if (parsed.examples) {
          aiExamples.value = parsed.examples;
        }
      } catch {
        aiError.value = 'AI 返回的数据格式不正确';
      }
    } else {
      aiError.value = 'AI 生成失败，请重试';
    }
  } catch (error) {
    console.error('[AI Examples] Error:', error);
    aiError.value = error.response?.data?.message || 'AI 服务暂时不可用';
  } finally {
    aiLoading.value = false;
  }
};

// 切换例句选择
const toggleExample = (idx) => {
  const index = selectedExamples.value.indexOf(idx);
  if (index > -1) {
    selectedExamples.value.splice(index, 1);
  } else {
    selectedExamples.value.push(idx);
  }
};

// 添加选中的例句
const addSelectedExamples = async () => {
  if (selectedExamples.value.length === 0) return;

  try {
    const newExamples = selectedExamples.value.map(idx => aiExamples.value[idx]);

    // 合并现有例句和新例句
    const allExamples = [...examples.value, ...newExamples];

    // 更新单词例句
    await request.put(`/words/${word.value.id}`, {
      examples: JSON.stringify(allExamples)
    });

    // 重新获取单词详情
    await fetchWordDetail();

    // 关闭对话框
    showAIDialog.value = false;
    selectedExamples.value = [];
    aiExamples.value = [];
  } catch (error) {
    console.error('Failed to add examples:', error);
    alert('添加例句失败，请重试');
  }
};

// 监听对话框打开，自动生成例句
const handleDialogOpen = () => {
  if (showAIDialog.value && aiExamples.value.length === 0) {
    generateAIExamples();
  }
};

// 监听 showAIDialog 变化
import { watch } from 'vue';
watch(showAIDialog, (newVal) => {
  if (newVal) {
    handleDialogOpen();
  }
});

onMounted(fetchWordDetail);
</script>
