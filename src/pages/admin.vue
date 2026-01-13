<template>
  <div class="admin-container">
    <!-- 顶部导航栏 -->
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
      <!-- 左侧导航栏 -->
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

      <!-- 主体内容区 -->
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
                  <!-- 这里的change逻辑如果是假数据可以先隐藏或保留 -->
                  <span v-if="stat.change !== 0">
                     {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
                  </span>
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
              <!-- 【已删除】这里删除了添加用户按钮 -->
            </div>

            <!-- 用户表格 -->
            <v-data-table
              :items="users"
              :search="searchQuery"
              :headers="userHeaders"
              class="user-table"
              item-key="user_id" 
              :items-per-page-options="[10, 20, 50]"
              :loading="userLoading"
            >
              <template v-slot:item.status="{ item }">
                <!-- 状态开关：对接 update_user_status -->
                <v-switch
                  v-model="item.statusBoolean"
                  :label="item.statusBoolean ? '启用' : '禁用'"
                  color="#742DD8"
                  @change="updateUserStatus(item)"
                  inset
                />
              </template>
              <template v-slot:item.actions="{ item }">
                <!-- 编辑按钮（保留功能，暂不对接复杂编辑） -->
                <v-btn
                  icon
                  small
                  @click="editUser(item)"
                  style="color: #675096;"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <!-- 删除按钮 -->
                <v-btn
                  icon
                  small
                  @click="deleteUser(item.user_id)"
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
              item-key="trip_id"
              :items-per-page-options="[10, 20, 50]"
              :loading="loading"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.publish_status)">
                  {{ getStatusText(item.publish_status) }}
                </v-chip>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn
                  small
                  @click="handleReview(item.trip_id, 'accept')"
                  style="background-color: #43a047; color: white; margin-right: 4px;"
                  v-if="item.publish_status === 'pending'"
                  :disabled="auditingIds.includes(item.trip_id)"
                >
                  <v-icon v-if="auditingIds.includes(item.trip_id)" small>mdi-loading</v-icon>
                  通过
                </v-btn>
                <v-btn
                  small
                  @click="handleReview(item.trip_id, 'reject')"
                  style="background-color: #e53935; color: white;"
                  v-if="item.publish_status === 'pending'"
                  :disabled="auditingIds.includes(item.trip_id)"
                >
                  <v-icon v-if="auditingIds.includes(item.trip_id)" small>mdi-loading</v-icon>
                  拒绝
                </v-btn>
              </template>
              <template v-slot:no-data>
                <v-alert type="info" border="start" color="#675096">暂无待审核的行程数据</v-alert>
              </template>
            </v-data-table>
          </v-card-text>

          <!-- 公告管理面板 -->
          <v-card-text v-if="activeSidebarItem === 2">
            <div class="user-controls">
              <v-btn
                style="background-color: #742DD8; color: white;"
                @click="openAnnouncementDialog"
              >
                <v-icon left>mdi-plus</v-icon>创建公告
              </v-btn>
            </div>

            <!-- 公告表格-->
            <v-data-table
              :items="announcements"
              :headers="announcementHeaders"
              class="announcement-table"
              item-key="notice_id"
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
                  <v-btn icon small @click="deleteAnnouncement(item.notice_id)" style="color: #e53935;">
                    <v-icon>mdi-delete-outline</v-icon>
                  </v-btn>
                  <v-btn
                    small
                    @click="toggleAnnouncementStatus(item)"
                    :style="{
                      backgroundColor: item.published ? '#f57c00' : '#43a047',
                      color: 'white',
                      marginLeft: '24px'
                    }"
                  >
                    {{ item.published ? '取消发布' : '发布' }}
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-card-text>

          <!-- 公告编辑对话框 -->
          <v-dialog v-model="announcementDialogOpen" max-width="800px">
            <v-card>
              <v-card-title>{{ editingAnnouncement ? '编辑公告' : '创建公告' }}</v-card-title>
              <v-card-text>
                <v-form>
                  <v-text-field
                    v-model="currentAnnouncement.title"
                    label="公告标题"
                    required
                    full-width
                    placeholder="请输入公告标题"
                  />
                  <v-textarea
                    v-model="currentAnnouncement.content"
                    label="公告内容"
                    required
                    rows="8"
                    full-width
                    placeholder="请输入公告详细内容"
                    style="margin-top: 16px;"
                  />
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-btn @click="announcementDialogOpen = false">取消</v-btn>
                <v-btn
                  style="background-color: #742DD8; color: white;"
                  @click="saveAnnouncement"
                  :disabled="announcementLoading"
                >
                  <v-icon v-if="announcementLoading" small>mdi-loading</v-icon>
                  保存
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-card>
      </v-container>
    </div>

    <!-- 用户编辑对话框 (虽然删除了添加按钮，但保留编辑功能) -->
    <v-dialog v-model="userDialogOpen" max-width="500px">
      <v-card>
        <v-card-title>编辑用户</v-card-title>
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="currentUser.username"
              label="用户名"
              disabled
            />
            <v-text-field
              v-model="currentUser.email"
              label="邮箱"
              type="email"
              disabled
            />
            <!-- 如果有更新用户信息的接口再启用这些编辑 -->
            <v-switch
              v-model="currentUser.statusBoolean"
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
            保存状态
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "AdminPanel",
  data() {
    return {
      // 基础状态
      activeSidebarItem: 0,
      searchQuery: "",
      unreadNotifications: 3,
      userDialogOpen: false,
      announcementDialogOpen: false,
      editingUser: null,
      editingAnnouncement: null,
      announcementLoading: false,

      // 加载状态
      loading: false,          
      userLoading: false,      // 用户列表加载状态
      
      auditingIds: [],         
      contents: [],            

      sidebarItems: [
        { title: "用户管理", icon: "mdi-account" },
        { title: "内容审核", icon: "mdi-file-check" },
        { title: "公告管理", icon: "mdi-bullhorn" }
      ],

      // 统计数据
      stats: [
        { title: "总用户数", value: 0, change: 0 },
        { title: "今日新增内容", value: 0, change: 0 },
        { title: "内容总数", value: 0, change: 0 },
        { title: "待审核内容", value: 0, change: 0 } // 这个将动态加载
      ],

      // 用户数据
      users: [], 

      // 公告数据
      announcements: [],
      currentAnnouncement: {
        title: "",
        content: "",
        notice_id: null
      },

      // 表格头部配置（适配后端字段）
      // ✅ 修正：字段改为 user_id
      userHeaders: [
        { text: "ID", value: "user_id", sortable: true, align: "start" },
        { text: "用户名", value: "username", sortable: true, align: "start" },
        { text: "邮箱", value: "email", sortable: true, align: "start" },
        { text: "角色", value: "role", sortable: true, align: "center" }, // 假设后端有role字段，没有则显示空
        { text: "状态", value: "status", sortable: true, align: "center" },
        { text: "操作", value: "actions", sortable: false, align: "center" }
      ],
      contentHeaders: [
        { text: "行程ID", value: "trip_id", sortable: true, align: "start" },
        { text: "行程标题", value: "title", sortable: true, align: "start" },
        { text: "发布用户", value: "username", sortable: true, align: "center" },
        { text: "目的地", value: "destination", sortable: true, align: "center" },
        { text: "审核状态", value: "publish_status", sortable: true, align: "center" },
        { text: "提交时间", value: "create_time", sortable: true, align: "center" },
        { text: "操作", value: "actions", sortable: false, align: "center" }
      ],
      announcementHeaders: [
        { text: "公告ID", value: "notice_id", sortable: true, align: "start" },
        { text: "公告标题", value: "title", sortable: true, align: "start" },
        { text: "发布时间", value: "created_at", sortable: true, align: "center" },
        { text: "发布状态", value: "published", sortable: true, align: "center" },
        { text: "操作", value: "actions", sortable: false, align: "center" }
      ],

      currentUser: {
        username: "",
        email: "",
        role: "user",
        statusBoolean: true
      },
    };
  },
  created() {
    // 页面初始化时加载所有数据
    this.refreshData();
  },
  methods: {
    // ========== 基础功能 ==========
    logout() {
      sessionStorage.removeItem('user');
      this.$router.push('/login');
    },
    refreshData() {
      this.loadDashboardStats(); // 加载统计
      this.loadAllUsers();       // 加载用户
      this.loadPendingTrips();   // 加载审核
      this.loadAllAnnouncements(); // 加载公告
      this.$toast?.success("数据已刷新");
    },
    showNotifications() {
      this.unreadNotifications = 0;
    },

    // ========== 1. 统计面板对接 ==========
// ========== 1. 统计面板对接 (修改后) ==========
   // ========== 1. 统计面板对接 (针对你的后端结构优化) ==========
    async loadDashboardStats() {
      try {
        // 并行请求
        const [resUser, resContent, resPending] = await Promise.allSettled([
          axios.get('/api/admin/user_count'),
          axios.get('/api/admin/content_count'),
          axios.get('/api/admin/pending_review_count')
        ]);

        // 辅助函数：专门处理你的后端返回格式 { success: true, data: { xxx_count: 123 } }
        const getCount = (res, keyName) => {
          if (res.status === 'rejected' || !res.value) return 0;
          const body = res.value.data; 
          // 尝试从 data.data[keyName] 获取
          if (body?.data && body.data[keyName] !== undefined) {
            return body.data[keyName];
          }
          return 0;
        };

        // 1. 总用户数 (对应后端 key: user_count)
        this.stats[0].value = getCount(resUser, 'user_count');

        // 2. ✅ 今日新增内容 (从 content_count 接口的新字段获取)
        if (resContent.status === 'fulfilled' && resContent.value.data?.data) {
           this.stats[1].value = resContent.value.data.data.today_new_count || 0;
        }

        // 3. 内容总数 (对应后端 key: content_count)
        this.stats[2].value = getCount(resContent, 'content_count');

        // 4. 待审核内容 (对应后端 key: pending_review_count)
        this.stats[3].value = getCount(resPending, 'pending_review_count');

      } catch (error) {
        console.error("加载统计数据失败", error);
      }
    },

    // ========== 2. 用户管理功能对接 ==========
    
    // 加载所有用户列表 /api/admin/all_user_info
    async loadAllUsers() {
      this.userLoading = true;
      try {
        const res = await axios.get('/api/admin/all_user_info');
        // 假设后端返回 { users: [...] } 或 { data: { users: [...] } }
        const users = res.data?.users || res.data?.data?.users || [];
        
        // 数据处理：将后端 status 字符串转换为 switch 需要的 boolean
        this.users = users.map(u => ({
          ...u,
          // 如果后端 status 是 'active'/'banned'，转为 true/false
          statusBoolean: u.status === 'active' || u.status === '1' || u.status === 1,
          role: u.admin_id ? 'admin' : 'user' // 简单推断角色
        }));
        
      } catch (error) {
        console.error("加载用户列表失败", error);
        this.$toast?.error("加载用户列表失败");
      } finally {
        this.userLoading = false;
        this.loadDashboardStats(); 
      }
    },

    // 更新用户状态（启用/禁用） /api/admin/update_user_status
    async updateUserStatus(item) {
      try {
        const formData = new URLSearchParams();
        formData.append('user_id', item.user_id);
        // 转换回后端需要的格式 'active' / 'banned'
        formData.append('status', item.statusBoolean ? 'active' : 'banned');

        await axios.post('/api/admin/update_user_status', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        this.$toast?.success(`用户 ${item.username} 状态已更新为 ${item.statusBoolean ? '启用' : '禁用'}`);
      } catch (error) {
        console.error("更新状态失败", error);
        // 失败回滚开关状态
        item.statusBoolean = !item.statusBoolean;
        this.$toast?.error("状态更新失败");
      }
    },

    // 删除用户 /api/admin/delete_user
    async deleteUser(userId) {
      if (!confirm("确定删除该用户吗？此操作不可恢复！")) return;

      try {
        const formData = new URLSearchParams();
        formData.append('user_id', userId);

        await axios.post('/api/admin/delete_user', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        // 前端移除
        this.users = this.users.filter(u => u.user_id !== userId);
        this.$toast?.success("用户删除成功");
      } catch (error) {
        console.error("删除用户失败", error);
        this.$toast?.error("删除失败: " + (error.response?.data?.detail || "未知错误"));
      }
    },

    // 简单的编辑弹窗逻辑（仅修改状态，因为没其他API）
    openUserDialog() {
       // 已删除添加功能
    },
    editUser(item) {
      this.editingUser = item.user_id;
      this.currentUser = { ...item };
      this.userDialogOpen = true;
    },
    async saveUser() {
      // 复用 updateUserStatus 逻辑
      await this.updateUserStatus({
        user_id: this.editingUser,
        username: this.currentUser.username,
        statusBoolean: this.currentUser.statusBoolean
      });
      this.userDialogOpen = false;
      this.loadAllUsers(); // 刷新列表
    },


    // ========== 3. 内容审核功能 ==========
    async loadPendingTrips() {
      this.loading = true;
      try {
        const res = await axios.get('/api/admin/all_pending_trips');
        const validTrips = res.data?.data?.trips || res.data?.trips || [];

        this.contents = validTrips.map(item => ({
          trip_id: item.trip_id,
          title: item.title || '未命名行程',
          username: item.owner_username || '未知用户',
          destination: item.destination || '未知目的地',
          publish_status: item.publish_status || 'pending',
          create_time: item.created_at || '未知时间' 
        }));
      } catch (error) {
        console.error("加载待审核行程失败:", error);
      } finally {
        this.loading = false;
      }
    },

    async handleReview(tripId, action) {
      if (this.auditingIds.includes(tripId)) return;
      this.auditingIds.push(tripId);

      try {
        const userInfo = JSON.parse(sessionStorage.getItem('user') || '{}');
        const senderId = userInfo.user_id || userInfo.id || 1;

        const reviewParams = new URLSearchParams();
        reviewParams.append('trip_id', tripId);
        reviewParams.append('status', action);
        await axios.post('/api/admin/pending', reviewParams);

        const msgParams = new URLSearchParams();
        msgParams.append('sender_id', senderId);
        msgParams.append('trip_id', tripId);
        msgParams.append('status', action);
        await axios.post('/api/admin/send_message', msgParams);

        this.$toast?.success(`操作成功`);
        this.loadPendingTrips();
        this.loadDashboardStats(); // 审核完刷新计数
      } catch (error) {
        this.$toast?.error(`操作失败`);
      } finally {
        this.auditingIds = this.auditingIds.filter(id => id !== tripId);
      }
    },

    getStatusText(status) {
      switch (status) {
        case 'pending': return '待审核';
        case 'published': return '已通过';
        case 'rejected': return '已拒绝';
        default: return '未知状态';
      }
    },
    getStatusColor(status) {
      switch (status) {
        case 'pending': return 'orange';
        case 'published': return 'green';
        case 'rejected': return 'red';
        default: return 'grey';
      }
    },

    // ========== 4. 公告管理功能 ==========
    openAnnouncementDialog() {
      this.editingAnnouncement = null;
      this.currentAnnouncement = { title: "", content: "", notice_id: null };
      this.announcementDialogOpen = true;
    },
    editAnnouncement(item) {
      this.editingAnnouncement = item.notice_id;
      this.currentAnnouncement = { ...item };
      this.announcementDialogOpen = true;
    },
    async saveAnnouncement() {
      const { title, content, notice_id } = this.currentAnnouncement;
      if (!title.trim() || !content.trim()) return;

      this.announcementLoading = true;
      try {
        const userInfo = JSON.parse(sessionStorage.getItem('user') || '{}');
        const adminId = userInfo.user_id || userInfo.id || 1;

        const formData = new URLSearchParams();
        formData.append('title', title);
        formData.append('content', content);
        formData.append('created_by', adminId);

        let url = '/api/notice/create';
        if (notice_id) {
          formData.append('notice_id', notice_id);
          // 假设有 update 接口
          url = '/api/notice/update'; 
        }

        await axios.post(url, formData);
        this.announcementDialogOpen = false;
        this.loadAllAnnouncements();
      } catch (error) {
        this.$toast?.error("操作失败");
      } finally {
        this.announcementLoading = false;
      }
    },
    async loadAllAnnouncements() {
      this.announcementLoading = true;
      try {
        const res = await axios.get('/api/notice/list');
        this.announcements = res.data?.data?.notices.map(item => ({
          notice_id: item.notice_id,
          title: item.title,
          content: item.content,
          created_at: item.created_at,
          published: item.is_active === 1
        }));
      } catch (error) {
        this.announcements = [];
      } finally {
        this.announcementLoading = false;
      }
    },
    async toggleAnnouncementStatus(item) {
      this.announcementLoading = true;
      try {
        const userInfo = JSON.parse(sessionStorage.getItem('user') || '{}');
        const adminId = userInfo.user_id || userInfo.id || 1;
        
        const url = item.published ? '/api/notice/unpublish' : '/api/notice/publish';
        const formData = new URLSearchParams();
        formData.append('notice_id', item.notice_id);
        if (!item.published) formData.append('admin_id', adminId);

        await axios.post(url, formData);
        
        // 更新本地
        item.published = !item.published;
      } catch (error) {
        this.$toast?.error("切换状态失败");
      } finally {
        this.announcementLoading = false;
      }
    },
    async deleteAnnouncement(noticeId) {
      if (!confirm("确定删除？")) return;
      try {
        const formData = new URLSearchParams();
        formData.append('notice_id', noticeId);
        await axios.post('/api/notice/delete', formData);
        this.loadAllAnnouncements();
      } catch (error) {
        this.$toast?.error("删除失败");
      }
    }
  }
};
</script>

<style scoped>
:deep(.v-data-table thead) {
  display: table-header-group !important;
  visibility: visible !important;
}
:deep(.v-data-table th.v-data-table-header__cell) {
  color: #675096 !important;
  font-weight: 600 !important;
}
.admin-container {
  min-height: 100vh;
  background-color: #FAFAFA;
}
.admin-layout {
  display: flex;
}
.admin-content {
  padding: 24px;
  margin-left: 250px;
  margin-top: 64px;
  width: calc(100% - 250px);
}
.v-navigation-drawer {
  width: 250px !important;
  height: calc(100vh - 64px) !important;
}
.stat-card {
  border-color: #DBD1EF;
  background-color: white;
  height: 100%;
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
.positive { color: #43a047; }
.negative { color: #e53935; }
.user-controls {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
.selected-item {
  background-color: rgba(116, 45, 216, 0.1);
  border-right: 4px solid #742DD8;
}
</style>