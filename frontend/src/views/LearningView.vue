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
            <div class="pronunciation-icon">
              <el-button
                :icon="Microphone"
                circle
                size="large"
                @click="playWord(currentReviewWord.word)"
              />
            </div>
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
            <div class="pronunciation-icon">
              <el-button
                :icon="Microphone"
                circle
                size="large"
                @click="playWord(currentReviewWord.word)"
              />
            </div>
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
            <div class="item-title-row">
              <h3>{{ word.word }}</h3>
              <el-button
                :icon="Microphone"
                size="small"
                circle
                @click="playWord(word.word)"
              />
            </div>
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
import { Microphone } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { learningApi } from '@/api'
import { playWord } from '@/utils/useSpeech'

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
.learning-view {
  animation: fade-in-up 0.6s ease-out;
}

.learning-view :deep(.el-card) {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 32px;
}

.learning-view :deep(.el-card:hover) {
  box-shadow: 0 12px 48px rgba(31, 38, 135, 0.25);
}

.page-title {
  font-size: 36px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
  letter-spacing: -1px;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-top: 28px;
}

.stat-item {
  text-align: center;
  padding: 36px 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-item::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  animation: float 8s ease-in-out infinite;
}

.stat-item:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.4);
}

.stat-item.success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  box-shadow: 0 8px 24px rgba(17, 153, 142, 0.3);
}

.stat-item.success:hover {
  box-shadow: 0 12px 32px rgba(17, 153, 142, 0.4);
}

.stat-item.warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 8px 24px rgba(240, 147, 251, 0.3);
}

.stat-item.warning:hover {
  box-shadow: 0 12px 32px rgba(240, 147, 251, 0.4);
}

.stat-item.danger {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  box-shadow: 0 8px 24px rgba(250, 112, 154, 0.3);
}

.stat-item.danger:hover {
  box-shadow: 0 12px 32px rgba(250, 112, 154, 0.4);
}

.stat-value {
  font-size: 56px;
  font-weight: 800;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 17px;
  opacity: 0.95;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.review-card {
  margin-top: 28px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
}

.card-header h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.card-header .el-button {
  border-radius: 12px;
  padding: 12px 28px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 15px;
}

.card-header .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

.review-mode {
  padding: 28px 0;
}

.review-progress {
  margin-bottom: 40px;
  text-align: center;
}

.review-progress :deep(.el-progress__text) {
  font-weight: 700;
  font-size: 16px;
}

.review-progress :deep(.el-progress-bar__outer) {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(102, 126, 234, 0.1);
}

.review-progress :deep(.el-progress-bar__inner) {
  border-radius: 12px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.progress-text {
  display: block;
  margin-top: 16px;
  font-size: 18px;
  color: #606266;
  font-weight: 700;
}

.review-card-flip {
  max-width: 700px;
  margin: 0 auto;
  min-height: 450px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-front,
.card-back {
  width: 100%;
  padding: 64px 48px;
  border-radius: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
  animation: fade-in-up 0.5s ease-out;
}

.card-front::before,
.card-back::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 8s ease-in-out infinite;
}

.pronunciation-icon {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 2;
}

.pronunciation-icon :deep(.el-button) {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.4);
  color: white;
  width: 56px;
  height: 56px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.pronunciation-icon :deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.review-word {
  font-size: 56px;
  font-weight: 800;
  margin-bottom: 20px;
  letter-spacing: -1px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
}

.review-phonetic {
  font-size: 26px;
  margin-bottom: 40px;
  opacity: 0.95;
  font-weight: 500;
  position: relative;
  z-index: 1;
}

.answer-content {
  margin: 36px 0;
  text-align: left;
  position: relative;
  z-index: 1;
}

.translation {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.6;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.definition {
  font-size: 20px;
  opacity: 0.95;
  font-style: italic;
  line-height: 1.7;
}

.review-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
  position: relative;
  z-index: 1;
}

.review-buttons .el-button {
  padding: 16px 32px;
  font-size: 18px;
  font-weight: 700;
  border-radius: 16px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.review-buttons .el-button:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.review-list {
  display: grid;
  gap: 16px;
}

.review-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.review-item::before {
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

.review-item:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
  transform: translateY(-2px) translateX(4px);
  background: rgba(255, 255, 255, 0.9);
}

.review-item:hover::before {
  transform: scaleY(1);
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.item-content h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: #303133;
  letter-spacing: -0.5px;
}

.item-content p {
  margin: 0;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.6;
}

.item-title-row .el-button {
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.1);
  border-color: transparent;
  color: #667eea;
}

.item-title-row .el-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
}

.review-item:hover .item-title-row .el-button {
  opacity: 1;
}

.review-item .el-tag {
  border-radius: 20px;
  padding: 8px 16px;
  font-weight: 700;
  font-size: 14px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.review-completed {
  padding: 48px 0;
}

.review-completed :deep(.el-result__icon svg) {
  width: 80px;
  height: 80px;
}

.review-completed :deep(.el-result__title p) {
  font-size: 28px;
  font-weight: 800;
}

.review-completed :deep(.el-result__subtitle p) {
  font-size: 16px;
}
</style>

