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
            <h2 class="word-text">{{ wordResult.word }}</h2>
            <span v-if="wordResult.phonetic" class="phonetic">{{ wordResult.phonetic }}</span>
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
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { wordApi } from '@/api'
import { useWordStore } from '@/stores/word'

const wordStore = useWordStore()

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
</script>

<style scoped>
.query-view {
  max-width: 900px;
  margin: 0 auto;
}

.query-card {
  border-radius: 12px;
}

.title {
  font-size: 32px;
  margin-bottom: 10px;
  color: #303133;
  text-align: center;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 30px;
}

.search-box {
  margin-bottom: 30px;
}

.result-container {
  margin-top: 30px;
}

.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.word-header {
  display: flex;
  align-items: baseline;
  gap: 15px;
  margin-bottom: 10px;
}

.word-text {
  font-size: 36px;
  font-weight: bold;
  margin: 0;
}

.phonetic {
  font-size: 18px;
  color: #e0e0e0;
}

.word-content h3 {
  font-size: 16px;
  margin-bottom: 10px;
  margin-top: 20px;
}

.translation {
  font-size: 24px;
  font-weight: 500;
  line-height: 1.6;
}

.definition {
  font-size: 16px;
  line-height: 1.6;
  font-style: italic;
}

.examples-list {
  list-style: none;
  padding: 0;
}

.examples-list li {
  padding: 8px 0;
  font-size: 15px;
  line-height: 1.6;
  border-left: 3px solid rgba(255, 255, 255, 0.5);
  padding-left: 15px;
  margin-bottom: 8px;
}

.context-form {
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
}

.context-form h3 {
  margin-bottom: 15px;
}

.context-form :deep(.el-form-item__label) {
  color: white;
}

.context-form :deep(.el-input__inner),
.context-form :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.9);
}

.word-stats {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.recent-queries {
  margin-top: 30px;
}

.recent-queries h3 {
  margin-bottom: 15px;
  color: #606266;
}

.recent-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.recent-tag {
  cursor: pointer;
  font-size: 14px;
  padding: 8px 16px;
  transition: all 0.3s;
}

.recent-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

:deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.3);
}
</style>

