<template>
  <!-- 当 mini 为 true 时，整个 NavTitle 不渲染 -->
  <v-list-item v-if="!mini" class="nav-title-wrapper">
    <v-list-item-content>
      <v-list-item-title class="nav-title">
        <slot>{{ item.heading }}</slot>
      </v-list-item-title>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
  export default {
    name: 'NavTitle',
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
  }
</script>

<style scoped>
.nav-title-wrapper {
  margin-top: 12px;
  margin-bottom: 8px;
}

.nav-title {
  font-size: 20px;
  font-weight: 600;
  color: #666;
  display: flex;
  align-items: center;
}

.nav-title::after {
  content: "";
  flex: 1;
  height: 1px;
  background-color: white;
  margin-left: 8px;
}
</style>
