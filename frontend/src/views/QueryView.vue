<template>
  <div class="query-view">
    <el-card class="query-card">
      <h1 class="title">📖 快速查询单词</h1>
      <p class="subtitle">输入你在观看美剧时遇到的单词，系统会自动记录并加入学习计划</p>
      
      <!-- 查询输入框 -->
      <div class="search-box">
        <el-input
          v-model="searchWord"
          placeholder="输入要查询的单词..."
          size="large"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button 
              type="primary" 
              :icon="Search"
              :loading="loading"
              @click="handleSearch"
            >
              查询
            </el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 查询结果 -->
      <div v-if="wordResult" class="result-container">
        <el-card class="result-card">
          <div class="word-header">
            <div class="word-title-group">
              <h2 class="word-text">{{ wordResult.word }}</h2>
              <span v-if="wordResult.phonetic" class="phonetic">{{ wordResult.phonetic }}</span>
            </div>
            <div class="pronunciation-controls">
              <el-tooltip content="播放发音 (空格键)" placement="top">
                <el-button
                  :icon="isSpeaking ? VideoPlay : Microphone"
                  :type="isSpeaking ? 'success' : 'primary'"
                  :loading="isSpeaking"
                  circle
                  @click="handleSpeak"
                />
              </el-tooltip>
              <el-dropdown trigger="click" @command="handleSpeechCommand">
                <el-button :icon="Setting" circle />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item divided disabled>播放速度</el-dropdown-item>
                    <el-dropdown-item :command="{type: 'rate', value: 'slow'}">
                      慢速 {{ currentRate === 'slow' ? '✓' : '' }}
                    </el-dropdown-item>
                    <el-dropdown-item :command="{type: 'rate', value: 'normal'}">
                      正常 {{ currentRate === 'normal' ? '✓' : '' }}
                    </el-dropdown-item>
                    <el-dropdown-item :command="{type: 'rate', value: 'fast'}">
                      快速 {{ currentRate === 'fast' ? '✓' : '' }}
                    </el-dropdown-item>
                    <el-dropdown-item divided disabled>口音选择</el-dropdown-item>
                    <el-dropdown-item :command="{type: 'accent', value: 'US'}">
                      美式英语 {{ currentAccent === 'US' ? '✓' : '' }}
                    </el-dropdown-item>
                    <el-dropdown-item :command="{type: 'accent', value: 'GB'}">
                      英式英语 {{ currentAccent === 'GB' ? '✓' : '' }}
                    </el-dropdown-item>
                    <el-dropdown-item :command="{type: 'accent', value: 'AU'}">
                      澳式英语 {{ currentAccent === 'AU' ? '✓' : '' }}
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          
          <el-divider />
          
          <div class="word-content">
            <div class="translation-section">
              <h3>🔤 中文释义</h3>
              <p class="translation">{{ wordResult.translation }}</p>
            </div>
            
            <div v-if="wordResult.definition" class="definition-section">
              <h3>📝 英文释义</h3>
              <p class="definition">{{ wordResult.definition }}</p>
            </div>
            
            <div v-if="wordResult.examples && wordResult.examples.length" class="examples-section">
              <h3>💡 例句</h3>
              <ul class="examples-list">
                <li v-for="(example, index) in wordResult.examples" :key="index">
                  {{ example }}
                </li>
              </ul>
            </div>
          </div>
          
          <el-divider />
          
          <!-- 情境信息表单 -->
          <div class="context-form">
            <h3>📺 添加剧情信息（可选）</h3>
            <el-form :model="contextForm" label-width="100px">
              <el-form-item label="剧名">
                <el-input v-model="contextForm.tv_show" placeholder="如：老友记" />
              </el-form-item>
              <el-form-item label="集数">
                <el-input v-model="contextForm.season_episode" placeholder="如：S01E01" />
              </el-form-item>
              <el-form-item label="剧情备注">
                <el-input
                  v-model="contextForm.context_note"
                  type="textarea"
                  :rows="3"
                  placeholder="记录这个单词出现的场景，帮助你回忆..."
                />
              </el-form-item>
            </el-form>
          </div>
          
          <div class="word-stats">
            <el-tag type="info">查询次数: {{ wordResult.query_count }}</el-tag>
            <el-tag v-if="wordResult.last_query" type="success">
              最后查询: {{ formatDate(wordResult.last_query) }}
            </el-tag>
          </div>
        </el-card>
      </div>
      
      <!-- 最近查询 -->
      <div v-if="recentQueries.length" class="recent-queries">
        <h3>🕒 最近查询</h3>
        <div class="recent-list">
          <el-tag
            v-for="word in recentQueries"
            :key="word.id"
            class="recent-tag"
            @click="quickQuery(word.word)"
          >
            {{ word.word }}
          </el-tag>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Search, Microphone, VideoPlay, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { wordApi } from '@/api'
import { useWordStore } from '@/stores/word'
import { useSpeech } from '@/utils/useSpeech'

const wordStore = useWordStore()

// 发音功能
const { speak, isSpeaking, currentAccent, currentRate, setAccent, setRate } = useSpeech()

const searchWord = ref('')
const wordResult = ref(null)
const loading = ref(false)
const contextForm = ref({
  tv_show: '',
  season_episode: '',
  context_note: ''
})

const recentQueries = computed(() => wordStore.recentQueries)

// 查询单词
const handleSearch = async () => {
  if (!searchWord.value.trim()) {
    ElMessage.warning('请输入要查询的单词')
    return
  }
  
  loading.value = true
  
  try {
    const response = await wordApi.query({
      word: searchWord.value.trim(),
      ...contextForm.value
    })
    
    if (response.code === 200) {
      wordResult.value = response.data
      wordStore.addRecentQuery(response.data)
      ElMessage.success('查询成功！已自动加入学习计划')
      
      // 清空情境表单
      contextForm.value = {
        tv_show: '',
        season_episode: '',
        context_note: ''
      }
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

// 快速查询
const quickQuery = (word) => {
  searchWord.value = word
  handleSearch()
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 播放发音
const handleSpeak = () => {
  if (wordResult.value && wordResult.value.word) {
    speak(wordResult.value.word)
  }
}

// 处理发音设置命令
const handleSpeechCommand = (command) => {
  if (command.type === 'rate') {
    setRate(command.value)
    const rateText = { slow: '慢速', normal: '正常', fast: '快速' }[command.value]
    ElMessage.success(`已切换到${rateText}播放`)
  } else if (command.type === 'accent') {
    setAccent(command.value)
    const accentText = { US: '美式英语', GB: '英式英语', AU: '澳式英语' }[command.value]
    ElMessage.success(`已切换到${accentText}`)
  }
}

// 监听键盘事件（空格键播放发音）
const handleKeydown = (event) => {
  if (event.code === 'Space' && wordResult.value && !event.target.matches('input, textarea')) {
    event.preventDefault()
    handleSpeak()
  }
}

// 组件挂载和卸载时添加/移除事件监听
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.query-view {
  max-width: 1000px;
  margin: 0 auto;
  animation: fade-in-up 0.6s ease-out;
}

.query-card {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  padding: 40px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.query-card:hover {
  box-shadow: 0 12px 48px rgba(31, 38, 135, 0.25);
  transform: translateY(-2px);
}

.title {
  font-size: 42px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
  font-weight: 800;
  letter-spacing: -1px;
}

.subtitle {
  text-align: center;
  color: var(--app-text-secondary, #909399);
  margin-bottom: 40px;
  font-size: 16px;
  line-height: 1.6;
}

.search-box {
  margin-bottom: 40px;
}

.search-box :deep(.el-input) {
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
}

.search-box :deep(.el-input:hover) {
  box-shadow: 0 6px 28px rgba(102, 126, 234, 0.25);
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 16px;
  padding: 8px 16px;
  box-shadow: none;
  background: rgba(255, 255, 255, 0.8);
}

.search-box :deep(.el-input-group__append) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: none;
}

.search-box :deep(.el-input-group__append .el-button) {
  background: transparent;
  border: none;
  color: white;
  font-weight: 600;
  padding: 0 24px;
}

.result-container {
  margin-top: 40px;
  animation: fade-in-up 0.6s ease-out 0.2s both;
}

.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 24px;
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.result-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 8s ease-in-out infinite;
}

.word-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 15px;
  position: relative;
  z-index: 1;
}

.word-title-group {
  display: flex;
  align-items: baseline;
  gap: 20px;
  flex: 1;
}

.word-text {
  font-size: 48px;
  font-weight: 800;
  margin: 0;
  letter-spacing: -1px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.phonetic {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.pronunciation-controls {
  display: flex;
  gap: 12px;
}

.pronunciation-controls :deep(.el-button.is-circle) {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.4);
  color: white;
  width: 48px;
  height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.pronunciation-controls :deep(.el-button.is-circle:hover) {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.pronunciation-controls :deep(.el-button--success.is-circle) {
  background: rgba(103, 194, 58, 0.9);
  border-color: rgba(103, 194, 58, 1);
  animation: pulse 1.5s infinite;
  box-shadow: 0 0 20px rgba(103, 194, 58, 0.5);
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}

.word-content {
  position: relative;
  z-index: 1;
}

.word-content h3 {
  font-size: 18px;
  margin-bottom: 12px;
  margin-top: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.translation {
  font-size: 28px;
  font-weight: 600;
  line-height: 1.8;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.definition {
  font-size: 17px;
  line-height: 1.8;
  font-style: italic;
  opacity: 0.95;
}

.examples-list {
  list-style: none;
  padding: 0;
}

.examples-list li {
  padding: 12px 0;
  font-size: 16px;
  line-height: 1.8;
  border-left: 4px solid rgba(255, 255, 255, 0.6);
  padding-left: 20px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.05);
  padding: 12px 20px;
  border-radius: 8px;
  transition: all 0.3s;
}

.examples-list li:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.context-form {
  margin-top: 24px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 24px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.context-form h3 {
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 700;
}

.context-form :deep(.el-form-item__label) {
  color: white;
  font-weight: 600;
}

.context-form :deep(.el-input__wrapper),
.context-form :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.word-stats {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  position: relative;
  z-index: 1;
}

.word-stats .el-tag {
  border-radius: 20px;
  padding: 8px 16px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.2);
}

.recent-queries {
  margin-top: 40px;
  animation: fade-in-up 0.6s ease-out 0.4s both;
}

.recent-queries h3 {
  margin-bottom: 20px;
  color: var(--app-text-color, #606266);
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recent-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.recent-tag {
  cursor: pointer;
  font-size: 15px;
  padding: 10px 20px;
  border-radius: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(102, 126, 234, 0.1);
  border: 2px solid rgba(102, 126, 234, 0.3);
  font-weight: 600;
}

.recent-tag:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.5);
}

:deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.25);
  margin: 24px 0;
}
</style>

