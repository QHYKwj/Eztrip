<template>
  <div class="profile-container">
    <!-- 顶部导航栏（保持不变） -->
    <v-app-bar
      elevation="0"
      style="background-color: #F3F2FD; border-bottom: 1px solid #DBD1EF"
    >
      <v-app-bar-nav-icon @click="$router.go(-1)" style="color: #675096" />
      <v-toolbar-title style="color: #675096; font-weight: 600">个人信息</v-toolbar-title>
    </v-app-bar>

    <!-- 主体内容区：新增顶部内边距，整体向下挪 -->
    <v-container fluid class="profile-content">
      <!-- 1. 头像与基础信息区（已随容器整体下移） -->
      <div class="profile-header">
        <div class="avatar-border">
          <v-img
            class="rounded-circle"
            src="https://randomuser.me/api/portraits/men/85.jpg"
            width="120"
            height="120"
          />
        </div>

        <div class="profile-basic">
          <h2 class="profile-name" style="color: #444">John Leider</h2>
          <p class="profile-role" style="color: #675096">普通用户</p>
        </div>

        <div class="profile-btn-group">
          <v-btn
            style="background-color: #742DD8; color: white; margin-right: 8px"
            @click="handleEdit"
            rounded
            size="small"
          >
            <v-icon left>mdi-pencil</v-icon>编辑信息
          </v-btn>

          <v-btn
            style="background-color: #675096; color: white; border: 1px solid #DBD1EF"
            @click="goToLogin"
            rounded
            size="small"
          >
            <v-icon left>mdi-login</v-icon>去登录
          </v-btn>
        </div>
      </div>

      <!-- 2. 信息卡片组（随容器下移，与头像保持原有间距） -->
      <v-card
        class="profile-card"
        outlined
        style="border-color: #DBD1EF; margin-top: 24px"
      >
        <v-card-title style="color: #675096; font-weight: 500">
          <v-icon left>mdi-account-details</v-icon>基本信息
        </v-card-title>
        <v-card-text>
          <v-list dense>
            <v-list-item>
              <v-list-item-icon style="color: #675096">
                <v-icon>mdi-phone</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title style="color: #444">+1 (555) 765-4321</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon style="color: #675096">
                <v-icon>mdi-email</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title style="color: #444">john.leider@example.com</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-list-item>
              <v-list-item-icon style="color: #675096">
                <v-icon>mdi-calendar-plus</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title style="color: #444">2024-01-15</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
      </v-card>

      <v-card
        class="profile-card"
        outlined
        style="border-color: #DBD1EF; margin-top: 16px"
      >
        <v-card-title style="color: #675096; font-weight: 500">
          <v-icon left>mdi-map-location-dot</v-icon>行程统计
        </v-card-title>
        <v-card-text>
          <div class="stats-grid">
            <div class="stat-item">
              <p class="stat-value" style="color: #742DD8; font-size: 24px; font-weight: 600">12</p>
              <p class="stat-label" style="color: #444">已完成行程</p>
            </div>
            <div class="stat-item">
              <p class="stat-value" style="color: #742DD8; font-size: 24px; font-weight: 600">3</p>
              <p class="stat-label" style="color: #444">待出发行程</p>
            </div>
            <div class="stat-item">
              <p class="stat-value" style="color: #742DD8; font-size: 24px; font-weight: 600">8</p>
              <p class="stat-label" style="color: #444">收藏地点</p>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-container>
  </div>
</template>

<script>
export default {
  name: "ProfilePage",
  methods: {
    handleEdit() {
      alert("进入编辑模式（实际项目中可替换为弹窗/路由跳转）");
    },
    goToLogin() {
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
/* 页面容器：保持基础样式 */
.profile-container {
  min-height: 100vh;
  background-color: #FAFAFA;
}

/* 核心修改：增加顶部内边距，让内容整体向下挪（可根据需求调整 px 值） */
.profile-content {
  padding: 79px 24px 24px; /* 上内边距从 24px 改为 60px，上下右保持原间距 */
  max-width: 800px;
  margin: 0 auto;
}

/* 头像样式（不变） */
.avatar-border {
  border: 3px solid white;
  border-radius: 50%;
  padding: 3px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 头部信息布局（不变） */
.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.profile-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-basic {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 统计卡片网格布局（不变） */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 24px;
  text-align: center;
}

/* 移动端适配（不变） */
@media (max-width: 600px) {
  .profile-header {
    justify-content: center;
    text-align: center;
  }
  .profile-btn-group {
    flex-direction: column;
    width: 100%;
    max-width: 200px;
  }
  /* 移动端可适当减少顶部内边距，避免内容太靠下 */
  .profile-content {
    padding-top: 60px;
  }
}
</style>