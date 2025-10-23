<template>
  <v-main class="layout">
    <Navbar :drawer="drawer" @toggle-drawer="drawer = !drawer" />
    <Menu />
    <div class="page-container">
      <router-view />
    </div>
  </v-main>
</template>

<script>
  import Menu from '@/layouts/components/Menu.vue';
  import Navbar from '../components/NavBar.vue'

  export default {
    name: 'Vbar',
    components: { Menu, Navbar },
    data () {
      return {
        drawer: true,
      }
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
