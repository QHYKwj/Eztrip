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

      <!-- 轮播卡片（居中显示） -->
      <v-card class="swiper-card" rounded="lg">
        <SwiperCard />
      </v-card>

      <!-- 行程卡片：一行3个，自动换行且列宽均匀 -->
      <v-row gutter="20">
        <template v-for="(group, groupIndex) in tripGroups" :key="groupIndex">
          <v-col :span="8" v-for="(trip, index) in group" :key="index">
            <!-- 有行程数据则显示TripCard，否则显示空占位 -->
            <TripCard v-if="trip.id" :trip="trip" />
            <div v-else class="empty-card" />
          </v-col>
        </template>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup>
import SwiperCard from '@/components/SwiperCard.vue'
import TripCard from '@/components/TripCard.vue'
import SearchBar from '@/components/SearchBar.vue'
import { ref } from 'vue';

// 搜索事件
const handleSearch = (query) => {
  console.log('执行搜索:', query)
};
const handleInput = (value) => {
  console.log('输入变化:', value)
};

// 模拟行程数据（可根据业务扩展）
const tripList = ref([
  { id: 1, name: '行程1', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', rating: 4.5, type: '$ • Italian, Cafe', desc: 'Small plates, salads & sandwiches' },
  { id: 2, name: '行程2', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', rating: 4.8, type: '$$ • Chinese, Restaurant', desc: 'Traditional Chinese dishes with a modern twist' },
  { id: 3, name: '行程3', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', rating: 4.2, type: '$ • Outdoor, Activity', desc: 'Hiking and camping in the mountain area' },
  { id: 4, name: '行程4', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', rating: 4.6, type: '$$ • Travel, Tour', desc: 'City tour with professional guide' },
  { id: 5, name: '行程5', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', rating: 4.7, type: '$$$ • Business, Hotel', desc: 'Luxury hotel with conference facilities' }
]);
// 分组函数：将数组按每3个一组拆分，不足3个时补空对象
const groupTrips = (list) => {
  const groups = [];
  for (let i = 0; i < list.length; i += 3) {
    const group = list.slice(i, i + 3);
    // 补全到3个元素，不足时用空对象占位
    while (group.length < 3) {
      group.push({});
    }
    groups.push(group);
  }
  return groups;
};
// 计算属性：分组后的行程数据
const tripGroups = computed(() => groupTrips(tripList.value));
</script>

<style scoped>
.swiper-card {
  background: #F3F2FD;
  height: 30vh;
  width: 40vh;
  display: flex;
  align-items: stretch;
  box-shadow: 0px 0px 2px 5px #F3F2FD;
  margin: 20px auto; /* 轮播卡片水平居中 */
}

.search-container {
  margin: 0 0 20px 0;
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 0 20px;
}

/* 行程卡片 */
.empty-card {
  width: 100%;
  min-height: 400px; /* 与TripCard高度一致 */
  border: 1px solid #eee;
  border-radius: 4px;
  box-sizing: border-box;
}
::v-deep .trip-card {
  width: 100%;
}
::v-deep .v-col {
  padding: 0 8px;
}
</style>