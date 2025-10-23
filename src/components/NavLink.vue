<template>
  <v-list-item
    class="nav-link"
    :class="{ active: isActive }"
    link
    @click="goTo(item.to)"
  >
    <v-list-item-content>
      <div class="nav-link-content" :class="{ mini: mini }">
        <v-icon
          class="nav-link-icon"
          :class="{ mini: mini, active: isActive }"
        >
          {{ item.icon }}
        </v-icon>
        <span v-if="!mini" class="nav-link-text">
          <slot>{{ item.title }}</slot>
        </span>
      </div>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
  export default {
    name: 'NavLink',
    props: {
      item: {
        type: Object,
        required: true,
      },
      mini: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      isActive () {
        // 根据当前路由是否匹配判断高亮
        return this.$route.path === this.item.to
      },
    },
    methods: {
      goTo (route) {
        if (route && this.$route.path !== route) {
          this.$router.push(route)
        }
      },
    },
  }
</script>

<style scoped>
.nav-link {
  padding-left: 12px;
  padding-right: 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.nav-link:hover {
  background-color: rgba(103, 80, 150, 0.1);
}

.nav-link-content {
  display: flex;
  align-items: center;
}

/* 收起时居中 */
.nav-link-content.mini {
  justify-content: center;
}

/* 默认图标颜色 */
.nav-link-icon {
  font-size: 20px;
  margin-right: 6px;
  color: #675096;
  transition: color 0.3s ease;
}

/* 收起时 icon 居中 */
.nav-link-icon.mini {
  margin:0 auto;
  font-size: 28px;
  width: 100%;
  text-align: center;
}

/* 激活状态图标高亮 */
.nav-link-icon.active {
  color: #742DD8;
}

.nav-link-text {
  font-size: 17px;
  color: #444;
  justify-content: center;
  align-items: center;
  margin-top: 1px;
}

.nav-link.active .nav-link-text {
  color: #742DD8;
  font-weight: 600;
}
</style>
