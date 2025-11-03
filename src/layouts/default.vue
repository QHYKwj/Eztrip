<template>
  <v-main class="layout">
    <Navbar :drawer="drawer" @show-create-dialog="showDialog = true" @toggle-drawer="drawer = !drawer" />
    <Menu />
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
      // 处理行程创建成功的回调（可调用后端接口）
      handleTripCreated (tripData) {
        console.log('创建的行程数据：', tripData)
        // 这里可以添加后端 API 调用逻辑，例如：
        // axios.post('/api/trips', tripData).then(() => {
        //   alert('行程创建成功！');
        // });
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
