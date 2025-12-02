<template>
  <div class="words-view">
    <el-card>
      <div class="header-section">
        <h1 class="page-title">📚 我的单词库</h1>

        <!-- 导出按钮 -->
        <el-dropdown @command="handleExport" :loading="exporting">
          <el-button type="primary" :icon="Download" :loading="exporting">
            导出单词本
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="excel">
                <el-icon><DocumentCopy /></el-icon>
                导出为 Excel
              </el-dropdown-item>
              <el-dropdown-item command="pdf">
                <el-icon><Document /></el-icon>
                导出为 PDF
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 筛选和排序 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索单词..."
          style="width: 250px"
          clearable
          @change="loadWords"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="filters.filter_show"
          placeholder="按剧集筛选"
          clearable
          style="width: 200px"
          @change="loadWords"
        >
          <el-option
            v-for="show in tvShows"
            :key="show"
            :label="show"
            :value="show"
          />
        </el-select>

        <el-select
          v-model="filters.order_by"
          placeholder="排序方式"
          style="width: 150px"
          @change="loadWords"
        >
          <el-option label="最新查询" value="time" />
          <el-option label="查询频率" value="frequency" />
          <el-option label="掌握程度" value="mastery" />
        </el-select>
      </div>
      
      <!-- 单词列表 -->
      <div v-loading="loading" class="words-list">
        <div
          v-for="word in words"
          :key="word.id"
          class="word-card"
          @click="showDetail(word)"
        >
          <div class="word-main">
            <div class="word-left">
              <div class="word-title-row">
                <h3 class="word-title">{{ word.word }}</h3>
                <el-button
                  :icon="Microphone"
                  size="small"
                  circle
                  @click.stop="playWord(word.word)"
                />
              </div>
              <p class="word-translation">{{ word.translation }}</p>
            </div>
            <div class="word-right">
              <el-tag
                :type="getMasteryType(word.mastery_level)"
                effect="dark"
              >
                掌握度: {{ word.mastery_level }}/5
              </el-tag>
            </div>
          </div>
          
          <div class="word-meta">
            <el-tag size="small" type="info">
              <el-icon><View /></el-icon>
              {{ word.query_count }} 次
            </el-tag>
            <el-tag
              v-for="show in word.tv_shows.slice(0, 2)"
              :key="show"
              size="small"
              type="success"
            >
              {{ show }}
            </el-tag>
            <span v-if="word.last_query" class="query-time">
              {{ formatDate(word.last_query) }}
            </span>
          </div>
        </div>
        
        <!-- 空状态 -->
        <el-empty
          v-if="!loading && words.length === 0"
          description="还没有查询过单词，快去查询吧！"
        />
      </div>
      
      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="loadWords"
          @size-change="loadWords"
        />
      </div>
    </el-card>
    
    <!-- 单词详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      width="700px"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ currentWord?.word }}</span>
          <el-button
            v-if="currentWord"
            :icon="Microphone"
            type="primary"
            @click="playWord(currentWord.word)"
          >
            播放发音
          </el-button>
        </div>
      </template>

      <div v-if="currentWord" class="word-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <p><strong>音标:</strong> {{ currentWord.phonetic }}</p>
          <p><strong>翻译:</strong> {{ currentWord.translation }}</p>
          <p v-if="currentWord.definition"><strong>释义:</strong> {{ currentWord.definition }}</p>
        </div>
        
        <div v-if="currentWord.examples && currentWord.examples.length" class="detail-section">
          <h3>例句</h3>
          <ul>
            <li v-for="(example, index) in currentWord.examples" :key="index">
              {{ example }}
            </li>
          </ul>
        </div>
        
        <div v-if="currentWord.query_logs && currentWord.query_logs.length" class="detail-section">
          <h3>查询记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="log in currentWord.query_logs"
              :key="log.id"
              :timestamp="formatDate(log.query_time)"
            >
              <div v-if="log.tv_show">
                <strong>{{ log.tv_show }}</strong>
                <span v-if="log.season_episode"> - {{ log.season_episode }}</span>
              </div>
              <p v-if="log.context_note">{{ log.context_note }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, View, Microphone, Download, Document, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { wordApi } from '@/api'
import { playWord } from '@/utils/useSpeech'

const loading = ref(false)
const exporting = ref(false)
const words = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const tvShows = ref([])

const filters = ref({
  keyword: '',
  filter_show: '',
  order_by: 'time'
})

const detailVisible = ref(false)
const currentWord = ref(null)

// 加载单词列表
const loadWords = async () => {
  loading.value = true
  
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      order_by: filters.value.order_by
    }
    
    if (filters.value.filter_show) {
      params.filter_show = filters.value.filter_show
    }
    
    const response = await wordApi.getList(params)
    
    if (response.code === 200) {
      words.value = response.data.items
      total.value = response.data.total
      
      // 提取所有剧集名称
      const showSet = new Set()
      words.value.forEach(word => {
        word.tv_shows?.forEach(show => showSet.add(show))
      })
      tvShows.value = Array.from(showSet)
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + (error.message || '网络错误'))
  } finally {
    loading.value = false
  }
}

// 显示单词详情
const showDetail = async (word) => {
  try {
    const response = await wordApi.getDetail(word.id)
    if (response.code === 200) {
      currentWord.value = response.data
      detailVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

// 获取掌握程度标签类型
const getMasteryType = (level) => {
  if (level === 0) return 'info'
  if (level <= 2) return 'warning'
  if (level <= 4) return 'primary'
  return 'success'
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 导出单词本
const handleExport = async (format) => {
  if (total.value === 0) {
    ElMessage.warning('您还没有查询过任何单词')
    return
  }

  exporting.value = true

  try {
    await wordApi.exportWords(format)
    const formatText = format === 'excel' ? 'Excel' : 'PDF'
    ElMessage.success(`${formatText} 文件导出成功！`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + (error.message || '网络错误'))
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadWords()
})
</script>

<style scoped>
.words-view {
  animation: fade-in-up 0.6s ease-out;
}

.words-view :deep(.el-card) {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.words-view :deep(.el-card:hover) {
  box-shadow: 0 12px 48px rgba(31, 38, 135, 0.25);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.page-title {
  font-size: 36px;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  letter-spacing: -1px;
}

.header-section :deep(.el-button) {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-section :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.filter-bar :deep(.el-input),
.filter-bar :deep(.el-select) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-bar :deep(.el-input__wrapper),
.filter-bar :deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  transition: all 0.3s;
}

.filter-bar :deep(.el-input__wrapper:hover),
.filter-bar :deep(.el-select .el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.words-list {
  min-height: 400px;
}

.word-card {
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.word-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleY(0);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.word-card:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
  transform: translateY(-4px) translateX(4px);
  background: rgba(255, 255, 255, 0.9);
}

.word-card:hover::before {
  transform: scaleY(1);
}

.word-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.word-left {
  flex: 1;
}

.word-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 10px;
}

.word-title {
  font-size: 28px;
  font-weight: 800;
  margin: 0;
  color: #303133;
  letter-spacing: -0.5px;
}

.word-title-row .el-button {
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  border-color: transparent;
  color: #667eea;
}

.word-title-row .el-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.word-card:hover .word-title-row .el-button {
  opacity: 1;
}

.word-translation {
  font-size: 17px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
  font-weight: 500;
}

.word-right {
  margin-left: 24px;
}

.word-right .el-tag {
  border-radius: 20px;
  padding: 8px 16px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.word-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.word-meta .el-tag {
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.query-time {
  font-size: 13px;
  color: #909399;
  margin-left: auto;
  font-weight: 500;
}

.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}

.pagination :deep(.el-pagination) {
  gap: 8px;
}

.pagination :deep(.el-pagination button),
.pagination :deep(.el-pager li) {
  border-radius: 10px;
  transition: all 0.3s;
}

.pagination :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.word-detail .detail-section {
  margin-bottom: 32px;
  animation: fade-in-up 0.5s ease-out;
}

.word-detail h3 {
  font-size: 20px;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 16px;
  border-left: 4px solid;
  border-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%) 1;
}

.word-detail p {
  margin: 12px 0;
  line-height: 1.8;
  font-size: 16px;
  color: #606266;
}

.word-detail ul {
  padding-left: 0;
  list-style: none;
}

.word-detail li {
  margin: 12px 0;
  line-height: 1.8;
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border-left: 3px solid rgba(102, 126, 234, 0.4);
  transition: all 0.3s;
}

.word-detail li:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateX(4px);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 20px;
}

.dialog-title {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
}

:deep(.el-dialog) {
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(31, 38, 135, 0.25);
}

:deep(.el-dialog__header) {
  padding: 32px 32px 20px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

:deep(.el-dialog__body) {
  padding: 32px;
}
</style>

