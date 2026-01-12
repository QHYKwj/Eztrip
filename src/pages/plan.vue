<template>
  <v-main class="main">
    <v-container fluid px-0>
      <!-- 顶部：只保留“全部查询” -->
      <div class="toolbar">
        <h1 class="page-title">我的行程</h1>
      </div>

      <!-- 我的行程 -->
      <div class="trip-section">
        <div class="section-header">
          <div class="title-with-btn">
            <h3 class="section-title">我创建的</h3>
            <v-btn class="toggle-btn" icon @click="myTripsExpanded = !myTripsExpanded">
              <v-icon>{{ myTripsExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            </v-btn>
          </div>
        </div>

        <v-row v-if="myTripsExpanded" class="trip-row" gutter="20">
          <v-col
            v-for="(trip, index) in myTrips"
            :key="trip.trip_id || index"
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
            <h3 class="section-title">我收藏的</h3>
            <v-btn class="toggle-btn" icon @click="favoriteTripsExpanded = !favoriteTripsExpanded">
              <v-icon>{{ favoriteTripsExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            </v-btn>
          </div>
        </div>

        <v-row v-if="favoriteTripsExpanded" class="trip-row" gutter="20">
          <v-col
            v-for="(trip, index) in favoriteTrips"
            :key="trip.trip_id || index"
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
  import axios from 'axios'
  import { computed, onMounted, ref } from 'vue'
  import TripCard from '@/components/TripCard.vue'

  const myTripsExpanded = ref(true)
  const favoriteTripsExpanded = ref(true)

  const rawTrips = ref([])
  const loading = ref(false)

  const defaultImage = 'https://cdn.vuetifyjs.com/images/cards/cooking.png'

  // sessionStorage 获取 user_id（沿用你写法）
  function getUserIdFromStorage () {
    const userStr = sessionStorage.getItem('user')
    if (!userStr) return null
    try {
      const user = JSON.parse(userStr)
      return user.user_id || user.id || null
    } catch {
      return null
    }
  }

  // ✅ 一次性拿“我的+收藏”
  async function loadTrips () {
    const userId = getUserIdFromStorage()
    if (!userId) {
      rawTrips.value = []
      return
    }

    loading.value = true
    try {
      const res = await axios.get('/api/user/trips/list', {
        params: { user_id: userId },
      })
      rawTrips.value = Array.isArray(res.data) ? res.data : []
    } catch (error) {
      console.error('加载行程失败:', error)
      rawTrips.value = []
    } finally {
      loading.value = false
    }
  }

  // ✅ 映射成 TripCard 需要的字段（重点：destination/days/class 都要传）
  const mappedTrips = computed(() => {
    const userId = getUserIdFromStorage()

    return rawTrips.value.map(t => ({
      // TripCard 跳转用
      trip_id: t.trip_id,
      trip_name: t.trip_name,

      // ✅ TripCard 展示用（你之前缺的就是这些）
      destination: t.destination,
      days: t.days,
      class: t.class,
      class_text: t.class_text,

      // 收藏态
      is_collected: !!t.is_collected,

      // 权限判断用
      owner_user_id: t.owner_user_id,

      // 兼容字段（避免 TripCard 内部还用 name/imageUrl/style）
      id: t.trip_id,
      name: t.trip_name,
      imageUrl: defaultImage,
      style: t.class_text || '',
      desc: t.destination ? `目的地：${t.destination}` : '',
      start_date: t.start_date,
      end_date: t.end_date,

      editable: userId != null && Number(t.owner_user_id) === Number(userId),
    }))
  })

  const myTrips = computed(() => {
    const userId = getUserIdFromStorage()
    if (!userId) return []
    return mappedTrips.value.filter(t => Number(t.owner_user_id) === Number(userId))
  })

  const favoriteTrips = computed(() => {
    return mappedTrips.value.filter(t => t.is_collected)
  })

  onMounted(() => {
    loadTrips()
  })
</script>

<style scoped>
.main {
  background-color: #ffffff;
  min-height: 100vh;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  margin: 10px 0 16px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #333;
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
  font-size: 1.2rem;
  color: #333;
  font-weight: 600;
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
