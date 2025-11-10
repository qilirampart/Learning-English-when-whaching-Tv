<template>
  <div class="statistics-view">
    <el-card>
      <h1 class="page-title">📊 学习统计</h1>
      
      <!-- 统计卡片 -->
      <div v-loading="loading" class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon primary">
            <el-icon><Collection /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.total_words }}</div>
            <div class="stat-label">总单词数</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon success">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.today_queries }}</div>
            <div class="stat-label">今日查询</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon warning">
            <el-icon><Star /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.mastered }}</div>
            <div class="stat-label">已掌握</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon danger">
            <el-icon><Edit /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.to_review }}</div>
            <div class="stat-label">待复习</div>
          </div>
        </div>
      </div>
      
      <!-- 学习曲线 -->
      <el-card class="chart-card">
        <h2>📈 最近7天查询趋势</h2>
        <div class="chart-container">
          <div class="bar-chart">
            <div
              v-for="(count, index) in stats.weekly_trend"
              :key="index"
              class="bar-item"
            >
              <div class="bar-wrapper">
                <div
                  class="bar"
                  :style="{ height: getBarHeight(count) + '%' }"
                >
                  <span class="bar-value">{{ count }}</span>
                </div>
              </div>
              <div class="bar-label">{{ getWeekDay(index) }}</div>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 剧集排行 -->
      <el-card class="chart-card">
        <h2>🏆 剧集单词数排行</h2>
        <div v-loading="showsLoading" class="tv-shows-list">
          <div
            v-for="(show, index) in tvShows"
            :key="index"
            class="show-item"
          >
            <div class="show-rank" :class="getRankClass(index)">
              {{ index + 1 }}
            </div>
            <div class="show-name">{{ show.tv_show }}</div>
            <div class="show-count">
              <el-tag type="primary">{{ show.word_count }} 个单词</el-tag>
            </div>
          </div>
          
          <el-empty
            v-if="!showsLoading && tvShows.length === 0"
            description="还没有记录剧集信息"
          />
        </div>
      </el-card>
      
      <!-- 学习建议 -->
      <el-card class="tips-card">
        <h2>💡 学习建议</h2>
        <div class="tips-content">
          <el-alert
            v-if="stats.to_review > 0"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #title>
              你有 {{ stats.to_review }} 个单词待复习，建议尽快完成复习任务！
            </template>
          </el-alert>
          
          <el-alert
            v-if="stats.today_queries === 0"
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              今天还没有查询单词，看美剧时记得查询生词哦！
            </template>
          </el-alert>
          
          <el-alert
            v-if="stats.today_queries > 20"
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              今天已经查询了 {{ stats.today_queries }} 个单词，学习状态很棒！
            </template>
          </el-alert>
          
          <div class="mastery-rate">
            <h3>掌握率</h3>
            <el-progress
              :percentage="masteryPercentage"
              :stroke-width="20"
              :color="progressColors"
            />
            <p class="rate-text">
              已掌握 {{ stats.mastered }} / {{ stats.total_words }} 个单词
            </p>
          </div>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Collection, Document, Star, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { statisticsApi } from '@/api'

const loading = ref(false)
const showsLoading = ref(false)

const stats = ref({
  total_words: 0,
  today_queries: 0,
  mastered: 0,
  learning: 0,
  to_review: 0,
  weekly_trend: [0, 0, 0, 0, 0, 0, 0]
})

const tvShows = ref([])

const progressColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

const masteryPercentage = computed(() => {
  if (stats.value.total_words === 0) return 0
  return Math.round((stats.value.mastered / stats.value.total_words) * 100)
})

// 加载统计数据
const loadStatistics = async () => {
  loading.value = true
  try {
    const response = await statisticsApi.getOverview()
    if (response.code === 200) {
      stats.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

// 加载剧集统计
const loadTvShows = async () => {
  showsLoading.value = true
  try {
    const response = await statisticsApi.getTvShows()
    if (response.code === 200) {
      tvShows.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载剧集统计失败')
  } finally {
    showsLoading.value = false
  }
}

// 获取柱状图高度
const getBarHeight = (count) => {
  const maxCount = Math.max(...stats.value.weekly_trend, 1)
  return (count / maxCount) * 100
}

// 获取星期几
const getWeekDay = (index) => {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const today = new Date().getDay()
  const dayIndex = (today - 1 + index - 6 + 7) % 7
  return days[dayIndex < 0 ? dayIndex + 7 : dayIndex]
}

// 获取排名样式
const getRankClass = (index) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

onMounted(() => {
  loadStatistics()
  loadTvShows()
})
</script>

<style scoped>
.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #303133;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 25px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 20px;
  color: white;
}

.stat-icon.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-icon.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.danger {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-card h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
}

.chart-container {
  padding: 20px 0;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 250px;
  padding: 0 20px;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 100px;
}

.bar-wrapper {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 50px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px 4px 0 0;
  min-height: 20px;
  position: relative;
  transition: all 0.3s;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.bar:hover {
  opacity: 0.8;
  transform: scaleY(1.05);
}

.bar-value {
  color: white;
  font-weight: bold;
  margin-top: 8px;
}

.bar-label {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}

.tv-shows-list {
  min-height: 200px;
}

.show-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  transition: background 0.3s;
}

.show-item:hover {
  background: #f5f7fa;
}

.show-rank {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #909399;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 20px;
  flex-shrink: 0;
}

.show-rank.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #333;
  font-size: 18px;
}

.show-rank.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #333;
  font-size: 16px;
}

.show-rank.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #d4a574 100%);
  color: white;
}

.show-name {
  flex: 1;
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.show-count {
  margin-left: 20px;
}

.tips-card h2 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 20px;
}

.tips-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.mastery-rate {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.mastery-rate h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.rate-text {
  margin: 10px 0 0 0;
  text-align: center;
  color: #606266;
  font-size: 14px;
}
</style>

