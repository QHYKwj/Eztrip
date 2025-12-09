<template>
  <v-container class="py-6" fluid>
    <!-- 页面标题栏 -->
    <v-row align="center" class="mb-6">
      <v-col cols="12">
        <v-toolbar flat>
          <v-toolbar-title class="text-h5 font-medium">消息中心</v-toolbar-title>
          <v-spacer />

          <!-- 消息筛选下拉框 -->
          <v-select
            v-model="activeFilter"
            density="compact"
            hide-details
            :items="filterOptions"
            style="width: 160px"
            variant="outlined"
          />

          <!-- 清空已读按钮 -->
          <v-btn
            color="primary"
            :disabled="!hasReadMessages"
            icon
            size="small"
            @click="clearReadMessages"
          >
            <v-icon>mdi-trash-can-outline</v-icon>
          </v-btn>

          <!-- 一键已读按钮 -->
          <v-btn
            class="ml-2"
            color="primary"
            :disabled="!hasUnreadMessages"
            icon
            size="small"
            @click="markAllAsRead"
          >
            <v-icon>mdi-check-all</v-icon>
          </v-btn>
        </v-toolbar>
      </v-col>
    </v-row>

    <!-- 加载状态 -->
    <v-skeleton-loader
      v-if="isLoading"
      class="mb-4"
      :loading="true"
      type="list-item-two-line"
    />

    <!-- 空消息状态 -->
    <v-card
      v-else-if="filteredMessages.length === 0"
      class="text-center py-10"
    >
      <v-card-text class="text-grey-darken-4">暂无消息</v-card-text>
    </v-card>

    <!-- 消息列表 -->
    <v-list
      v-else
      class="elevation-1 rounded-lg overflow-hidden"
      density="compact"
    >
      <v-list-item
        v-for="(msg, index) in filteredMessages"
        :key="msg.id"
        :class="{ 'bg-primary-lighten-5': msg.unread }"
        @click="handleMsgClick(msg, index)"
      >
        <!-- 未读标记 -->
        <template #prepend>
          <v-badge
            v-if="msg.unread"
            class="mr-1"
            color="primary"
            dot
          />
        </template>

        <v-list-item-title class="d-flex align-center">
          <span class="font-medium">{{ msg.sender }}</span>
          <v-chip
            class="ml-2"
            :color="msg.type === 'system' ? 'primary' : 'success'"
            size="x-small"
            variant="outlined"
          >
            {{ msg.type === 'system' ? '系统' : '客服' }}
          </v-chip>
        </v-list-item-title>

        <v-list-item-subtitle class="text-grey-darken-4">
          {{ msg.content }}
        </v-list-item-subtitle>

        <template #append>
          <span class="text-xs text-grey-darken-4">
            {{ formatTime(msg.time) }}
          </span>
        </template>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
import axios from 'axios'
import { notificationState } from '@/stores/notificationState'

export default {
  name: 'MessageCenter',
  data () {
    return {
      isLoading: true,
      activeFilter: 'all',
      filterOptions: [
        { title: '全部消息', value: 'all' },
        { title: '未读消息', value: 'unread' },
        { title: '已读消息', value: 'read' },
      ],
      messages: [], // 从后端加载
    }
  },
  computed: {
    filteredMessages () {
      switch (this.activeFilter) {
        case 'unread':
          return this.messages.filter(m => m.unread)
        case 'read':
          return this.messages.filter(m => !m.unread)
        default:
          return this.messages
      }
    },
    hasReadMessages () {
      return this.messages.some(m => !m.unread)
    },
    hasUnreadMessages () {
      return this.messages.some(m => m.unread)
    },
  },
  async mounted () {
    await this.fetchMessages()
  },
  methods: {
    getUserFromStorage () {
      // 你前面已经把登录信息改到 sessionStorage，这里保持一致
      const str = sessionStorage.getItem('user')
      if (!str) return null
      try {
        return JSON.parse(str)
      } catch {
        return null
      }
    },
    async fetchMessages () {
      const user = this.getUserFromStorage()
      if (!user || !user.user_id) {
        this.isLoading = false
        return
      }

      this.isLoading = true
      try {
        const res = await axios.get('/api/notifications', {
          params: { user_id: user.user_id },
        })

        // 后端返回：[{ id, kind, sender, title, content, created_at, unread, type }, ...]
        this.messages = (res.data || []).map(raw => {
          const time = new Date(raw.created_at).getTime()
          return {
            id: raw.id,
            kind: raw.kind,      // 'message' | 'notice'
            sender: raw.sender,
            title: raw.title,
            content: raw.content,
            type: raw.type,      // 'system' | 'service'
            time,
            unread: !!raw.unread,
          }
        })

        this.updateGlobalUnreadCount()
      } catch (e) {
        console.error('加载消息失败', e)
      } finally {
        this.isLoading = false
      }
    },
    formatTime (timestamp) {
      const date = new Date(timestamp)
      if (Number.isNaN(date.getTime())) return ''
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      })
    },
    async handleMsgClick (msg, index) {
      // 如果是个人消息且未读，调用后端标记已读
      if (msg.kind === 'message' && msg.unread) {
        const user = this.getUserFromStorage()
        if (user && user.user_id) {
          try {
            await axios.put(`/api/notifications/messages/${msg.id}/read`, null, {
              params: { user_id: user.user_id },
            })
          } catch (e) {
            console.error('标记消息已读失败（前端继续本地置为已读）', e)
          }
        }
        // 本地更新
        const idxInAll = this.messages.findIndex(m => m.id === msg.id && m.kind === msg.kind)
        if (idxInAll !== -1) {
          this.messages[idxInAll].unread = false
        }
        this.updateGlobalUnreadCount()
      }
    },
    clearReadMessages () {
      // 只在前端列表中清空已读，不动数据库
      this.messages = this.messages.filter(m => m.unread)
      this.updateGlobalUnreadCount()
    },
    async markAllAsRead () {
      const user = this.getUserFromStorage()
      if (!user || !user.user_id) return

      try {
        await axios.put('/api/notifications/messages/read-all', null, {
          params: { user_id: user.user_id },
        })
      } catch (e) {
        console.error('一键已读接口失败（前端仍然本地置为已读）', e)
      }

      // 本地把所有 message 标记为已读（notice 不受影响；但这里统一置为 false 问题也不大）
      this.messages = this.messages.map(m => ({
        ...m,
        unread: false,
      }))
      this.updateGlobalUnreadCount()
    },
    updateGlobalUnreadCount () {
      const unread = this.messages.filter(m => m.unread).length
      notificationState.unreadCount = unread
    },
  },
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.v-list-item {
  transition: background-color 0.2s;
}

.v-list-item:hover {
  background-color: #f6f5ff;
}
</style>
