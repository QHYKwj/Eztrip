<template>
  <v-main class="main">
    <v-container>
      <v-card class="swiper-card" rounded="lg">
        <SwiperCard />
      </v-card>
      <TripCard />
    </v-container>
  </v-main>
</template>

<script setup>
  import SwiperCard from '@/components/SwiperCard.vue'
  import TripCard from '@/components/TripCard.vue'
</script>

<style>
.swiper-card {
  background: #F3F2FD;
  height: 40vh; /* ✅ 高度由父层控制 */
  width: 40vh;
  display: flex;
  align-items: stretch; /* 让子组件填充卡片 */
  //border: #742DD8 solid 1px;
  box-shadow: 0px 0px 2px 5px #F3F2FD;
}
</style>
