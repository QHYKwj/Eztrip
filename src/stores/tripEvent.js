// src/stores/tripEvent.js
import { defineStore } from 'pinia'

export const useTripEventStore = defineStore('tripEvent', {
  state: () => ({
    // 每次发生新增、删除行程时，自增数值触发全局响应式监听
    refreshTrigger: 0,
  }),
  actions: {
    // 供外部调用触发刷新的动作
    triggerRefresh () {
      this.refreshTrigger++
    },
  },
})
