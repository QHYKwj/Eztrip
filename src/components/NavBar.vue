<template>
  <v-card
    class="sidenav-card"
    outlined
  >
    <v-navigation-drawer
      v-model="localdrawer"
      v-model:mini-variant="mini"
      app
      class="sidenav"
      permanent
      style="background-color: #F3F2FD"
      :width="mini ? 64 : 140"
    >
      <!-- 顶部收起/展开按钮 -->
      <v-list-item>
        <v-btn class="menu-toggle-btn" icon @click="toggleMini">
          <v-icon>{{ mini ? 'mdi-menu-close' : 'mdi-menu-open' }}</v-icon>
        </v-btn>
      </v-list-item>

      <v-divider />

      <!-- 主菜单 -->
      <v-list dense>
        <NavLink :item="{ title: '创建', icon: 'mdi-plus-circle', onClick: () => $emit('showCreateDialog') }" :mini="mini" />
        <v-divider style="height: 2px;margin-top: 6px" />
        <NavTitle :item="{ heading: 'Main Menu' }" :mini="mini" />
        <NavLink :item="{ title: '首页', icon: 'mdi-home', to: '/home' }" :mini="mini" />
        <NavLink :item="{ title: '行程', icon: 'mdi-content-save', to: '/plan' }" :mini="mini" />

        <NavTitle :item="{ heading: 'Dev Tools' }" :mini="mini" />
        <NavLink :item="{ title: 'AI生成', icon: 'mdi-creation', to: '/AI' }" :mini="mini" />
      </v-list>

      <!-- 头像固定在底部 -->
      <template #append>
        <!-- 消息入口 -->
        <NavLink
          :item="{
            title: '消息',
            icon: 'mdi-bell-badge-outline',
            to: '/message',
            showBadge: hasUnread
          }"
          :mini="mini"
        />
        <v-divider style="height: 2px;margin-top: 6px" />

        <!-- 底部用户信息：改为当前用户 -->
        <v-list-item class="px-4 pb-4 user-info">
          <div class="avatar-border" @click="goToProfile">
            <v-list-item-avatar size="48">
              <v-img
                class="rounded-circle"
                :src="user.avatar || defaultAvatar"
                style="cursor: pointer"
              />
            </v-list-item-avatar>
          </div>

          <v-list-item-title
            v-if="!mini"
            class="mt-2 user-name"
          >
            {{ user.username || '未登录' }}
          </v-list-item-title>
        </v-list-item>
      </template>
    </v-navigation-drawer>
  </v-card>
</template>

<script>
import axios from 'axios'
import { notificationState } from '@/stores/notificationState'
import NavLink from './NavLink.vue'
import NavTitle from './NavTitle.vue'

export default {
  name: 'SideNav',
  components: {
    NavLink,
    NavTitle,
  },
  props: {
    drawer: {
      type: Boolean,
      required: true,
    },
  },
  emits: ['showCreateDialog'],
  data () {
    return {
      localdrawer: this.drawer,
      mini: true,
      notificationState,
      defaultAvatar: 'https://randomuser.me/api/portraits/men/85.jpg',
      user: {
        username: '',
        avatar: '',
      },
    }
  },
  computed: {
    hasUnread () {
      return this.notificationState.unreadCount > 0
    },
  },
  watch: {
    drawer (newVal) {
      this.localdrawer = newVal
    },
  },
  created () {
    this.loadUserInfo()
  },
  methods: {
    toggleMini () {
      this.mini = !this.mini
    },
    goToProfile () {
      this.$router.push('/profile')
    },
    getUserFromSession () {
      const str = sessionStorage.getItem('user')
      if (!str) return null
      try {
        return JSON.parse(str)
      } catch {
        return null
      }
    },
    async loadUserInfo () {
      const stored = this.getUserFromSession()
      if (!stored || !stored.user_id) {
        // 未登录：保持默认头像 & 名字
        return
      }
      try {
        const res = await axios.get(`/api/profile/${stored.user_id}`)
        const data = res.data
        this.user.username = data.username
        this.user.avatar = data.avatar
      } catch (e) {
        console.error('加载用户信息失败', e)
      }
    },
  },
}
</script>

<style scoped>
.sidenav {
  border-right: 2px solid #DBD1EF;
}

.rounded-circle {
  border-radius: 50%;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar-border {
  border: 2px solid white;
  border-radius: 50%;
  padding: 2px;
}

.user-name {
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  color: #444;
}
/* 其他样式保持不变 */
.menu-toggle-btn {
  border-radius: 50%;
  width: fit-content;
  height: fit-content;
  box-shadow: none !important;
  min-width: 36px;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}
.menu-toggle-btn:hover {
  transform: scale(1.1);
}
.menu-toggle-btn {
  background-color: transparent !important;
}
</style>
