<template>
  <v-main class="layout">
    <Navbar
      :drawer="drawer"
      @show-create-dialog="showDialog = true"
      @toggle-drawer="drawer = !drawer"
    />
    <!-- ✅ 给 Menu 加 ref，方便创建行程后刷新 -->
    <Menu ref="menu" />
    <div class="page-container">
      <router-view />
    </div>
    <CreateTripDialog
      v-model="showDialog"
      @trip-created="handleTripCreated"
    />
  </v-main>
</template>

<script>
import CreateTripDialog from '@/components/createTripDialog.vue'
import Menu from '@/layouts/components/Menu.vue'
import Navbar from '../components/NavBar.vue'

export default {
  name: 'Vbar',
  // eslint-disable-next-line vue/no-reserved-component-names
  components: { Menu, Navbar, CreateTripDialog },
  data () {
    return {
      drawer: true,
      showDialog: false,
    }
  },
  methods: {
    // 处理行程创建成功的回调
    handleTripCreated (tripData) {
      console.log('创建的行程数据：', tripData)
      // ✅ 创建完成后，刷新左侧菜单行程列表
      if (this.$refs.menu && typeof this.$refs.menu.loadTrips === 'function') {
        this.$refs.menu.loadTrips()
      }
    },
  },
}
</script>

<style>
.layout {
  background-color: #F3F2FD;
}
/* ✅ 所有页面内容统一的外层容器样式 */
.page-container {
  flex: 1;
  background-color: white;
  margin: 3vh 3vh 3vh 2vh; /* 上方 & 侧边留白 */
  border-radius: 1.2vh;
  padding: 2vh;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
}
</style>
