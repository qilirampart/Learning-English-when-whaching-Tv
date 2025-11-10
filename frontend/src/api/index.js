import axios from 'axios'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('响应错误:', error)
    return Promise.reject(error)
  }
)

// 单词相关API
export const wordApi = {
  // 查询单词
  query(data) {
    return request.post('/words/query', data)
  },
  
  // 搜索单词
  search(keyword) {
    return request.get('/words/search', { params: { keyword } })
  },
  
  // 获取单词详情
  getDetail(id) {
    return request.get(`/words/${id}`)
  },
  
  // 获取单词列表
  getList(params) {
    return request.get('/words/list', { params })
  }
}

// 学习计划相关API
export const learningApi = {
  // 获取今日待复习单词
  getTodayReview() {
    return request.get('/learning/today')
  },
  
  // 获取学习计划概览
  getPlan() {
    return request.get('/learning/plan')
  },
  
  // 提交复习结果
  submitReview(data) {
    return request.post('/learning/review', data)
  }
}

// 统计相关API
export const statisticsApi = {
  // 获取统计概览
  getOverview() {
    return request.get('/statistics/overview')
  },
  
  // 获取剧集统计
  getTvShows() {
    return request.get('/statistics/tv_shows')
  }
}

export default request

