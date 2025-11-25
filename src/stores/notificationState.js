// src/stores/notificationState.js
import { reactive } from 'vue'

export const notificationState = reactive({
  unreadCount: 0, // 全局未读消息数量
})
