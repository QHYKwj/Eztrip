<template>
  <v-main class="main">
    <v-container fluid px-0>
      <!-- 搜索栏 -->
      <div class="search-container">
        <SearchBar
          placeholder="搜索目的地、行程..."
          @input="handleInput"
          @search="handleSearch"
        />
        <!-- 创建按钮 -->
        <CreateTripDialog /> <!-- 直接使用之前创建的弹窗组件 -->
      </div>

      <!-- 筛选框 -->
      <div class="filter-container">
        <FilterBar @filter="handleTripFilter" />
      </div>

      <!-- 轮播卡片 -->
      <v-card class="swiper-card" rounded="lg">
        <SwiperCard />
      </v-card>

      <!-- 行程卡片：响应式排列 -->
      <v-row gutter="20" class="trip-row">
        <!-- 桌面lg：每行8个 (24/3=8) -->
        <v-col 
          v-for="(trip, index) in filteredTrips" 
          :key="trip.id || index" 
          :cols="12"   
          :md="8"      
          :lg="3"    
        >
          <TripCard :trip="trip" />
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import CreateTripDialog from '@/components/createTripDialog.vue'
  import FilterBar from '@/components/FilterBar.vue'
  import SearchBar from '@/components/SearchBar.vue'
  import SwiperCard from '@/components/SwiperCard.vue'
  import TripCard from '@/components/TripCard.vue'

  // 搜索事件
  function handleSearch (query) {
    console.log('执行搜索:', query)
  }
  function handleInput (value) {
    console.log('输入变化:', value)
  }

  // 模拟行程数据（时间统一为字符串，与筛选框匹配）
  const originalTrips = ref([
    { id: 1, name: '行程1', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', time: '2', location: 'domestic', style: 'leisure' },
    { id: 2, name: '行程2', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', time: '4-7', location: 'domestic', style: 'food' },
    { id: 3, name: '行程3', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', time: '7+', location: 'abroad', style: 'adventure' },
    { id: 4, name: '行程4', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', time: '3', location: 'domestic', style: 'culture' },
    { id: 5, name: '行程5', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', time: '4-7', location: 'abroad', style: 'leisure' },
  ])

  // 筛选后的数据
  const filteredTrips = ref([...originalTrips.value])

  // 处理筛选逻辑（支持范围筛选）
  function handleTripFilter (filters) {
    const { time, location, style } = filters
    filteredTrips.value = originalTrips.value.filter(trip => {
      // 时间筛选
      if (time) {
        const tripTime = trip.time
        if (time === '4-7') {
          if (!['4', '5', '6', '7', '4-7'].includes(tripTime)) return false
        } else if (time === '7+') {
          if (!['7+', '8', '9'].includes(tripTime)) return false
        } else {
          if (tripTime !== time) return false
        }
      }

      // 地点筛选
      if (location && trip.location !== location) return false

      // 风格筛选
      if (style && trip.style !== style) return false

      return true
    })
  }
</script>

<style scoped>
.search-container {
  margin: 0 0 20px 0;
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 0 20px;
}

/* 筛选框容器样式 */
.filter-container {
  padding: 0;
  margin-bottom: 20px;
}

.swiper-card {
  background: #F3F2FD;
  height: 30vh;
  width: 40vh;
  display: flex;
  align-items: stretch;
  box-shadow: 0px 0px 2px 5px #F3F2FD;
  margin: 20px auto; /* 轮播卡片水平居中 */
}

/* 行程卡片 */
.trip-row {
  padding: 0 16px;
  margin-bottom: 20px;
}

:deep(.v-col) {
  padding: 0 10px;
  margin-bottom: 20px; /* 卡片之间的垂直间距 */
}
</style>
