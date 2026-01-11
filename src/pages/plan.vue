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
      </div>

      <!-- 我的行程 -->
      <div class="trip-section">
        <div class="section-header">
          <div class="title-with-btn">
            <h2 class="section-title">我的行程</h2>
            <v-btn
              class="toggle-btn"
              icon
              @click="myTripsExpanded = !myTripsExpanded"
            >
              <v-icon>
                {{ myTripsExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
              </v-icon>
            </v-btn>
          </div>
        </div>

        <!-- 行程列表 -->
        <v-row
          v-if="myTripsExpanded"
          class="trip-row"
          gutter="20"
        >
          <v-col
            v-for="(trip, index) in myTrips"
            :key="trip.id || index"
            :cols="12"
            :lg="3"
            :md="8"
          >
            <TripCard :trip="trip" />
          </v-col>
          <v-col v-if="myTrips.length === 0" class="no-trip" :cols="12">
            暂无我的行程
          </v-col>
        </v-row>
      </div>

      <!-- 收藏的行程 -->
      <div class="trip-section">
        <div class="section-header">
          <div class="title-with-btn">
            <h2 class="section-title">收藏的行程</h2>
            <v-btn
              class="toggle-btn"
              icon
              @click="favoriteTripsExpanded = !favoriteTripsExpanded"
            >
              <v-icon>
                {{ favoriteTripsExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
              </v-icon>
            </v-btn>
          </div>
        </div>

        <!-- 行程列表 -->
        <v-row
          v-if="favoriteTripsExpanded"
          class="trip-row"
          gutter="20"
        >
          <v-col
            v-for="(trip, index) in favoriteTrips"
            :key="trip.id || index"
            :cols="12"
            :lg="3"
            :md="8"
          >
            <TripCard :trip="trip" />
          </v-col>
          <v-col v-if="favoriteTrips.length === 0" class="no-trip" :cols="12">
            暂无收藏的行程
          </v-col>
        </v-row>
      </div>
    </v-container>
  </v-main>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import axios from 'axios' // 新增：引入axios用于接口请求
import SearchBar from '@/components/SearchBar.vue'
import TripCard from '@/components/TripCard.vue'

// 展开/收起状态（保留原有逻辑）
const myTripsExpanded = ref(true)
const favoriteTripsExpanded = ref(true)

// 新增：存储从后端获取的原始行程数据
const myTripsList = ref([]) // 我的行程原始数据
const favoriteTripsList = ref([]) // 收藏行程原始数据
// 新增：默认封面图（同welcomehome.vue，防止卡片无图）
const defaultImage = 'https://cdn.vuetifyjs.com/images/cards/cooking.png'

// 搜索/输入方法（保留原有逻辑，可后续扩展）
function handleSearch (query) {
  console.log('搜索:', query)
  // 可选扩展：搜索时重新请求接口过滤数据
  // loadTrips({ destination: query })
}
function handleInput (value) {
  console.log('输入:', value)
}

// 新增：模仿Menu.vue获取用户ID的方法
const getUserIdFromStorage = () => {
  const userStr = sessionStorage.getItem('user')
  if (!userStr) return null
  try {
    const user = JSON.parse(userStr)
    return user.user_id || user.id || null
  } catch {
    return null
  }
}

// 新增：模仿Menu.vue的loadTrips + welcomehome.vue的fetchTrips逻辑，加载行程数据
const loadTrips = async (params = {}) => {
  const userId = getUserIdFromStorage() || 1 // 暂时默认1，方便调试
  try {
    // 1. 获取我的行程（模仿Menu.vue调用/my_trips接口）
    const myTripsRes = await axios.get('/api/trip/my_trips', {
      params: { 
        user_id: userId,
        ...params // 支持传入搜索/筛选参数
      },
    })

    // 2. 映射后端字段到TripCard需要的格式（模仿welcomehome.vue的字段映射）
    if (myTripsRes.data && myTripsRes.data.trips) {
      myTripsList.value = myTripsRes.data.trips.map(item => ({
        id: item.id,
        name: item.title, // 后端title -> 卡片需要的name
        location: item.destination, // 后端destination -> 卡片location
        time: String(item.days), // 后端days -> 卡片time
        style: item.class ? getClassText(item.class) : '', // 行程风格（可选）
        imageUrl: item.image || defaultImage, // 图片（无则用默认图）
        author: item.author, // 作者信息
        type: 'my' // 标记为我的行程，保持原有过滤逻辑
      }))
    } else {
      myTripsList.value = []
    }

    // 3. 获取收藏行程（待后端实现/favorites接口后补充）
    // 目前先置空，后续替换为真实接口请求
    // const favoriteRes = await axios.get('/api/trip/favorites', {
    //   params: { user_id: userId }
    // })
    // if (favoriteRes.data && favoriteRes.data.trips) {
    //   favoriteTripsList.value = favoriteRes.data.trips.map(item => ({
    //     id: item.id,
    //     name: item.title,
    //     location: item.destination,
    //     time: String(item.days),
    //     style: item.class ? getClassText(item.class) : '',
    //     imageUrl: item.image || defaultImage,
    //     author: item.author,
    //     type: 'favorite' // 标记为收藏行程
    //   }))
    // } else {
    //   favoriteTripsList.value = []
    // }
    favoriteTripsList.value = [] // 临时置空

  } catch (error) {
    console.error('加载行程失败:', error)
    myTripsList.value = []
    favoriteTripsList.value = []
  }
}

// 新增：模仿welcomehome.vue的辅助函数，转换行程风格数字为文字
const getClassText = (classVal) => {
  const map = { 1: '休闲', 2: '美食', 3: '商务', 4: '家庭' }
  return map[classVal] || ''
}

// 调整：基于后端数据计算我的行程/收藏行程（保留原有computed逻辑）
const myTrips = computed(() => myTripsList.value.filter(trip => trip.type === 'my'))
const favoriteTrips = computed(() => favoriteTripsList.value.filter(trip => trip.type === 'favorite'))

// 新增：页面挂载时加载行程数据
onMounted(() => {
  loadTrips()
})
</script>

<style scoped>
/* 原有样式保持不变 */
.search-container {
  margin: 0 0 20px 0;
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 0 20px;
}

.trip-section {
  margin-bottom: 30px;
  padding: 16px;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.section-header {
  margin-bottom: 16px;
}

.title-with-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title {
  font-size: 1.5rem;
  color: #333;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
}

.toggle-btn {
  color: #666;
  width: 24px;
  height: 24px;
  min-width: 24px;
  border-radius: 50% !important;
  padding: 0 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, color 0.2s;
}

.toggle-btn:hover {
  color: #333;
  transform: scale(1.1);
}

.toggle-btn :deep(.v-icon) {
  font-size: 16px !important;
}

.trip-row {
  padding: 0;
  margin-bottom: 0;
}

:deep(.v-col) {
  padding: 0 10px;
  margin-bottom: 20px;
}

.no-trip {
  text-align: center;
  padding: 20px;
  color: #666;
  font-style: italic;
}
</style>