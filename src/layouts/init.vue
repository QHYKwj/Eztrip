<template>
  <div class="app-container">
    <div class="background2" />
    <div class="content">
      <!-- 包裹整个内容以便使用过渡效果 -->
      <transition name="fade" @after-leave="onFadeOutComplete">
        <v-container v-if="isLoading" class="d-flex justify-center align-center" style="height: 100vh;">
          <!-- 显示加载动画 -->
          <!-- Logo -->
          <v-img
            alt="Logo"
            class="logo"
            lazy-src="@/assets/logo2.svg"
            max-height="300"
            max-width="400"
            src="@/assets/logo2.svg"
          />
          <v-progress-circular
            class="v-progress-circular"
            color="grey lighten-5"
            indeterminate
            size="100"
          />
        </v-container>
      </transition>
    </div>
  </div>
</template>

<script>
  export default {
    data () {
      return {
        isLoading: true, // 控制加载动画显示与否
      }
    },
    mounted () {
      // 模拟延迟加载，3秒后隐藏加载动画并跳转到登录页面
      setTimeout(() => {
        this.isLoading = false // 隐藏加载动画
      }, 3000)
    },
    methods: {
      onFadeOutComplete () {
        // 当淡出动画完成时跳转到登录页面
        this.$router.push('/login')
      },
    },
  }
</script>

<style scoped>
.app-container {
  background-color: #e6e0fd;
  position: relative;
  height: 100vh;
}

.background2 {
  position: absolute; /* 确保它覆盖在 background 上 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(182, 96, 255, 0.4), rgba(108, 189, 255, 0.4)); /* 蓝紫渐变色 */
}

.logo {
  z-index: 1;
  opacity: 0.5;
}

/* 加载动画圆圈的位置，调整大小 */
.v-progress-circular {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 淡出动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 1s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
.background2.fade-leave-active {
  background: linear-gradient(to bottom, rgba(138, 43, 226, 0.8),rgba(70, 130, 180, 0.8)); /* 目标渐变色 */
}
</style>
