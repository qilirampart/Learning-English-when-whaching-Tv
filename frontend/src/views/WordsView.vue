<template>
  <div class="words-view">
    <el-card>
      <h1 class="page-title">📚 我的单词库</h1>
      
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
              <h3 class="word-title">{{ word.word }}</h3>
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
      :title="currentWord?.word"
      width="700px"
    >
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
import { Search, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { wordApi } from '@/api'

const loading = ref(false)
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

onMounted(() => {
  loadWords()
})
</script>

<style scoped>
.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #303133;
}

.filter-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.words-list {
  min-height: 400px;
}

.word-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
  background: white;
}

.word-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.word-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.word-left {
  flex: 1;
}

.word-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #303133;
}

.word-translation {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.word-right {
  margin-left: 20px;
}

.word-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.query-time {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.word-detail .detail-section {
  margin-bottom: 25px;
}

.word-detail h3 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #409eff;
  border-left: 4px solid #409eff;
  padding-left: 10px;
}

.word-detail p {
  margin: 8px 0;
  line-height: 1.6;
}

.word-detail ul {
  padding-left: 20px;
}

.word-detail li {
  margin: 8px 0;
  line-height: 1.6;
}
</style>

