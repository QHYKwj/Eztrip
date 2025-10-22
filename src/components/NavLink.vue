<template>
  <v-list-item class="nav-link" link @click="goTo(item.to)">
    <v-list-item-content>
      <div
        class="nav-link-content"
        :class="{ mini: mini }"
      >
        <v-icon class="nav-link-icon" :class="{ mini: mini }">
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
    methods: {
      goTo (route) {
        if (route) this.$router.push(route)
      },
    },
  }
</script>

<style scoped>
.nav-link {
  padding-left: 12px;
  padding-right: 12px;
}

.nav-link-content {
  display: flex;
  align-items: center;
}

/* 收起时 icon 居中 */
.nav-link-content.mini {
  justify-content: center;
}

/* 默认 icon 样式 */
.nav-link-icon {
  font-size: 20px;
  margin-right: 8px;
}

/* 收起时 icon 居中且自适应 */
.nav-link-icon.mini {
  margin-right: 0;
  font-size: 28px;       /* 让图标稍微大一点 */
  width: 100%;
  text-align: center;    /* 水平居中 */
  object-fit: contain;   /* 模拟 aspect-fit 效果 */
}

.nav-link-text {
  font-size: 17px;
}
</style>
