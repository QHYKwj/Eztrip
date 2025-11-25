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
        :key="index"
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
        messages: [
          {
            sender: '系统通知',
            type: 'system',
            content: '您的2025年11月行程申请已通过审核，可在「行程」页面查看详情。',
            time: 1_730_613_000_000,
            unread: true,
          },
          {
            sender: '客服小助手',
            type: 'service',
            content: '您上周咨询的「AI生成行程」功能已上线，快去体验吧！',
            time: 1_730_534_400_000,
            unread: true,
          },
          {
            sender: '系统通知',
            type: 'system',
            content: '账号安全提醒：您的账号于2025-11-01在杭州登录。',
            time: 1_730_448_000_000,
            unread: false,
          },
          {
            sender: '行程助手',
            type: 'service',
            content: '您11月5日的「上海出差」行程已添加天气提醒。',
            time: 1_730_361_600_000,
            unread: false,
          },
        ],
      }
    },
    computed: {
      filteredMessages () {
        switch (this.activeFilter) {
          case 'unread': {
            return this.messages.filter(m => m.unread)
          }
          case 'read': {
            return this.messages.filter(m => !m.unread)
          }
          default: {
            return this.messages
          }
        }
      },
      hasReadMessages () {
        return this.messages.some(m => !m.unread)
      },
      hasUnreadMessages () {
        return this.messages.some(m => m.unread)
      },
    },
    mounted () {
      setTimeout(() => {
        this.isLoading = false
        this.updateGlobalUnreadCount()
      }, 800)
    },
    methods: {
      formatTime (timestamp) {
        const date = new Date(timestamp)
        return date.toLocaleString('zh-CN', {
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
        })
      },
      handleMsgClick (msg, index) {
        if (msg.unread) {
          this.messages[index].unread = false
          this.updateGlobalUnreadCount()
        }
      },
      clearReadMessages () {
        this.messages = this.messages.filter(m => m.unread)
        this.updateGlobalUnreadCount()
      },
      markAllAsRead () {
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
