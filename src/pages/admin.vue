<template>
  <div class="admin-container">
    <!-- 顶部导航栏 -->
    <v-app-bar
      elevation="0"
      style="background-color: #F3F2FD; border-bottom: 1px solid #DBD1EF; z-index: 10"
    >
      <v-app-bar-nav-icon @click="toggleSidebar" style="color: #675096" />
      <v-toolbar-title style="color: #675096; font-weight: 600">
        管理员中心
      </v-toolbar-title>
      <v-spacer />
      <v-btn
        icon
        style="color: #675096"
        @click="refreshData"
        v-tooltip:left="'刷新数据'"
      >
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
      <v-btn
        icon
        style="color: #675096"
        @click="showNotifications"
        v-tooltip:left="'通知'"
      >
        <v-icon>mdi-bell</v-icon>
        <span v-if="unreadNotifications" class="notification-badge">
          {{ unreadNotifications }}
        </span>
      </v-btn>
      <v-btn
        style="background-color: #e53935; color: white; margin-left: 10px"
        @click="logout"
      >
        <v-icon left>mdi-logout</v-icon>登出
      </v-btn>
    </v-app-bar>

    <div class="admin-layout">
      <!-- 侧边导航栏 -->
      <v-navigation-drawer
        v-model="sidebarOpen"
        :width="250"
        style="background-color: #F3F2FD; border-right: 1px solid #DBD1EF"
        permanent
      >
        <v-list>
          <v-list-item
            v-for="(item, index) in sidebarItems"
            :key="index"
            @click="activeSidebarItem = index"
            :class="activeSidebarItem === index ? 'selected-item' : ''"
          >
            <v-list-item-icon style="color: #675096">
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title style="color: #675096">{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <!-- 主体内容区 -->
      <v-container fluid class="admin-content">
        <!-- 统计卡片 -->
        <v-row class="stats-row">
          <v-col cols="12" sm="6" md="3" v-for="(stat, index) in stats" :key="index">
            <v-card class="stat-card" outlined>
              <v-card-title style="color: #675096; font-size: 16px">
                {{ stat.title }}
              </v-card-title>
              <v-card-text>
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-change" :class="stat.change > 0 ? 'positive' : 'negative'">
                  {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 内容区域 -->
        <v-card class="admin-card" outlined style="margin-top: 24px;">
          <!-- 用户管理面板 -->
          <v-card-text v-if="activeSidebarItem === 0">
            <!-- 搜索和操作区 -->
            <div class="user-controls">
              <v-text-field
                v-model="searchQuery"
                label="搜索用户"
                prepend-icon="mdi-magnify"
                style="width: 300px;"
              />
              <v-btn
                style="background-color: #742DD8; color: white;"
                @click="openUserDialog"
              >
                <v-icon left>mdi-plus</v-icon>添加用户
              </v-btn>
            </div>

            <!-- 用户表格 -->
            <v-data-table
              :items="users"
              :search="searchQuery"
              :headers="userHeaders"
              class="user-table"
              item-key="id"
              :items-per-page-options="[10, 20, 50]"
            >
              <template v-slot:item.status="{ item }">
                <v-switch
                  v-model="item.status"
                  :label="item.status ? '启用' : '禁用'"
                  color="#742DD8"
                  @change="updateUserStatus(item)"
                />
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  small
                  @click="editUser(item)"
                  style="color: #675096;"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  icon
                  small
                  @click="deleteUser(item.id)"
                  style="color: #e53935;"
                >
                  <v-icon>mdi-trash</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>

          <!-- 内容审核面板 -->
          <v-card-text v-if="activeSidebarItem === 1">
            <v-data-table
              :items="contents"
              :headers="contentHeaders"
              class="content-table"
              item-key="id"
              :items-per-page-options="[10, 20, 50]"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="item.status === 'pending' ? 'orange' : item.status === 'approved' ? 'green' : 'red'">
                  {{ item.status === 'pending' ? '待审核' : item.status === 'approved' ? '已通过' : '已拒绝' }}
                </v-chip>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn
                  small
                  @click="approveContent(item.id)"
                  style="background-color: #43a047; color: white; margin-right: 4px;"
                  v-if="item.status === 'pending'"
                >
                  通过
                </v-btn>
                <v-btn
                  small
                  @click="rejectContent(item.id)"
                  style="background-color: #e53935; color: white;"
                  v-if="item.status === 'pending'"
                >
                  拒绝
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>

          <!-- 系统设置面板 -->
          <v-card-text v-if="activeSidebarItem === 2">
            <v-form>
              <v-checkbox
                v-model="settings.enableRegistration"
                label="允许新用户注册"
                color="#742DD8"
              />
              <v-checkbox
                v-model="settings.enableGuestAccess"
                label="允许游客访问"
                color="#742DD8"
              />
              <v-slider
                v-model="settings.sessionTimeout"
                label="会话超时时间 (分钟)"
                min="5"
                max="120"
                step="5"
                color="#742DD8"
                style="margin-top: 16px;"
              />
              <v-text-field
                v-model="settings.maxFileSize"
                label="最大文件上传大小 (MB)"
                type="number"
                min="1"
                max="100"
                style="margin-top: 16px;"
              />
              <v-btn
                style="background-color: #742DD8; color: white; margin-top: 24px;"
                @click="saveSettings"
              >
                <v-icon left>mdi-save</v-icon>保存设置
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-container>
    </div>

    <!-- 用户编辑对话框 -->
    <v-dialog v-model="userDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>{{ editingUser ? '编辑用户' : '添加用户' }}</v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="currentUser.username"
              label="用户名"
              required
            />
            <v-text-field
              v-model="currentUser.email"
              label="邮箱"
              type="email"
              required
            />
            <v-select
              v-model="currentUser.role"
              label="角色"
              :items="['admin', 'user', 'moderator']"
              required
            />
            <v-switch
              v-model="currentUser.status"
              label="启用账号"
              color="#742DD8"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="userDialogOpen = false">取消</v-btn>
          <v-btn
            style="background-color: #742DD8; color: white;"
            @click="saveUser"
          >
            保存
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  name: "AdminPanel",
  data() {
    return {
      // 状态管理
      sidebarOpen: true,
      activeSidebarItem: 0,
      searchQuery: "",
      unreadNotifications: 3,
      userDialogOpen: false,
      editingUser: null,
      
      // 侧边栏项目
      sidebarItems: [
        { title: "用户管理", icon: "mdi-account" },
        { title: "内容审核", icon: "mdi-file-check" },
        { title: "系统设置", icon: "mdi-cog" }
      ],
      
      // 统计数据
      stats: [
        { title: "总用户数", value: 1280, change: 12 },
        { title: "今日新增", value: 24, change: 8 },
        { title: "内容总数", value: 3560, change: 5 },
        { title: "待审核内容", value: 12, change: -3 }
      ],
      
      // 用户数据
      users: [
        { id: 1, username: "john_doe", email: "john@example.com", role: "admin", status: true, registered: "2024-01-15" },
        { id: 2, username: "jane_smith", email: "jane@example.com", role: "user", status: true, registered: "2024-02-20" },
        { id: 3, username: "mike_brown", email: "mike@example.com", role: "moderator", status: false, registered: "2024-03-05" }
      ],
      
      // 内容数据
      contents: [
        { id: 1, title: "三亚旅行攻略", author: "jane_smith", type: "article", status: "pending", created: "2024-05-10" },
        { id: 2, title: "北京美食推荐", author: "mike_brown", type: "article", status: "approved", created: "2024-05-09" },
        { id: 3, title: "上海行程规划", author: "john_doe", type: "plan", status: "rejected", created: "2024-05-08" }
      ],
      
      // 表格头部
      userHeaders: [
        { text: "ID", value: "id" },
        { text: "用户名", value: "username" },
        { text: "邮箱", value: "email" },
        { text: "角色", value: "role" },
        { text: "状态", value: "status" },
        { text: "注册日期", value: "registered" },
        { text: "操作", value: "actions", sortable: false }
      ],
      
      contentHeaders: [
        { text: "ID", value: "id" },
        { text: "标题", value: "title" },
        { text: "作者", value: "author" },
        { text: "类型", value: "type" },
        { text: "状态", value: "status" },
        { text: "创建日期", value: "created" },
        { text: "操作", value: "actions", sortable: false }
      ],
      
      // 当前编辑的用户
      currentUser: {
        username: "",
        email: "",
        role: "user",
        status: true
      },
      
      // 系统设置
      settings: {
        enableRegistration: true,
        enableGuestAccess: false,
        sessionTimeout: 30,
        maxFileSize: 20
      }
    };
  },
  methods: {
    // 切换侧边栏
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    },
    
    // 登出功能
    logout() {
      // 实际项目中这里应该清除用户登录状态
      this.$router.push('/login');
    },
    
    // 刷新数据
    refreshData() {
      // 实际项目中这里会调用API刷新数据
      this.$toast.success("数据已刷新");
    },
    
    // 显示通知
    showNotifications() {
      this.unreadNotifications = 0;
      // 显示通知面板逻辑
    },
    
    // 用户管理相关方法
    openUserDialog() {
      this.editingUser = null;
      this.currentUser = { username: "", email: "", role: "user", status: true };
      this.userDialogOpen = true;
    },
    
    editUser(user) {
      this.editingUser = user.id;
      this.currentUser = { ...user };
      this.userDialogOpen = true;
    },
    
    saveUser() {
      if (this.editingUser) {
        // 更新现有用户
        const index = this.users.findIndex(u => u.id === this.editingUser);
        this.users.splice(index, 1, this.currentUser);
      } else {
        // 添加新用户
        this.currentUser.id = Date.now();
        this.currentUser.registered = new Date().toISOString().split("T")[0];
        this.users.push(this.currentUser);
      }
      this.userDialogOpen = false;
    },
    
    deleteUser(id) {
      if (confirm("确定要删除这个用户吗？")) {
        this.users = this.users.filter(user => user.id !== id);
      }
    },
    
    updateUserStatus(user) {
      // 实际项目中这里会调用API更新用户状态
      console.log(`用户 ${user.username} 状态已更新为 ${user.status ? '启用' : '禁用'}`);
    },
    
    // 内容审核相关方法
    approveContent(id) {
      const content = this.contents.find(c => c.id === id);
      if (content) content.status = "approved";
    },
    
    rejectContent(id) {
      const content = this.contents.find(c => c.id === id);
      if (content) content.status = "rejected";
    },
    
    // 系统设置相关方法
    saveSettings() {
      // 实际项目中这里会调用API保存设置
      this.$toast.success("设置已保存");
    }
  }
};
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  background-color: #FAFAFA;
}

.admin-layout {
  display: flex;
  min-height: calc(100vh - 64px);
}

.admin-content {
  padding: 24px;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-color: #DBD1EF;
  background-color: white;
  height: 100%;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #444;
}

.stat-change {
  font-size: 14px;
  margin-top: 4px;
}

.positive {
  color: #43a047;
}

.negative {
  color: #e53935;
}

.admin-card {
  border-color: #DBD1EF;
  background-color: white;
}

.user-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 16px;
}

.notification-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #e53935;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selected-item {
  background-color: rgba(116, 45, 216, 0.1);
  border-right: 4px solid #742DD8;
}

@media (max-width: 600px) {
  .admin-content {
    padding: 16px;
  }
  
  .user-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .v-text-field {
    width: 100% !important;
  }
}
</style>