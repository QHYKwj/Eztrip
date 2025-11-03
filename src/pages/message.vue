<template>
  <v-container fluid class="py-6">
    <!-- 页面标题栏 -->
    <v-row align="center" class="mb-6">
      <v-col cols="12">
        <v-toolbar flat>
          <v-toolbar-title class="text-h5 font-medium">消息中心</v-toolbar-title>
          <v-spacer></v-spacer>

          <!-- 消息筛选下拉框 -->
          <v-select
            v-model="activeFilter"
            :items="filterOptions"
            dense
            hide-details
            variant="outlined"
            style="width: 160px"
          ></v-select>

          <!-- 清空已读按钮 -->
          <v-btn
            icon
            size="small"
            color="primary"
            :disabled="!hasReadMessages"
            @click="clearReadMessages"
          >
            <v-icon>mdi-trash-can-outline</v-icon>
          </v-btn>
        </v-toolbar>
      </v-col>
    </v-row>

    <!-- 加载状态 -->
    <v-skeleton-loader
      v-if="isLoading"
      type="list-item-two-line"
      :count="3"
      class="mb-4"
    ></v-skeleton-loader>

    <!-- 空消息状态 -->
    <v-card v-else-if="filteredMessages.length === 0" class="text-center py-10">
      <v-card-text class="text-grey-darken-4">暂无消息</v-card-text>
    </v-card>

    <!-- 消息列表 -->
    <v-list v-else dense class="elevation-1 rounded-lg overflow-hidden">
      <v-list-item
        v-for="(msg, index) in filteredMessages"
        :key="index"
        :class="{ 'bg-primary-lighten-5': msg.unread }"
        @click="handleMsgClick(msg, index)"
      >
        <!-- 未读标记 -->
        <v-badge v-if="msg.unread" color="primary" variant="dot" class="mr-2"></v-badge>

        <!-- 消息文字 -->
        <v-list-item-content>
          <v-row no-gutters align="center">
            <v-col cols="auto">
              <v-list-item-title class="font-medium">{{ msg.sender }}</v-list-item-title>
            </v-col>
            <v-col cols="auto">
              <v-chip
                :color="msg.type === 'system' ? 'primary' : 'success'"
                size="x-small"
                variant="outlined"
                class="ml-2"
              >
                {{ msg.type === 'system' ? '系统' : '客服' }}
              </v-chip>
            </v-col>
          </v-row>

          <v-list-item-subtitle class="text-grey-darken-4">
            {{ msg.content }}
          </v-list-item-subtitle>
        </v-list-item-content>

        <!-- 消息时间 -->
        <v-list-item-action class="text-right">
          <span class="text-xs text-grey-darken-4">{{ formatTime(msg.time) }}</span>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
export default {
  name: 'MessageCenter',
  data() {
    return {
      isLoading: true,
      activeFilter: 'all',
      filterOptions: [
        { text: '全部消息', value: 'all' },
        { text: '未读消息', value: 'unread' },
        { text: '已读消息', value: 'read' }
      ],
      messages: [
        {
          sender: '系统通知',
          type: 'system',
          content: '您的2025年11月行程申请已通过审核，可在「行程」页面查看详情。',
          time: 1730613000000,
          unread: true
        },
        {
          sender: '客服小助手',
          type: 'service',
          content: '您上周咨询的「AI生成行程」功能已上线，快去体验吧！',
          time: 1730534400000,
          unread: true
        },
        {
          sender: '系统通知',
          type: 'system',
          content: '账号安全提醒：您的账号于2025-11-01在杭州登录。',
          time: 1730448000000,
          unread: false
        },
        {
          sender: '行程助手',
          type: 'service',
          content: '您11月5日的「上海出差」行程已添加天气提醒。',
          time: 1730361600000,
          unread: false
        }
      ]
    }
  },
  computed: {
    filteredMessages() {
      switch (this.activeFilter) {
        case 'unread':
          return this.messages.filter(m => m.unread)
        case 'read':
          return this.messages.filter(m => !m.unread)
        default:
          return this.messages
      }
    },
    hasReadMessages() {
      return this.messages.some(m => !m.unread)
    }
  },
  mounted() {
    setTimeout(() => (this.isLoading = false), 800)
  },
  methods: {
    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    handleMsgClick(msg, index) {
      if (msg.unread) this.$set(this.messages[index], 'unread', false)
    },
    clearReadMessages() {
      this.messages = this.messages.filter(m => m.unread)
    }
  }
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
