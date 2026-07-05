<template>
  <v-carousel v-model="model" height="100%" hide-delimiter-background show-arrows="hover">
    <v-carousel-item v-for="(src, index) in slides" :key="index">
      <v-sheet height="100%" tile>
        <v-row align="center" class="fill-height" justify="center" no-gutters>
          <v-img class="h-100 w-100" cover :src="src" />
        </v-row>
      </v-sheet>
    </v-carousel-item>
  </v-carousel>
</template>

<script setup>
  import { ref } from 'vue'

  // 1. ✅ 必须通过 import 引入本地静态图片，Vite 才能在编译时正确识别并打包路径
  import welcome1 from '@/assets/welcome1.png'
  import welcome2 from '@/assets/welcome2.png'
  import welcome3 from '@/assets/welcome3.png'
  import welcome4 from '@/assets/welcome4.png'
  import welcome5 from '@/assets/welcome5.png'

  const model = ref(0)

  // 2. ✅ 将引入的图片变量直接放入数组中
  const slides = [
    welcome1,
    welcome2,
    welcome3,
    welcome4,
    welcome5,
  ]
</script>

<style scoped>
.full-screen-carousel {
  width: auto;
  margin: 0;
  padding: 0;
}

html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>
