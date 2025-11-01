<template>
  <v-main class="main">
    <v-container fluid px-0>
      <!-- 搜索栏 -->
      <div class="search-container">
        <SearchBar 
          @search="handleSearch" 
          @input="handleInput"
          placeholder="搜索目的地、行程..."
        />
      </div>

      <!-- 筛选框 -->
      <div class="filter-container">
        <FilterBar @filter="handleTripFilter" />
      </div>

      <!-- 轮播卡片 -->
      <v-card class="swiper-card" rounded="lg">
        <SwiperCard />
      </v-card>

      <!-- 行程卡片：一行3个 -->
      <v-row gutter="20">
        <template v-for="(group, groupIndex) in tripGroups" :key="groupIndex">
          <v-col :span="8" v-for="(trip, index) in group" :key="index">
            <TripCard v-if="trip.id" :trip="trip" />
            <div v-else class="empty-card" />
          </v-col>
        </template>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup>
import { ref, computed } from 'vue';
import FilterBar from '@/components/FilterBar.vue';
import SwiperCard from '@/components/SwiperCard.vue';
import TripCard from '@/components/TripCard.vue';
import SearchBar from '@/components/SearchBar.vue';

// 搜索事件
const handleSearch = (query) => {
  console.log('执行搜索:', query)
};
const handleInput = (value) => {
  console.log('输入变化:', value)
};

// 模拟行程数据（时间统一为字符串，与筛选框匹配）
const originalTrips = ref([
  { id: 1, name: '行程1', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', time: '2', location: 'domestic', style: 'leisure' },
  { id: 2, name: '行程2', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png',time: '4-7', location: 'domestic', style: 'food' },
  { id: 3, name: '行程3', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png',time: '7+', location: 'abroad', style: 'adventure' },
  { id: 4, name: '行程4', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png',time: '3', location: 'domestic', style: 'culture' },
  { id: 5, name: '行程5', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png',time: '4-7', location: 'abroad', style: 'leisure' }
]);

// 筛选后的数据
const filteredTrips = ref([...originalTrips.value]);

// 处理筛选逻辑（支持范围筛选）
const handleTripFilter = (filters) => {
  const { time, location, style } = filters;
  filteredTrips.value = originalTrips.value.filter(trip => {
    // 时间筛选（支持范围）
    if (time) {
      const tripTime = trip.time;
      // 处理4-7天和7+的范围匹配
      if (time === '4-7') {
        // 匹配时间为4-7天的行程（这里假设trip.time是'4-7'或具体数字）
        if (!['4', '5', '6', '7', '4-7'].includes(tripTime)) return false;
      } else if (time === '7+') {
        if (!['7+', '8', '9'].includes(tripTime)) return false;
      } else {
        // 1-3天精确匹配
        if (tripTime !== time) return false;
      }
    }

    // 地点筛选
    if (location && trip.location !== location) return false;

    // 风格筛选
    if (style && trip.style !== style) return false;

    return true;
  });
};

// 分组逻辑（保持不变）
const groupTrips = (list) => {
  const groups = [];
  for (let i = 0; i < list.length; i += 3) {
    const group = list.slice(i, i + 3);
    while (group.length < 3) group.push({});
    groups.push(group);
  }
  return groups;
};

const tripGroups = computed(() => groupTrips(filteredTrips.value));
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
.empty-card {
  width: 100%;
  min-height: 400px; /* 与TripCard高度一致 */
  border: 1px solid #eee;
  border-radius: 4px;
  box-sizing: border-box;
}
:deep(.trip-card) {
  width: 100%;
}
:deep(.v-col) {
  padding: 0 8px;
}
</style>