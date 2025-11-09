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
              icon 
              class="toggle-btn"
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
          gutter="20" 
          class="trip-row"
          v-if="myTripsExpanded"
        >
          <v-col 
            v-for="(trip, index) in myTrips" 
            :key="trip.id || index" 
            :cols="12"   
            :md="8"      
            :lg="3"    
          >
            <TripCard :trip="trip" />
          </v-col>
          <v-col v-if="myTrips.length === 0" :cols="12" class="no-trip">
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
              icon 
              class="toggle-btn"
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
          gutter="20" 
          class="trip-row"
          v-if="favoriteTripsExpanded"
        >
          <v-col 
            v-for="(trip, index) in favoriteTrips" 
            :key="trip.id || index" 
            :cols="12"   
            :md="8"      
            :lg="3"    
          >
            <TripCard :trip="trip" />
          </v-col>
          <v-col v-if="favoriteTrips.length === 0" :cols="12" class="no-trip">
            暂无收藏的行程
          </v-col>
        </v-row>
      </div>
    </v-container>
  </v-main>
</template>

<script setup>
// 逻辑部分与之前一致，此处省略（保持不变）
import { computed, ref } from 'vue'
import SearchBar from '@/components/SearchBar.vue'
import TripCard from '@/components/TripCard.vue'

const myTripsExpanded = ref(true)
const favoriteTripsExpanded = ref(true)

function handleSearch(query) { console.log('搜索:', query) }
function handleInput(value) { console.log('输入:', value) }

const originalTrips = ref([
  { id: 1, name: '我的行程1', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', type: 'my' },
  { id: 2, name: '我的行程2', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', type: 'my' },
  { id: 3, name: '收藏行程1', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', type: 'favorite' },
  { id: 4, name: '我的行程3', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', type: 'my' },
  { id: 5, name: '收藏行程2', imageUrl: 'https://cdn.vuetifyjs.com/images/cards/cooking.png', type: 'favorite' },
])

const myTrips = computed(() => originalTrips.value.filter(trip => trip.type === 'my'))
const favoriteTrips = computed(() => originalTrips.value.filter(trip => trip.type === 'favorite'))
</script>

<style scoped>
/* 搜索栏样式保持不变 */
.search-container {
  margin: 0 0 20px 0;
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 0 20px;
}

/* 核心修改1：卡片区域背景改为白色 */
.trip-section {
  margin-bottom: 30px;
  padding: 16px; /* 保留内边距 */
  border-radius: 8px;
  background-color: white; /* 改为白色背景 */
  /* 可选：添加轻微阴影增强层次感 */
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* 标题区域布局 */
.section-header {
  margin-bottom: 16px;
}

.title-with-btn {
  display: flex;
  align-items: center;
  gap: 8px; /* 文字与按钮间距 */
}

.section-title {
  font-size: 1.5rem;
  color: #333;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
}

/* 核心修改2：修复按钮椭圆问题，确保为正圆形 */
.toggle-btn {
  color: #666;
  /* 关键：固定宽高并设置圆形边框 */
  width: 24px;
  height: 24px;
  min-width: 24px; /* 覆盖Vuetify默认最小宽度 */
  border-radius: 50% !important; /* 强制圆形 */
  padding: 0 !important; /* 清除内边距，避免变形 */
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, color 0.2s;
}

.toggle-btn:hover {
  color: #333;
  transform: scale(1.1);
}

/* 图标大小适配按钮 */
.toggle-btn :deep(.v-icon) {
  font-size: 16px !important; /* 图标尺寸与按钮匹配 */
}

/* 行程列表样式 */
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