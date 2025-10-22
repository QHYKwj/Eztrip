<template>
  <router-view />
  <Navbar :drawer="drawer" @toggle-drawer="drawer = !drawer" />
</template>

<script>
  import Navbar from '../components/NavBar.vue'

  export default {
    name: 'Vbar',
    components: { Navbar },
    data () {
      return {
        drawer: true,
      }
    },
  }
</script>
