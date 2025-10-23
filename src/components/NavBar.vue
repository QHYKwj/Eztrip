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
<!--        <v-list-item-title v-if="!mini" class="ml-2" style="color: black;position: relative;left: 32%">菜单</v-list-item-title>-->
      </v-list-item>

      <v-divider />

      <!-- 主菜单 -->
      <v-list dense>
        <NavLink :item="{ title: '创建', icon: 'mdi-plus-circle', to: '/hello' }" :mini="mini" />
        <v-divider style="height: 2px;margin-top: 6px"></v-divider>
        <NavTitle :item="{ heading: 'Main Menu' }" :mini="mini" />
        <NavLink :item="{ title: '首页', icon: 'mdi-home', to: '/home' }" :mini="mini" />
        <NavLink :item="{ title: '行程', icon: 'mdi-content-save', to: '/trip' }" :mini="mini" />

        <NavTitle :item="{ heading: 'Dev Tools' }" :mini="mini" />
        <NavLink :item="{ title: 'AI生成', icon: 'mdi-creation', to: '/AI' }" :mini="mini" />
      </v-list>

      <!-- 头像固定在底部 -->
      <template #append>
        <NavLink :item="{ title: '消息', icon: 'mdi-bell-badge-outline', to: '/message' }" :mini="mini" />
        <v-divider style="height: 2px;margin-top: 6px"></v-divider>
        <v-list-item class="px-4 pb-4 user-info">
          <div class="avatar-border">
            <v-list-item-avatar size="48">
              <v-img
                class="rounded-circle"
                src="https://randomuser.me/api/portraits/men/85.jpg"
              />
            </v-list-item-avatar>
          </div>

          <v-list-item-title
            v-if="!mini"
            class="mt-2 user-name"
          >
            John Leider
          </v-list-item-title>
        </v-list-item>
      </template>
    </v-navigation-drawer>
  </v-card>
</template>

<script>
  import NavLink from './NavLink.vue'
  import NavTitle from './NavTitle.vue'

  export default {
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
    data () {
      return {
        localdrawer: this.drawer,
        mini: true,
      }
    },
    watch: {
      drawer (newVal) {
        this.localdrawer = newVal
      },
    },
    methods: {
      toggleMini () {
        this.mini = !this.mini
      },
    },
  }
</script>

<style scoped>
.sidenav {
  border-right: 2px solid #DBD1EF; /* 👈 明显的边界 */
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

/* 白色边框的头像容器 */
.avatar-border {
  border: 2px solid white;
  border-radius: 50%;
  padding: 2px; /* 边距让白框更明显 */
}

.user-name {
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  color: #444;
}
.menu-toggle-btn {
  border-radius: 50%;
  width: fit-content;
  height: fit-content;
  box-shadow: none !important;              /* ✅ 去除阴影 */
  min-width: 36px;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.menu-toggle-btn {
  background-color: transparent !important;
}

/* 悬停时稍微放大一点反馈感（可选） */
.menu-toggle-btn:hover {
  transform: scale(1.1);
}
</style>
