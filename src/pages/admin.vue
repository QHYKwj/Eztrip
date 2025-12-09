<template>
  <div class="admin-container">
    <!-- 顶部导航栏（移除侧边栏切换按钮） -->
    <v-app-bar
      elevation="0"
      style="background-color: #F3F2FD; border-bottom: 1px solid #DBD1EF; z-index: 10"
    >
      <v-toolbar-title style="color: #675096; font-weight: 600; margin-left: 16px;">
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
        style="background-color: #e53935; color: white; margin-left: 10px; margin-right: 16px;"
        @click="logout"
      >
        <v-icon left>mdi-logout</v-icon>登出
      </v-btn>
    </v-app-bar>

    <!-- 布局：左侧固定导航栏 + 右侧主内容 -->
    <div class="admin-layout">
      <!-- 左侧导航栏（固定不可收起） -->
      <v-navigation-drawer
        :width="250"
        style="background-color: #F3F2FD; border-right: 1px solid #DBD1EF"
        permanent
        fixed
      >
        <v-list>
          <v-list-item
            v-for="(item, index) in sidebarItems"
            :key="index"
            @click="activeSidebarItem = index"
            :class="activeSidebarItem === index ? 'selected-item' : ''"
            style="height: 60px;"
          >
            <v-list-item-icon style="color: #675096">
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title style="color: #675096">{{ item.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <!-- 主体内容区（避开导航栏遮挡） -->
      <v-container fluid class="admin-content">
        <!-- 统计卡片 -->
        <v-row class="stats-row" style="margin-top: 24px;">
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
                  <v-icon>mdi-delete-outline</v-icon>
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

          <!-- 公告管理面板 -->
          <v-card-text v-if="activeSidebarItem === 2">
            <!-- 搜索和操作区 -->
            <div class="user-controls">
              <v-text-field
                v-model="announcementSearch"
                label="搜索公告"
                prepend-icon="mdi-magnify"
                style="width: 300px;"
              />
              <v-btn
                style="background-color: #742DD8; color: white;"
                @click="openAnnouncementDialog"
              >
                <v-icon left>mdi-plus</v-icon>发布公告
              </v-btn>
            </div>

            <!-- 公告表格 -->
            <v-data-table
              :items="announcements"
              :search="announcementSearch"
              :headers="announcementHeaders"
              class="announcement-table"
              item-key="id"
              :items-per-page-options="[10, 20, 50]"
            >
              <template v-slot:item.published="{ item }">
                <v-chip :color="item.published ? 'green' : 'grey'">
                  {{ item.published ? '已发布' : '草稿' }}
                </v-chip>
              </template>
            <template v-slot:item.actions="{ item }">
              <div style="display:flex; gap:12px; align-items:center;">
                <v-btn icon small @click="editAnnouncement(item)" style="color: #675096;">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>

                <v-btn icon small @click="deleteAnnouncement(item.id)" style="color: #e53935;">
                  <v-icon>mdi-delete-outline</v-icon>
                </v-btn>

                <v-btn
              small
              @click="toggleAnnouncementStatus(item)"
              :style="{
                backgroundColor: item.published ? '#f57c00' : '#43a047',
                color: 'white',
                marginLeft: '24px'  // 注意这里是驼峰式命名（marginLeft）
              }"
            >
              {{ item.published ? '取消发布' : '发布' }}
            </v-btn>
  </div>
</template>
            </v-data-table>
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

    <!-- 公告编辑对话框 -->
    <v-dialog v-model="announcementDialogOpen" max-width="800px">
      <v-card>
        <v-card-title>{{ editingAnnouncement ? '编辑公告' : '发布公告' }}</v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="currentAnnouncement.title"
              label="公告标题"
              required
              full-width
            />
            <v-textarea
              v-model="currentAnnouncement.content"
              label="公告内容"
              required
              rows="8"
              full-width
              style="margin-top: 16px;"
            />
            <v-switch
              v-model="currentAnnouncement.published"
              label="立即发布"
              color="#742DD8"
              style="margin-top: 16px;"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="announcementDialogOpen = false">取消</v-btn>
          <v-btn
            style="background-color: #742DD8; color: white;"
            @click="saveAnnouncement"
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
      // 状态管理（移除sidebarOpen）
      activeSidebarItem: 0,
      searchQuery: "",
      announcementSearch: "",
      unreadNotifications: 3,
      userDialogOpen: false,
      announcementDialogOpen: false,
      editingUser: null,
      editingAnnouncement: null,

      // 侧边栏项目
      sidebarItems: [
        { title: "用户管理", icon: "mdi-account" },
        { title: "内容审核", icon: "mdi-file-check" },
        { title: "公告管理", icon: "mdi-bullhorn" }
      ],

      // 统计数据
      stats: [
        { title: "总用户数", value: 1280, change: 12 },
        { title: "今日新增", value: 24, change: 8 },
        { title: "内容总数", value: 3560, change: 5 },
        { title: "待审核内容", value: 12, change: -3 }
      ],

      // 用户/内容/公告数据（保持不变）
      users: [
        { id: 1, username: "john_doe", email: "john@example.com", role: "admin", status: true, registered: "2024-01-15" },
        { id: 2, username: "jane_smith", email: "jane@example.com", role: "user", status: true, registered: "2024-02-20" },
        { id: 3, username: "mike_brown", email: "mike@example.com", role: "moderator", status: false, registered: "2024-03-05" }
      ],
      contents: [
        { id: 1, title: "三亚旅行攻略", author: "jane_smith", type: "article", status: "pending", created: "2024-05-10" },
        { id: 2, title: "北京美食推荐", author: "mike_brown", type: "article", status: "approved", created: "2024-05-09" },
        { id: 3, title: "上海行程规划", author: "john_doe", type: "plan", status: "rejected", created: "2024-05-08" }
      ],
      announcements: [
        { id: 1, title: "系统维护通知", content: "本系统将于5月20日进行维护，届时可能无法正常访问，敬请谅解。", published: true, created: "2024-05-15", updated: "2024-05-15" },
        { id: 2, title: "新功能上线公告", content: "我们新增了用户积分系统，欢迎大家体验！", published: true, created: "2024-05-10", updated: "2024-05-10" },
        { id: 3, title: "端午节活动策划", content: "端午节将举办线上答题活动，奖品丰富，敬请期待...", published: false, created: "2024-05-05", updated: "2024-05-06" }
      ],

      // 表格头部（保持不变）
      userHeaders: [
        { text: "ID", value: "id", sortable: true, align: "start" },
        { text: "用户名", value: "username", sortable: true, align: "start" },
        { text: "邮箱", value: "email", sortable: true, align: "start" },
        { text: "角色", value: "role", sortable: true, align: "center" },
        { text: "状态", value: "status", sortable: true, align: "center" },
        { text: "注册日期", value: "registered", sortable: true, align: "center" },
        { text: "操作", value: "actions", sortable: false, align: "center" }
      ],
      contentHeaders: [
        { text: "ID", value: "id", sortable: true, align: "start" },
        { text: "标题", value: "title", sortable: true, align: "start" },
        { text: "作者", value: "author", sortable: true, align: "center" },
        { text: "类型", value: "type", sortable: true, align: "center" },
        { text: "状态", value: "status", sortable: true, align: "center" },
        { text: "创建日期", value: "created", sortable: true, align: "center" },
        { text: "操作", value: "actions", sortable: false, align: "center" }
      ],
      announcementHeaders: [
        { text: "ID", value: "id", sortable: true, align: "start" },
        { text: "标题", value: "title", sortable: true, align: "start" },
        { text: "状态", value: "published", sortable: true, align: "center" },
        { text: "创建日期", value: "created", sortable: true, align: "center" },
        { text: "更新日期", value: "updated", sortable: true, align: "center" },
        { text: "操作", value: "actions", sortable: false, align: "center" }
      ],

      // 当前编辑对象（保持不变）
      currentUser: {
        username: "",
        email: "",
        role: "user",
        status: true
      },
      currentAnnouncement: {
        title: "",
        content: "",
        published: false
      },

      // 系统设置（保持不变）
      settings: {
        enableRegistration: true,
        enableGuestAccess: false,
        sessionTimeout: 30,
        maxFileSize: 20
      }
    };
  },
  methods: {
    // 移除toggleSidebar方法（无需收起侧边栏）

    // 登出功能（保持不变）
    logout() {
      // 删除登录信息
      sessionStorage.removeItem('user')

      // 跳转到登录页面
      this.$router.push('/login')
    },

    // 其他方法（刷新、用户/内容/公告管理等保持不变）
    refreshData() {
      this.$toast.success("数据已刷新");
    },
    showNotifications() {
      this.unreadNotifications = 0;
    },
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
        const index = this.users.findIndex(u => u.id === this.editingUser);
        this.users.splice(index, 1, this.currentUser);
      } else {
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
      console.log(`用户 ${user.username} 状态已更新为 ${user.status ? '启用' : '禁用'}`);
    },
    approveContent(id) {
      const content = this.contents.find(c => c.id === id);
      if (content) content.status = "approved";
    },
    rejectContent(id) {
      const content = this.contents.find(c => c.id === id);
      if (content) content.status = "rejected";
    },
    saveSettings() {
      this.$toast.success("设置已保存");
    },
    openAnnouncementDialog() {
      this.editingAnnouncement = null;
      this.currentAnnouncement = { title: "", content: "", published: false };
      this.announcementDialogOpen = true;
    },
    editAnnouncement(announcement) {
      this.editingAnnouncement = announcement.id;
      this.currentAnnouncement = { ...announcement };
      this.announcementDialogOpen = true;
    },
    saveAnnouncement() {
      const currentDate = new Date().toISOString().split("T")[0];
      if (this.editingAnnouncement) {
        const index = this.announcements.findIndex(a => a.id === this.editingAnnouncement);
        this.currentAnnouncement.updated = currentDate;
        this.announcements.splice(index, 1, this.currentAnnouncement);
      } else {
        this.currentAnnouncement.id = Date.now();
        this.currentAnnouncement.created = currentDate;
        this.currentAnnouncement.updated = currentDate;
        this.announcements.push(this.currentAnnouncement);
      }
      this.announcementDialogOpen = false;
      this.$toast.success(this.editingAnnouncement ? "公告已更新" : "公告已发布");
    },
    deleteAnnouncement(id) {
      if (confirm("确定要删除这个公告吗？")) {
        this.announcements = this.announcements.filter(announcement => announcement.id !== id);
        this.$toast.success("公告已删除");
      }
    },
    toggleAnnouncementStatus(announcement) {
      announcement.published = !announcement.published;
      announcement.updated = new Date().toISOString().split("T")[0];
      this.$toast.success(`公告已${announcement.published ? '发布' : '取消发布'}`);
    }
  }
};
</script>

<style scoped>
::v-deep .v-data-table thead {
  display: table-header-group !important; /* 强制渲染表头组 */
  visibility: visible !important;
}

::v-deep .v-data-table th.v-data-table-header__cell {
  display: table-cell !important;
  height: 56px !important; /* 标准表头高度 */
  min-height: 56px !important;
  padding: 0 16px !important; /* 内边距，避免文字截断 */
  color: #675096 !important; /* 主题色 */
  font-weight: 600 !important;
  border-bottom: 2px solid #DBD1EF !important; /* 表头底部边框，醒目 */
}

/* 表格内容垂直居中，避免布局错乱 */
::v-deep .v-data-table td.v-data-table__cell {
  vertical-align: middle !important;
  padding: 12px 16px !important;
}

/* 修复公告表格操作列拥挤问题（之前 150px 导致布局错乱） */
::v-deep .announcement-table .v-data-table__cell:last-child {
  min-width: 200px !important; /* 给操作列留足够宽度 */
}

.action-group {
  display: flex;
  gap: 12px; /* 按钮之间保持固定间距 */
}

.action-btn {
  margin-left: 12px;
}

.admin-container {
  min-height: 100vh;
  background-color: #FAFAFA;
}

.admin-layout {
  display: flex;
}

/* 解决内容被遮挡问题 */
.admin-content {
  padding: 24px;
  margin-left: 250px; /* Drawer */
  margin-top: 64px;   /* AppBar */
  width: calc(100% - 250px);
  box-sizing: border-box;
}
/* 左侧导航栏固定宽度，不收缩 */
.v-navigation-drawer {
  width: 250px !important;
  flex-shrink: 0;
  height: calc(100vh - 64px) !important; /* 与主内容区高度一致 */
}

/* 主内容区：避开左侧导航栏 + 顶部间距 */
.admin-content {
  padding: 24px 32px;
  flex: 1;
  max-width: calc(100% - 250px); /* 减去左侧导航栏宽度 */
  width: 100%;
  box-sizing: border-box;
}

/* 统计卡片样式（保持不变） */
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

/* 内容区域样式（保持不变） */
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

/* 通知角标（保持不变） */
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

/* 侧边栏选中项样式（保持不变） */
.selected-item {
  background-color: rgba(116, 45, 216, 0.1);
  border-right: 4px solid #742DD8;
}

/* 响应式适配（保持不变） */
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
