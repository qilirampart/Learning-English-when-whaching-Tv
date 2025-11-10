import { defineStore } from 'pinia'
import { ref } from 'vue'
import { wordApi } from '@/api'

export const useWordStore = defineStore('word', () => {
  const recentQueries = ref([])
  
  // 添加最近查询记录
  const addRecentQuery = (word) => {
    const index = recentQueries.value.findIndex(w => w.word === word.word)
    if (index > -1) {
      recentQueries.value.splice(index, 1)
    }
    recentQueries.value.unshift(word)
    if (recentQueries.value.length > 5) {
      recentQueries.value.pop()
    }
  }
  
  return {
    recentQueries,
    addRecentQuery
  }
})

