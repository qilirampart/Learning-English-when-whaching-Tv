import request from '@/utils/request'

// 单词相关API
export const wordApi = {
  // 查询单词
  async query(data) {
    const response = await request.post('/api/words/query', data)
    return response.data
  },

  // 搜索单词
  async search(keyword) {
    const response = await request.get('/api/words/search', { params: { keyword } })
    return response.data
  },

  // 获取单词详情
  async getDetail(id) {
    const response = await request.get(`/api/words/${id}`)
    return response.data
  },

  // 获取单词列表
  async getList(params) {
    const response = await request.get('/api/words/list', { params })
    return response.data
  }
}

// 学习计划相关API
export const learningApi = {
  // 获取今日待复习单词
  async getTodayReview() {
    const response = await request.get('/api/learning/today')
    return response.data
  },

  // 获取学习计划概览
  async getPlan() {
    const response = await request.get('/api/learning/plan')
    return response.data
  },

  // 提交复习结果
  async submitReview(data) {
    const response = await request.post('/api/learning/review', data)
    return response.data
  }
}

// 统计相关API
export const statisticsApi = {
  // 获取统计概览
  async getOverview() {
    const response = await request.get('/api/statistics/overview')
    return response.data
  },

  // 获取剧集统计
  async getTvShows() {
    const response = await request.get('/api/statistics/tv_shows')
    return response.data
  }
}

export default request

