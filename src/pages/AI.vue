<template>
  <div class="ai-chat-container">
    <!-- 顶部导航栏 -->
    <v-app-bar
      elevation="0"
      style="background-color: #F3F2FD; border-bottom: 1px solid #DBD1EF"
    >
      <v-app-bar-nav-icon style="color: #675096" @click="$router.go(-1)" />
      <v-toolbar-title style="color: #675096; font-weight: 600">
        AI 智能助手
      </v-toolbar-title>
      <v-spacer />
      <v-btn
        v-tooltip:left="'清空对话'"
        icon
        style="color: #675096"
        @click="clearChat"
      >
        <v-icon>mdi-trash-can-outline</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- 对话历史区 -->
    <div ref="chatHistory" class="chat-history">
      <!-- 欢迎提示 -->
      <div v-if="chatMessages.length === 0" class="welcome-tip">
        <v-avatar size="64" style="background-color: #742DD8; margin-bottom: 16px">
          <v-icon color="white" size="32">mdi-robot</v-icon>
        </v-avatar>
        <h3 style="color: #444; margin-bottom: 8px">你好！我是你的 AI 助手</h3>
        <p style="color: #675096; font-size: 14px">
          有什么可以帮你的？开启下方 Agent 模式可以直接为你排版行程哦~
        </p>
      </div>

      <!-- 对话列表 -->
      <div v-else class="chat-list">
        <div
          v-for="(msg, index) in chatMessages"
          :key="index"
          :class="['chat-item', msg.role === 'user' ? 'user-chat' : 'ai-chat']"
        >
          <v-avatar class="chat-avatar" size="40">
            <v-icon color="white" size="20">
              {{ msg.role === 'user' ? 'mdi-account-circle' : 'mdi-robot' }}
            </v-icon>
          </v-avatar>
          <div class="chat-content">
            <div
              class="chat-bubble"
              :style="msg.role === 'user' ? userBubbleStyle : aiBubbleStyle"
            >
              <!-- 文本消息 -->
              <p :style="{ color: msg.role === 'user' ? 'white' : '#444' }">
                {{ msg.content }}
              </p>

              <!-- ✅ 核心：如果大模型生成了行程，渲染卡片 ✅ -->
              <div v-if="msg.trip_id" class="mt-4" style="width: 100%;">
                <v-divider class="mb-3" color="#DBD1EF" />
                <div style="color: #2e7d32; font-weight: 600; font-size: 14px; margin-bottom: 12px; display: flex; align-items: center;">
                  <v-icon class="mr-1" color="success" size="18">mdi-check-circle</v-icon>
                  行程已自动生成并保存至草稿箱
                </div>

                <!-- 渲染复用的 TripCard 组件 -->
                <TripCard
                  :ai-days="msg.structured_data?.total_days"
                  :ai-destination="msg.structured_data?.destination"
                  :ai-title="msg.structured_data?.trip_title"
                  :ai-trip-id="msg.trip_id"
                />

                <v-btn
                  block
                  class="mt-2 text-white"
                  color="#742DD8"
                  prepend-icon="mdi-map-search-outline"
                  variant="flat"
                  @click="$router.push(`/trip/${msg.trip_id}`)"
                >
                  查看并编辑详细路线
                </v-btn>
              </div>

            </div>
            <p class="chat-time">{{ formatTime(msg.timestamp) }}</p>
          </div>
        </div>

        <!-- AI 加载中状态 -->
        <div v-if="isLoading" class="chat-item ai-chat">
          <v-avatar class="chat-avatar" size="40">
            <v-icon color="white" size="20">mdi-robot</v-icon>
          </v-avatar>
          <div class="chat-content">
            <div class="chat-bubble" :style="aiBubbleStyle">
              <div class="loading-dots">
                <span class="dot" />
                <span class="dot" />
                <span class="dot" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input-area">
      <v-card
        outlined
        style="border-color: #DBD1EF; background-color: white; width: 100%"
      >
        <v-card-text class="pb-1">
          <!-- ✅ Agent 模式开关 ✅ -->
          <v-switch
            v-model="directAddPlan"
            class="mb-2"
            color="#742DD8"
            density="compact"
            hide-details
            label="🤖 开启 Agent 模式：直接生成详细行程并存入我的计划"
          />

          <v-textarea
            v-model="inputMessage"
            hide-details
            max-rows="4"
            placeholder="输入你的问题或需求..."
            rows="1"
            style="resize: none; color: #444; border: 1px solid #DBD1EF; border-radius: 8px; padding: 8px 12px"
            @keydown.enter.exact.prevent="sendMessage"
          />
        </v-card-text>
        <v-card-actions style="justify-content: flex-end; padding: 8px 16px">
          <v-btn
            :disabled="!inputMessage.trim() || isLoading"
            rounded
            style="background-color: #742DD8; color: white"
            @click="sendMessage"
          >
            <v-icon left>mdi-paper-plane</v-icon>发送
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script>
  import TripCard from '@/components/TripCard.vue' // 引入卡片组件
  import axios from '@/config/axios' // 建议使用你们统一配置好的 axios 实例
  // 🌟 新增：导入全局行程更新事件仓库
  import { useTripEventStore } from '@/stores/tripEvent'

  export default {
    name: 'AIChatPage',
    components: {
      TripCard,
    },
    data () {
      return {
        chatMessages: [],
        inputMessage: '',
        isLoading: false,
        directAddPlan: false, // 绑定开关的值
        userId: null, // 当前用户ID
        userBubbleStyle: {
          backgroundColor: '#742DD8',
          borderRadius: '16px 16px 4px 16px',
          padding: '12px 16px',
          maxWidth: '100%',
          lineHeight: '1.6',
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
          boxShadow: '0 1px 4px rgba(0, 0, 0, 0.05)',
        },
        aiBubbleStyle: {
          backgroundColor: '#F3F2FD',
          border: '1px solid #DBD1EF',
          borderRadius: '16px 16px 16px 4px',
          padding: '12px 16px',
          maxWidth: '85%', // 稍微加宽一点以适应可能出现的卡片
          lineHeight: '1.6',
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
          boxShadow: '0 1px 4px rgba(0, 0, 0, 0.05)',
        },
      }
    },

    mounted () {
      this.initUserAndLoadChat()
    },

    // ✅ 增加 activated 钩子，防止 App.vue 使用了 <keep-alive> 导致 mounted 不执行
    activated () {
      this.initUserAndLoadChat()
    },
    methods: {
      // 🌟 1. 抽离初始化方法
      initUserAndLoadChat () {
        console.log('=== 开始读取用户信息 ===')
        // 1. 取出存储字符串
        const userRaw = sessionStorage.getItem('user')
        console.log('sessionStorage["user"] 原始字符串：', userRaw)

        // 2. 解析JSON
        let userInfo = {}
        if (userRaw) {
          userInfo = JSON.parse(userRaw)
        }
        console.log('解析后的 userInfo 对象：', userInfo)

        // 3. 提取 user_id
        this.userId = userInfo.user_id ?? null
        console.log('赋值后的 this.userId =', this.userId)

        this.loadChatHistory()
      },

      // 🌟 2. 显式保存方法（核心解法）
      saveChatHistory () {
        if (this.userId) {
          sessionStorage.setItem(`eztrip_ai_chat_${this.userId}`, JSON.stringify(this.chatMessages))
        }
      },

      // 🌟 3. 加载历史记录
      loadChatHistory () {
        const savedChat = sessionStorage.getItem(`eztrip_ai_chat_${this.userId}`)
        if (savedChat) {
          try {
            const parsedChat = JSON.parse(savedChat)
            // 仅当缓存里真的有数据时才赋值，防止被 [] 覆盖
            if (parsedChat && parsedChat.length > 0) {
              this.chatMessages = parsedChat
              this.scrollToBottom()
            }
          } catch (error) {
            console.error('解析历史聊天记录失败', error)
          }
        }
      },
      async sendMessage () {
        const content = this.inputMessage.trim()
        if (!content || this.isLoading) return

        // ========== 新增：Agent模式下校验用户ID，避免行程归属错误 ==========
        if (this.directAddPlan && !this.userId) {
          alert('请先登录后再生成并保存行程')
          return
        }

        // 1) 先把用户消息放入列表
        const userMsg = {
          role: 'user',
          content,
          timestamp: Date.now(),
        }
        this.chatMessages.push(userMsg)
        this.saveChatHistory()
        this.inputMessage = ''
        this.scrollToBottom()

        // 2) 调用后端
        this.isLoading = true

        try {
          const payload = {
            user_id: this.userId,
            prompt: content,
            direct_add_plan: this.directAddPlan,
          }

          const res = await axios.post('/model/agent_plan', payload, {
            timeout: 120_000,
          })
          console.log('✅ 收到后端响应内容:', res)

          const resData = res?.data ?? res
          console.log(resData)
          const aiText = resData.reply ?? '（模型没有返回内容）'
          const tripId = resData.trip_id || null
          // 🌟 核心修改：如果本次 AI 成功生成并存入了数据库，立刻派发全局更新事件！
          if (tripId) {
            const tripStore = useTripEventStore()
            tripStore.triggerRefresh()
          }
          const aiMsg = {
            role: 'ai',
            content: aiText,
            trip_id: tripId,
            // ========== 新增：保存结构化行程数据，供卡片直接展示 ==========
            structured_data: resData.structured_data || {},
            timestamp: Date.now(),
          }
          console.log('aiMsg', aiMsg)
          this.chatMessages.push(aiMsg)
          this.saveChatHistory()
        } catch (error) {
          console.error('❌ 请求大模型异常:', error)
          const msg
            = error?.response?.data?.detail
              || error?.message
              || '请求失败：未知错误'

          this.chatMessages.push({
            role: 'ai',
            content: `⚠️ 调用失败：${msg}`,
            timestamp: Date.now(),
          })
        } finally {
          this.isLoading = false
          this.scrollToBottom()
        }
      },

      scrollToBottom () {
        this.$nextTick(() => {
          const chatHistory = this.$refs.chatHistory
          if (chatHistory) chatHistory.scrollTop = chatHistory.scrollHeight
        })
      },

      formatTime (timestamp) {
        const date = new Date(timestamp)
        const hours = String(date.getHours()).padStart(2, '0')
        const minutes = String(date.getMinutes()).padStart(2, '0')
        return `${hours}:${minutes}`
      },

      clearChat () {
        // 🌟 3. 清空数组，并同步移除 localStorage 中的缓存
        this.chatMessages = []
        this.saveChatHistory() // ✅ 清空也手动触发一次保存（相当于清空 localStorage）
      },
    },
  }
</script>

<style scoped>
/* 保持你原来的样式不变 */
.ai-chat-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #FAFAFA;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  scrollbar-width: thin;
  scrollbar-color: #DBD1EF transparent;
}

.welcome-tip {
  text-align: center;
  padding: 32px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  max-width: 400px;
  width: 100%;
  margin: auto;
}

.chat-list {
  width: 100%;
  max-width: 90%;
  margin: 0 auto;
}

.chat-item {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.user-chat {
  flex-direction: row-reverse;
}

.chat-avatar {
  background-color: #675096;
  margin: 0 6px;
  flex-shrink: 0;
}

.user-chat .chat-avatar {
  background-color: #742DD8;
}

.chat-content {
  display: flex;
  flex-direction: column;
}

.user-chat .chat-content {
  align-items: flex-end;
}

.chat-time {
  font-size: 11px;
  color: #AAA;
  margin-top: 4px;
  padding: 0 8px;
}

.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid #DBD1EF;
  background-color: #FAFAFA;
  box-shadow: 0 -1px 8px rgba(0, 0, 0, 0.05);
}

.loading-dots {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #742DD8;
  animation: dotBounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}
.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@media (max-width: 600px) {
  .chat-history { padding: 16px; }
  .chat-bubble { max-width: 90% !important; }
  .chat-input-area { padding: 12px 16px; }
  .welcome-tip { padding: 24px 16px; }
}

.chat-history::-webkit-scrollbar {
  width: 6px;
}
.chat-history::-webkit-scrollbar-thumb {
  background-color: #DBD1EF;
  border-radius: 3px;
}
</style>
