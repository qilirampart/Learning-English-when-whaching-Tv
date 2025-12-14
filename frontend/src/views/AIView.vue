<template>
  <div class="h-[calc(100vh-140px)] flex flex-col">
    <div class="text-center mb-6">
      <h1 class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-fuchsia-600">
        AI 语境助手
      </h1>
      <p class="text-slate-500 text-sm">输入单词和剧名,AI 帮你深度解析剧情语境。</p>
    </div>

    <div class="flex-1 overflow-y-auto space-y-4 pr-2 mb-4 scrollbar-thin">
      <div class="flex gap-3">
        <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">AI</div>
        <div class="bg-white/80 border border-slate-100 p-4 rounded-2xl rounded-tl-none shadow-sm text-sm text-slate-700 max-w-[80%]">
          你好！遇到哪句台词看不懂了?告诉我单词和剧名,我来帮你分析。
        </div>
      </div>

      <div v-for="(msg, index) in messages" :key="index" class="flex gap-3" :class="{'flex-row-reverse': msg.role === 'user'}">

        <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
             :class="msg.role === 'user' ? 'bg-slate-900' : 'bg-gradient-to-br from-violet-500 to-fuchsia-500'">
             {{ msg.role === 'user' ? '我' : 'AI' }}
        </div>

        <div class="p-4 rounded-2xl shadow-sm text-sm max-w-[80%]"
             :class="msg.role === 'user'
                ? 'bg-slate-900 text-white rounded-tr-none'
                : 'bg-white/80 border border-slate-100 text-slate-700 rounded-tl-none'">

          <div v-if="msg.loading" class="flex space-x-2 items-center h-5">
             <div class="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce"></div>
             <div class="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce delay-100"></div>
             <div class="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce delay-200"></div>
          </div>
          <div v-else class="whitespace-pre-wrap leading-relaxed">{{ msg.content }}</div>
        </div>
      </div>
    </div>

    <div class="bg-white/80 backdrop-blur-xl border border-white/50 p-2 rounded-2xl shadow-lg shadow-indigo-500/10 flex flex-col gap-2">
      <div class="flex gap-2 px-2 pt-2">
        <input v-model="tvShow" type="text" placeholder="剧集 (如: Friends)" class="bg-slate-50 text-xs px-3 py-1.5 rounded-lg border-none focus:ring-1 focus:ring-violet-500 w-1/3">
      </div>

      <div class="flex items-center gap-2 p-2">
        <input
          v-model="inputWord"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="输入单词或句子..."
          class="flex-1 bg-transparent border-none focus:ring-0 text-slate-800 placeholder-slate-400 font-medium"
        >
        <button
          @click="sendMessage"
          :disabled="!inputWord || loading"
          class="bg-slate-900 text-white p-2 rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import request from '../utils/request';

const messages = ref([]);
const inputWord = ref('');
const tvShow = ref('');
const loading = ref(false);

const sendMessage = async () => {
  if (!inputWord.value || loading.value) return;

  const word = inputWord.value;
  const show = tvShow.value;

  // 1. 添加用户消息
  messages.value.push({ role: 'user', content: `${word} ${show ? '('+show+')' : ''}` });
  inputWord.value = '';

  // 2. 添加 AI loading 占位
  const aiMsgIndex = messages.value.push({ role: 'assistant', loading: true }) - 1;
  loading.value = true;

  try {
    // POST /api/ai/usage with extended timeout
    const res = await request.post('/ai/usage',
      { word, tv_show: show },
      { timeout: 60000 }  // 60秒超时，因为AI生成需要时间
    );

    console.log('[AI] 收到响应:', res);

    // 3. 替换为真实回复
    // 后端返回 {code: 200, data: {content: "...", word: "...", ...}}
    const content = res.data?.content || res.content;

    messages.value[aiMsgIndex] = {
      role: 'assistant',
      content: content || '暂无解析结果,请稍后再试。'
    };
  } catch (error) {
    console.error('[AI] 请求失败:', error);
    console.error('[AI] 错误详情:', error.response);

    messages.value[aiMsgIndex] = {
      role: 'assistant',
      content: `AI 服务暂时不可用: ${error.message || '请检查网络'}`
    };
  } finally {
    loading.value = false;
  }
};
</script>
