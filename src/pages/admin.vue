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
                  <!-- 标题输入框 -->
                  <v-text-field
                    v-model="currentAnnouncement.title"
                    label="公告标题"
                    required
                    full-width
                    placeholder="请输入公告标题"
                  />
                  <!-- 内容输入框 -->
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
      announcementLoading: false, // 新增：公告加载/操作状态

      // 内容审核相关状态（核心）
      loading: false,          // 加载状态
      auditingIds: [],         // 正在审核的行程ID（防重复点击）
      contents: [],            // 待审核行程数组（从API获取）

      // 侧边栏配置
      sidebarItems: [
        { title: "用户管理", icon: "mdi-account" },
        { title: "内容审核", icon: "mdi-file-check" },
        { title: "公告管理", icon: "mdi-bullhorn" }
      ],

      // 统计数据（原有假数据，可后续对接API）
      stats: [
        { title: "总用户数", value: 1280, change: 12 },
        { title: "今日新增", value: 24, change: 8 },
        { title: "内容总数", value: 3560, change: 5 },
        { title: "待审核内容", value: 12, change: -3 }
      ],

      // 用户数据（原有假数据，可后续对接API）
      users: [
        { id: 1, username: "john_doe", email: "john@example.com", role: "admin", status: true, registered: "2024-01-15" },
        { id: 2, username: "jane_smith", email: "jane@example.com", role: "user", status: true, registered: "2024-02-20" },
        { id: 3, username: "mike_brown", email: "mike@example.com", role: "moderator", status: false, registered: "2024-03-05" }
      ],

      // 公告数据
      announcements: [],
      currentAnnouncement: {
        title: "",
        content: "",
        notice_id: null
      },

      // 表格头部配置（适配后端字段）
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

      // 编辑对象
      currentUser: {
        username: "",
        email: "",
        role: "user",
        status: true
      },
    };
  },
  created() {
    // 页面初始化时加载待审核行程
    this.loadPendingTrips();
    this.loadAllAnnouncements();
  },
  methods: {
    // ========== 基础功能 ==========
    logout() {
      sessionStorage.removeItem('user');
      this.$router.push('/login');
    },
    refreshData() {
      this.$toast?.success("数据已刷新");
      // 刷新待审核行程
      this.loadPendingTrips();
    },
    showNotifications() {
      this.unreadNotifications = 0;
    },

    // ========== 用户管理功能 ==========
    openUserDialog() {
      this.editingUser = null;
      this.currentUser = { username: "", email: "", role: "user", status: true };
      this.userDialogOpen = true;
    },
    editUser(item) {
      this.editingUser = item.id;
      this.currentUser = { ...item };
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
      this.$toast?.success("用户保存成功");
    },
    deleteUser(id) {
      if (confirm("确定删除该用户吗？")) {
        this.users = this.users.filter(u => u.id !== id);
        this.$toast?.success("用户删除成功");
      }
    },
    updateUserStatus(item) {
      this.$toast?.success(`用户 ${item.username} 状态已更新`);
    },

    /*
      加载待审核行程（对接后端 /api/admin/all_pending_trips）
     */
    async loadPendingTrips() {
      this.loading = true;
      try {
        const res = await axios.get('/api/admin/all_pending_trips');
        // 后端返回结构：{success: true, data: {trips: [], count: ...}}
        const backendTripList = res.data?.data?.trips || [];
        // 确保是数组（避免后端返回非数组类型）
        const validTrips = Array.isArray(backendTripList) ? backendTripList : [];

        // 映射后端字段到前端表格
        this.contents = validTrips.map(item => ({
          trip_id: item.trip_id, // 后端行程ID
          title: item.title || '未命名行程',
          username: item.owner_username || '未知用户', // 后端关联的用户名
          destination: item.destination || '未知目的地',
          publish_status: item.publish_status || 'pending', // 审核状态
          create_time: item.created_at 
            ? new Date(item.created_at).toLocaleDateString() 
            : new Date().toLocaleDateString() // 提交时间
        }));
        console.log("成功加载待审核行程:", this.contents);
      } catch (error) {
        console.error("加载待审核行程失败:", error);
        this.contents = [];
        this.$toast?.error("加载待审核行程失败，请重试");
      } finally {
        this.loading = false;
      }
    },

    /**
     * 处理行程审核（对接审核+发消息API）
     * @param {number} tripId - 行程ID
     * @param {string} action - accept/reject
     */
    async handleReview(tripId, action) {
      if (this.auditingIds.includes(tripId)) return;
      this.auditingIds.push(tripId);

      try {
        // 获取管理员ID（从登录信息中读取）
        const userInfo = JSON.parse(sessionStorage.getItem('user') || '{}');
        const senderId = userInfo.user_id || userInfo.id || 1;

        // 1. 调用审核API（/api/admin/pending）
        const reviewParams = new URLSearchParams();
        reviewParams.append('trip_id', tripId);
        reviewParams.append('status', action);
        await axios.post('/api/admin/pending', reviewParams, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        // 2. 调用发消息API（/api/admin/send_message）
        const msgParams = new URLSearchParams();
        msgParams.append('sender_id', senderId);
        msgParams.append('trip_id', tripId);
        msgParams.append('status', action);
        await axios.post('/api/admin/send_message', msgParams, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        // 操作成功提示+刷新数据
        this.$toast?.success(`行程${tripId}已${action === 'accept' ? '审核通过' : '审核拒绝'}，已通知用户`);
        this.loadPendingTrips();
      } catch (error) {
        console.error(`审核行程${tripId}失败:`, error);
        this.$toast?.error(`行程${tripId}审核失败，请重试`);
      } finally {
        this.auditingIds = this.auditingIds.filter(id => id !== tripId);
      }
    },

    /**
     * 审核状态文本映射
     */
    getStatusText(status) {
      switch (status) {
        case 'pending': return '待审核';
        case 'published': return '已通过';
        case 'rejected': return '已拒绝';
        default: return '未知状态';
      }
    },

    /**
     * 审核状态颜色映射
     */
    getStatusColor(status) {
      switch (status) {
        case 'pending': return 'orange';
        case 'published': return 'green';
        case 'rejected': return 'red';
        default: return 'grey';
      }
    },

    // ==========公告管理核心方法 ==========
    /**
     * 1. 打开发布公告弹窗（清空表单数据）
     */
    openAnnouncementDialog() {
      this.editingAnnouncement = null;
      this.currentAnnouncement = {
        title: "",
        content: "",
        notice_id: null
      };
      this.announcementDialogOpen = true;
    },

    /**
     * 编辑公告
     */
    editAnnouncement(item) {
      this.editingAnnouncement = item.notice_id;
      this.currentAnnouncement = { ...item };
      this.announcementDialogOpen = true;
    },

    /**
     * 2. 保存公告（发布/编辑）- 只保留对接后端的逻辑，删除旧的假数据逻辑
     */
    async saveAnnouncement() {
      const { title, content, notice_id } = this.currentAnnouncement;
      // 表单校验
      if (!title.trim() || !content.trim()) {
        this.$toast?.warning("公告标题和内容不能为空！");
        return;
      }

      this.announcementLoading = true;
      try {
        // 获取管理员ID
        const userInfo = JSON.parse(sessionStorage.getItem('user') || '{}');
        const adminId = userInfo.user_id || userInfo.id || 1;

        const formData = new URLSearchParams();
        formData.append('title', title);
        formData.append('content', content);
        formData.append('created_by', adminId);

        let url = '/api/notice/create';
        
        // 如果是编辑操作
        if (notice_id) {
          formData.append('notice_id', notice_id);
          // 这里假设存在更新接口，如果后端没有可以调整
          url = '/api/notice/update';
        }

        await axios.post(
          url,
          formData,
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );

        this.announcementDialogOpen = false;
        this.$toast?.success(notice_id ? "公告更新成功！" : "公告创建成功！");
        this.loadAllAnnouncements();
      } catch (error) {
        console.error("公告操作失败：", error.response?.data || error.message);
        this.$toast?.error("操作失败：" + (error.response?.data?.detail || "服务器错误"));
      } finally {
        this.announcementLoading = false;
      }
    },

    /**
     * 3. 加载所有公告
     */
    async loadAllAnnouncements() {
      this.announcementLoading = true;
      try {
        const res = await axios.get('/api/notice/list');
        
        // 映射后端字段到前端
        this.announcements = res.data?.data?.notices.map(item => ({
          notice_id: item.notice_id,
          title: item.title,
          content: item.content,
          created_at: item.created_at,
          published: item.is_active === 1
        }));
      } catch (error) {
        console.error("加载公告失败：", error.response?.data || error.message);
        this.announcements = [];
        this.$toast?.error("加载公告失败：" + (error.response?.data?.detail || "接口调用错误"));
      } finally {
        this.announcementLoading = false;
      }
    },

    /**
     * 4. 切换公告发布状态
     */
    async toggleAnnouncementStatus(item) {
      this.announcementLoading = true;
      try {
        const userInfo = JSON.parse(sessionStorage.getItem('user') || '{}');
        const adminId = userInfo.user_id || userInfo.id || 1;
        
        const url = item.published ? '/api/notice/unpublish' : '/api/notice/publish';
        const formData = new URLSearchParams();
        formData.append('notice_id', item.notice_id);
        
        // 发布时需要管理员ID
        if (!item.published) {
          formData.append('admin_id', adminId);
        }

        await axios.post(
          url,
          formData,
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );

        // 更新本地状态
        this.announcements = this.announcements.map(notice => 
          notice.notice_id === item.notice_id 
            ? { ...notice, published: !item.published } 
            : notice
        );
        this.$toast?.success(`公告已${!item.published ? '发布' : '取消发布'}`);
      } catch (error) {
        console.error("切换公告状态失败：", error.response?.data || error.message);
        this.$toast?.error("切换状态失败：" + (error.response?.data?.detail || error.message));
      } finally {
        this.announcementLoading = false;
      }
    },

    /**
     * 5. 删除公告
     */
    async deleteAnnouncement(noticeId) {
      if (!noticeId || isNaN(Number(noticeId)) || Number(noticeId) <= 0) {
        this.$toast?.error("公告ID无效，无法删除");
        return;
      }
      if (!confirm("确定删除该公告吗？删除后无法恢复！")) return;

      try {
        const formData = new URLSearchParams();
        formData.append('notice_id', Number(noticeId));

        await axios.post(
          '/api/notice/delete',
          formData,
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
        );

        // 更新本地列表
        this.announcements = this.announcements.filter(notice => 
          Number(notice.notice_id) !== Number(noticeId)
        );
        this.$toast?.success("公告删除成功");
      } catch (error) {
        console.error("删除失败详情：", error.response);
        const errDetail = error.response?.data?.detail || "未知错误";
        this.$toast?.error("删除失败：" + errDetail);
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
  display: table-cell !important;
  height: 56px !important;
  min-height: 56px !important;
  padding: 0 16px !important;
  color: #675096 !important;
  font-weight: 600 !important;
  border-bottom: 2px solid #DBD1EF !important;
}
:deep(.v-data-table td.v-data-table__cell) {
  vertical-align: middle !important;
  padding: 12px 16px !important;
}
:deep(.announcement-table .v-data-table__cell:last-child) {
  min-width: 200px !important;
}

/* 原有样式完全保留 */
.action-group {
  display: flex;
  gap: 12px;
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
.admin-content {
  padding: 24px;
  margin-left: 250px;
  margin-top: 64px;
  width: calc(100% - 250px);
  box-sizing: border-box;
}
.v-navigation-drawer {
  width: 250px !important;
  flex-shrink: 0;
  height: calc(100vh - 64px) !important;
}
.admin-content {
  padding: 24px 32px;
  flex: 1;
  max-width: calc(100% - 250px);
  width: 100%;
  box-sizing: border-box;
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