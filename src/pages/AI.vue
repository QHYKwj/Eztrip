<template>
  <div class="ai-chat-container">
    <!-- 顶部导航栏 -->
    <v-app-bar
      elevation="0"
      style="background-color: #F3F2FD; border-bottom: 1px solid #DBD1EF"
    >
      <v-app-bar-nav-icon @click="$router.go(-1)" style="color: #675096" />
      <v-toolbar-title style="color: #675096; font-weight: 600">
        AI 智能助手
      </v-toolbar-title>
      <v-spacer />
      <v-btn
        icon
        style="color: #675096"
        @click="clearChat"
        v-tooltip:left="'清空对话'"
      >
        <v-icon>mdi-trash-can-outline</v-icon>
      </v-btn>
    </v-app-bar>

    <!-- 对话历史区 -->
    <div class="chat-history" ref="chatHistory">
      <!-- 欢迎提示 -->
      <div v-if="chatMessages.length === 0" class="welcome-tip">
        <v-avatar size="64" style="background-color: #742DD8; margin-bottom: 16px">
          <v-icon size="32" color="white">mdi-robot</v-icon>
        </v-avatar>
        <h3 style="color: #444; margin-bottom: 8px">你好！我是你的 AI 助手</h3>
        <p style="color: #675096; font-size: 14px">
          有什么可以帮你的？比如生成行程、解答问题~
        </p>
      </div>

      <!-- 对话列表 -->
      <div v-else class="chat-list">
        <div
          v-for="(msg, index) in chatMessages"
          :key="index"
          :class="['chat-item', msg.role === 'user' ? 'user-chat' : 'ai-chat']"
        >
          <v-avatar size="40" class="chat-avatar">
            <v-icon color="white" size="20">
              {{ msg.role === 'user' ? 'mdi-account-circle' : 'mdi-robot' }}
            </v-icon>
          </v-avatar>
          <div class="chat-content">
            <div
              class="chat-bubble"
              :style="msg.role === 'user' ? userBubbleStyle : aiBubbleStyle"
            >
              <p :style="{ color: msg.role === 'user' ? 'white' : '#444' }">
                {{ msg.content }}
              </p>
            </div>
            <p class="chat-time">{{ formatTime(msg.timestamp) }}</p>
          </div>
        </div>

        <!-- AI 加载中状态 -->
        <div v-if="isLoading" class="chat-item ai-chat">
          <v-avatar size="40" class="chat-avatar">
            <v-icon color="white" size="20">mdi-robot</v-icon>
          </v-avatar>
          <div class="chat-content">
            <div class="chat-bubble" :style="aiBubbleStyle">
              <div class="loading-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
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
        <v-card-text>
          <v-textarea
            v-model="inputMessage"
            placeholder="输入你的问题或需求..."
            style="resize: none; color: #444; border: 1px solid #DBD1EF; border-radius: 8px; padding: 8px 12px"
            rows="1"
            max-rows="4"
            @keydown.enter.prevent="sendMessage"
            hide-details
          />
        </v-card-text>
        <v-card-actions style="justify-content: flex-end; padding: 8px 16px">
          <v-btn
            style="background-color: #742DD8; color: white"
            @click="sendMessage"
            rounded
            :disabled="!inputMessage.trim() || isLoading"
          >
            <v-icon left>mdi-paper-plane</v-icon>发送
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script>
export default {
  name: "AIChatPage",
  data() {
    return {
      chatMessages: [],
      inputMessage: "",
      isLoading: false,
      userBubbleStyle: {
        backgroundColor: "#742DD8",
        borderRadius: "16px 16px 4px 16px",
        padding: "12px 16px",
        maxWidth: "100%", // ✅ 扩宽气泡
        lineHeight: "1.6",
        wordBreak: "break-word",
        whiteSpace: "pre-wrap",
        boxShadow: "0 1px 4px rgba(0, 0, 0, 0.05)"
      },
      aiBubbleStyle: {
        backgroundColor: "#F3F2FD",
        border: "1px solid #DBD1EF",
        borderRadius: "16px 16px 16px 4px",
        padding: "12px 16px",
        maxWidth: "80%",
        lineHeight: "1.6",
        wordBreak: "break-word",
        whiteSpace: "pre-wrap",
        boxShadow: "0 1px 4px rgba(0, 0, 0, 0.05)"
      }
    };
  },
  methods: {
    sendMessage() {
      const content = this.inputMessage.trim();
      if (!content || this.isLoading) return;
      const userMsg = {
        role: "user",
        content,
        timestamp: new Date().getTime()
      };
      this.chatMessages.push(userMsg);
      this.inputMessage = "";
      this.scrollToBottom();
      this.isLoading = true;
      setTimeout(() => {
        const aiReply = this.getAIReply(content);
        const aiMsg = {
          role: "ai",
          content: aiReply,
          timestamp: new Date().getTime()
        };
        this.chatMessages.push(aiMsg);
        this.isLoading = false;
        this.scrollToBottom();
      }, 1500);
    },
    getAIReply(userInput) {
      const lowerInput = userInput.toLowerCase();
      if (lowerInput.includes("行程") || lowerInput.includes("旅游") || lowerInput.includes("旅行")) {
        return "为你推荐通用行程模板：\n1. 第一天：抵达目的地 → 入住酒店 → 晚上逛当地夜市\n2. 第二天：核心景点打卡（建议提前在官方平台预约门票）\n3. 第三天：体验当地美食 + 文化体验（如博物馆、民俗村）\n需要我帮你生成具体城市（如上海、三亚）的3天2晚行程吗？";
      } else if (lowerInput.includes("ai") || lowerInput.includes("智能") || lowerInput.includes("你是谁")) {
        return "我是你的专属 AI 助手，基于大语言模型开发～ 可以帮你：\n• 生成旅行行程\n• 解答日常问题\n• 整理笔记/文案\n• 提供生活建议\n你有具体需求可以详细告诉我哦！";
      } else if (lowerInput.includes("你好") || lowerInput.includes("hi") || lowerInput.includes("hello")) {
        return "你好呀！😊 很高兴能为你服务～ 有什么需要我帮忙的吗？可以试试让我帮你规划行程哦！";
      } else if (lowerInput.includes("天气") || lowerInput.includes("温度")) {
        return "抱歉，我目前无法获取实时天气～ 你可以告诉我具体城市和出行日期，我会帮你在行程中备注天气相关的注意事项（如带雨伞、防晒用品等）！";
      } else {
        return "感谢你的提问！我已经记录了你的需求～\n如果需要更精准的回答，可以补充更多细节（比如具体城市、出行天数、需求偏好等），我会为你提供更有针对性的帮助！";
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const chatHistory = this.$refs.chatHistory;
        if (chatHistory) chatHistory.scrollTop = chatHistory.scrollHeight;
      });
    },
    formatTime(timestamp) {
      const date = new Date(timestamp);
      const hours = String(date.getHours()).padStart(2, "0");
      const minutes = String(date.getMinutes()).padStart(2, "0");
      return `${hours}:${minutes}`;
    },
    clearChat() {
      this.chatMessages = [];
    }
  }
};
</script>

<style scoped>
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
  .chat-bubble { max-width: 85% !important; }
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
