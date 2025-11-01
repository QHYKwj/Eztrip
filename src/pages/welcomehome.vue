<template>
  <v-main class="main">
    <v-container>
      <!-- 搜索栏 -->
      <div class="search-container">
        <SearchBar 
          @search="handleSearch" 
          @input="handleInput"
          placeholder="搜索目的地、行程..."
        />
      </div>

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
  import SearchBar from '@/components/SearchBar.vue'

// 处理搜索事件
const handleSearch = (query) => {
  console.log('执行搜索:', query)
  // 这里可以添加实际的搜索逻辑
}

// 处理输入实时变化
const handleInput = (value) => {
  console.log('输入变化:', value)
  
}
</script>

<style>
.swiper-card {
  background: #F3F2FD;
  height: 40vh; /* ✅ 高度由父层控制 */
  width: 40vh;
  display: flex;
  align-items: stretch; /* 让子组件填充卡片 */
  box-shadow: 0px 0px 2px 5px #F3F2FD;
  margin: 20px 0; /* 增加与其他元素的间距 */
}

/* 搜索栏容器样式 */
.search-container {
  margin: 20px 0;
  display: flex;
  justify-content: center; /* 让搜索栏居中显示 */
}
</style>
