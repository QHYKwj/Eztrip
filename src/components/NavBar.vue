<template>
  <v-card>
    <v-navigation-drawer
      v-model="localdrawer"
      v-model:mini-variant="mini"
      app
      permanent
      :width="mini ? 80 : 200"
    >
      <!-- 顶部收起/展开按钮 -->
      <v-list-item>
        <v-btn icon @click="toggleMini">
          <v-icon>{{ mini ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
        </v-btn>
        <v-list-item-title v-if="!mini" class="ml-2">菜单</v-list-item-title>
      </v-list-item>

      <v-divider />

      <!-- 主菜单 -->
      <v-list dense>
        <NavTitle :item="{ heading: 'Main Menu' }" :mini="mini" />
        <NavLink :item="{ title: 'Home', icon: 'mdi-home', to: '/hello' }" :mini="mini" />
        <NavLink :item="{ title: 'ChatLLM', icon: 'mdi-robot-outline', to: '/LLM' }" :mini="mini" />
        <NavLink :item="{ title: '相册', icon: 'mdi-image-album', to: '/photos' }" :mini="mini" />

        <NavTitle :item="{ heading: 'Dev Tools' }" :mini="mini" />
        <NavLink :item="{ title: 'Timeline Drawer', icon: 'mdi-timeline-text', to: '/timelineTools' }" :mini="mini" />
      </v-list>

      <!-- 头像固定在底部 -->
      <template #append>
        <v-list-item
          class="px-4 pb-4 user-info"
        >
          <v-list-item-avatar size="40">
            <v-img
              class="rounded-circle"
              src="https://randomuser.me/api/portraits/men/85.jpg"
            />
          </v-list-item-avatar>

          <!-- 名字放在头像下方 -->
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
.rounded-circle {
  border-radius: 50%;
}
.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.user-name {
  text-align: center;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap; /* 避免文字换行 */
}
</style>
