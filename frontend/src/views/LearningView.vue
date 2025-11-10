<template>
  <div class="learning-view">
    <el-card class="overview-card">
      <h1 class="page-title">📖 学习计划</h1>
      
      <!-- 学习概览 -->
      <div v-loading="overviewLoading" class="overview-stats">
        <div class="stat-item">
          <div class="stat-value">{{ overview.total_words }}</div>
          <div class="stat-label">总单词数</div>
        </div>
        <div class="stat-item success">
          <div class="stat-value">{{ overview.mastered }}</div>
          <div class="stat-label">已掌握</div>
        </div>
        <div class="stat-item warning">
          <div class="stat-value">{{ overview.learning }}</div>
          <div class="stat-label">学习中</div>
        </div>
        <div class="stat-item danger">
          <div class="stat-value">{{ overview.to_review }}</div>
          <div class="stat-label">待复习</div>
        </div>
      </div>
    </el-card>
    
    <!-- 今日待复习 -->
    <el-card v-loading="reviewLoading" class="review-card">
      <div class="card-header">
        <h2>📝 今日待复习 ({{ reviewWords.length }})</h2>
        <el-button
          v-if="!isReviewing && reviewWords.length > 0"
          type="primary"
          @click="startReview"
        >
          开始复习
        </el-button>
      </div>
      
      <!-- 复习模式 -->
      <div v-if="isReviewing && currentReviewWord" class="review-mode">
        <div class="review-progress">
          <el-progress
            :percentage="reviewProgress"
            :stroke-width="12"
          />
          <span class="progress-text">
            {{ currentReviewIndex + 1 }} / {{ reviewWords.length }}
          </span>
        </div>
        
        <div class="review-card-flip">
          <div v-if="!showAnswer" class="card-front">
            <h2 class="review-word">{{ currentReviewWord.word }}</h2>
            <p class="review-phonetic">{{ currentReviewWord.phonetic }}</p>
            <el-button
              type="primary"
              size="large"
              @click="showAnswer = true"
            >
              显示答案
            </el-button>
          </div>
          
          <div v-else class="card-back">
            <h2 class="review-word">{{ currentReviewWord.word }}</h2>
            <p class="review-phonetic">{{ currentReviewWord.phonetic }}</p>
            <div class="answer-content">
              <p class="translation">{{ currentReviewWord.translation }}</p>
              <p v-if="currentReviewWord.definition" class="definition">
                {{ currentReviewWord.definition }}
              </p>
            </div>
            
            <div class="review-buttons">
              <el-button
                type="danger"
                size="large"
                @click="submitAnswer(false)"
              >
                😕 不会
              </el-button>
              <el-button
                type="warning"
                size="large"
                @click="submitAnswer(false)"
              >
                🤔 模糊
              </el-button>
              <el-button
                type="success"
                size="large"
                @click="submitAnswer(true)"
              >
                ✅ 掌握
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 复习完成 -->
      <div v-else-if="reviewCompleted" class="review-completed">
        <el-result
          icon="success"
          title="复习完成！"
          sub-title="今天的复习任务已完成，明天继续加油！"
        >
          <template #extra>
            <el-button type="primary" @click="loadReviewWords">
              重新加载
            </el-button>
          </template>
        </el-result>
      </div>
      
      <!-- 单词列表 -->
      <div v-else-if="!isReviewing" class="review-list">
        <div
          v-for="word in reviewWords"
          :key="word.id"
          class="review-item"
        >
          <div class="item-content">
            <h3>{{ word.word }}</h3>
            <p>{{ word.translation }}</p>
          </div>
          <el-tag
            :type="getMasteryType(word.learning_plan?.mastery_level)"
          >
            Lv.{{ word.learning_plan?.mastery_level || 0 }}
          </el-tag>
        </div>
        
        <el-empty
          v-if="reviewWords.length === 0"
          description="今天没有需要复习的单词"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { learningApi } from '@/api'

const overviewLoading = ref(false)
const reviewLoading = ref(false)

const overview = ref({
  total_words: 0,
  mastered: 0,
  learning: 0,
  to_review: 0
})

const reviewWords = ref([])
const isReviewing = ref(false)
const currentReviewIndex = ref(0)
const showAnswer = ref(false)
const reviewCompleted = ref(false)

const currentReviewWord = computed(() => {
  return reviewWords.value[currentReviewIndex.value]
})

const reviewProgress = computed(() => {
  if (reviewWords.value.length === 0) return 0
  return Math.round((currentReviewIndex.value / reviewWords.value.length) * 100)
})

// 加载学习概览
const loadOverview = async () => {
  overviewLoading.value = true
  try {
    const response = await learningApi.getPlan()
    if (response.code === 200) {
      overview.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载概览失败')
  } finally {
    overviewLoading.value = false
  }
}

// 加载待复习单词
const loadReviewWords = async () => {
  reviewLoading.value = true
  reviewCompleted.value = false
  try {
    const response = await learningApi.getTodayReview()
    if (response.code === 200) {
      reviewWords.value = response.data.words
    }
  } catch (error) {
    ElMessage.error('加载待复习单词失败')
  } finally {
    reviewLoading.value = false
  }
}

// 开始复习
const startReview = () => {
  isReviewing.value = true
  currentReviewIndex.value = 0
  showAnswer.value = false
}

// 提交答案
const submitAnswer = async (isCorrect) => {
  try {
    await learningApi.submitReview({
      word_id: currentReviewWord.value.id,
      is_correct: isCorrect,
      time_spent: 0
    })
    
    // 下一个单词
    if (currentReviewIndex.value < reviewWords.value.length - 1) {
      currentReviewIndex.value++
      showAnswer.value = false
    } else {
      // 复习完成
      isReviewing.value = false
      reviewCompleted.value = true
      ElMessage.success('复习完成！')
      loadOverview()
    }
  } catch (error) {
    ElMessage.error('提交失败')
  }
}

// 获取掌握程度标签类型
const getMasteryType = (level) => {
  if (!level || level === 0) return 'info'
  if (level <= 2) return 'warning'
  if (level <= 4) return 'primary'
  return 'success'
}

onMounted(() => {
  loadOverview()
  loadReviewWords()
})
</script>

<style scoped>
.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #303133;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  text-align: center;
  padding: 30px 20px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-item.success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-item.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-item.danger {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-value {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
}

.review-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.review-mode {
  padding: 20px 0;
}

.review-progress {
  margin-bottom: 30px;
  text-align: center;
}

.progress-text {
  display: block;
  margin-top: 10px;
  font-size: 16px;
  color: #606266;
}

.review-card-flip {
  max-width: 600px;
  margin: 0 auto;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-front,
.card-back {
  width: 100%;
  padding: 60px 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.review-word {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 15px;
}

.review-phonetic {
  font-size: 24px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.answer-content {
  margin: 30px 0;
  text-align: left;
}

.translation {
  font-size: 28px;
  font-weight: 500;
  margin-bottom: 15px;
}

.definition {
  font-size: 18px;
  opacity: 0.9;
  font-style: italic;
}

.review-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.review-list {
  display: grid;
  gap: 15px;
}

.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s;
}

.review-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.item-content h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.item-content p {
  margin: 0;
  color: #606266;
}

.review-completed {
  padding: 40px 0;
}
</style>

