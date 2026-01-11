<template>
  <v-main class="main">
    <v-container fluid px-0>
      <!-- 搜索栏 -->
      <div class="search-container">
        <!-- 这里的搜索我们也对接一下，让它也能触发搜索 -->
        <SearchBar
          placeholder="搜索目的地..."
          @search="handleSearchInput"
        />
        <!-- 创建按钮：监听 tripCreated 事件，创建成功后刷新列表 -->
        <CreateTripDialog @tripCreated="fetchTrips" />
      </div>

      <!-- 筛选框 -->
      <div class="filter-container">
        <FilterBar @filter="handleTripFilter" />
      </div>

      <!-- 轮播卡片 (保持不变) -->
      <v-card class="swiper-card" rounded="lg">
        <SwiperCard />
      </v-card>

      <!-- 行程卡片：响应式排列 -->
      <v-row gutter="20" class="trip-row">
        <!-- 桌面lg：每行8个 (根据你的布局 24/3=8) -->
        <v-col
          v-for="(trip, index) in trips"
          :key="trip.id || index"
          :cols="12"
          :md="8"
          :lg="3"
        >
          <!-- 传给子组件的数据 -->
          <TripCard :trip="trip" />
        </v-col>

        <!-- 缺省状态：如果没有数据 -->
        <v-col v-if="trips.length === 0" cols="12" class="text-center mt-10">
          <div class="text-grey text-h6">暂无符合条件的行程，快去创建吧！</div>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios' // 引入 axios
import CreateTripDialog from '@/components/createTripDialog.vue'
import FilterBar from '@/components/FilterBar.vue'
import SearchBar from '@/components/SearchBar.vue'
import SwiperCard from '@/components/SwiperCard.vue'
import TripCard from '@/components/TripCard.vue'

// 存储行程列表数据
const trips = ref([])

// 默认封面图 (因为目前数据库还没存图片，给个占位图防止卡片空白)
const defaultImage = 'https://cdn.vuetifyjs.com/images/cards/cooking.png'

/**
 * 核心方法：从后端获取数据
 * @param {Object} params - 搜索参数 { destination, style, days }
 */
const fetchTrips = async (params = {}) => {
  try {
    const res = await axios.get('/api/trip/search', { params })

    if (res.data && res.data.trips) {
      // 数据适配：后端返回的字段 -> TripCard 需要的字段
      // 后端返回: { id, title, destination, days, image ... }
      // 原假数据: { id, name, location, time, imageUrl ... }
      trips.value = res.data.trips.map(item => ({
        id: item.id,
        name: item.title,        // 映射 title -> name
        location: item.destination, // 映射 destination -> location
        time: String(item.days),    // 映射 days -> time
        style: item.class ? getClassText(item.class) : '', // 把数字转回文字(可选)
        imageUrl: item.image || defaultImage, // 如果后端没图，用默认图
        author: item.author // 保留作者信息
      }))
    } else {
      trips.value = []
    }
  } catch (error) {
    console.error('获取行程失败:', error)
  }
}

// 辅助函数：把数据库里的 class 数字转回文字显示（如果 TripCard 需要展示风格的话）
const getClassText = (classVal) => {
  const map = { 1: '休闲', 2: '美食', 3: '商务', 4: '家庭' }
  return map[classVal] || ''
}

// 处理 FilterBar 传来的筛选事件
const handleTripFilter = (filters) => {
  // filters 格式: { location: "北京", style: "food", time: "3" }

  // 转换为后端需要的参数名
  const apiParams = {
    destination: filters.location, // 对应后端的 destination
    style: filters.style,          // 对应后端的 style (leisure/food...)
    days: filters.time             // 对应后端的 days
  }

  // 发起请求
  fetchTrips(apiParams)
}

// 处理 SearchBar 的输入 (这里简单处理为搜地点)
const handleSearchInput = (val) => {
  // 当搜索框回车或点击搜索时触发
  fetchTrips({ destination: val })
}

// 页面加载时获取所有数据
onMounted(() => {
  fetchTrips()
})
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

.main {
  background-color: #121212; /* 确保背景色与你的主题一致 */
  min-height: 100vh;
}
</style>
