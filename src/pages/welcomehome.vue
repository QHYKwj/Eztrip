<template>
  <v-main class="main">
    <v-container fluid px-0>
      <!-- 筛选栏 + 查询按钮 -->
      <div class="filter-container">
        <div class="filter-row">
          <div style="flex: 1">
            <FilterBar @filter="handleTripFilter" />
          </div>

          <v-btn
            color="primary"
            :loading="searching"
            prepend-icon="mdi-magnify"
            variant="elevated"
            @click="handleSearchClick"
          >
            查询
          </v-btn>
        </div>
      </div>


      <!-- 轮播卡片 (保持不变) -->
      <v-card class="swiper-card" rounded="lg">
        <SwiperCard />
      </v-card>

      <!-- 行程卡片 -->
      <v-row class="trip-row" gutter="20">
        <v-col
          v-for="(trip, index) in trips"
          :key="trip.id || index"
          :cols="12"
          :lg="3"
          :md="8"
        >
          <TripCard :trip="trip" />
        </v-col>

        <v-col v-if="trips.length === 0" class="text-center mt-10" cols="12">
          <div class="text-grey text-h6">暂无符合条件的行程</div>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup>
  import axios from 'axios'
  import { onMounted, ref } from 'vue'
  import CreateTripDialog from '@/components/createTripDialog.vue'
  import FilterBar from '@/components/FilterBar.vue'
  import SwiperCard from '@/components/SwiperCard.vue'
  import TripCard from '@/components/TripCard.vue'

  const trips = ref([])
  const searching = ref(false)

  const defaultImage = 'https://picsum.photos/1920/1073?random.jpg'

  // ✅ 当前筛选条件（由 FilterBar 更新，点“查询”才生效）
  const filtersState = ref({
    destination: '',
    class_type: null,
    days: null,
  })

  // class 数字 -> 文本
  function getClassText (classVal) {
    const map = { 1: '休闲', 2: '美食', 3: '商务', 4: '家庭' }
    return map[classVal] || ''
  }

  // 后端数据 -> TripCard 需要字段
  function adaptTrips (items = []) {
    return items.map(item => ({
      trip_id: item.trip_id,
      trip_name: item.title,
      destination: item.destination,
      days: item.days,
      class: item.class,
      style: getClassText(item.class),
      created_at: item.created_at,
      author: item.creator_username || item.owner_user_id,
      imageUrl: item.image || defaultImage,
    }))
  }

  // ✅ 调后端搜索 API（点按钮才调）
  async function fetchTripsByApi (params = {}) {
    searching.value = true
    try {
      const res = await axios.get('/api/public_trips/search_trips', {
        params: {
          limit: 200,
          offset: 0,
          ...params,
        },
      })
      trips.value = adaptTrips(res.data || [])
    } catch (error) {
      console.error('获取公开行程失败:', error)
      trips.value = []
    } finally {
      searching.value = false
    }
  }

  // FilterBar 回传：{ location, style, time }
  function handleTripFilter (filters) {
    const styleMap = {
      休闲: 1, leisure: 1,
      美食: 2, food: 2,
      商务: 3, business: 3,
      家庭: 4, family: 4,
    }

    filtersState.value.destination = (filters.location || '').trim()
    filtersState.value.class_type = styleMap[filters.style] ?? null

    // days：允许空
    const daysVal = filters.time
    filtersState.value.days
      = daysVal != null && String(daysVal).trim() !== '' && !Number.isNaN(Number(daysVal))
        ? Number(daysVal)
        : null
  }

  // 点击“查询”：才把 filtersState 作为 params 调 API
  async function handleSearchClick () {
    await fetchTripsByApi({
      destination: filtersState.value.destination || undefined,
      class_type: filtersState.value.class_type ?? undefined,
      days: filtersState.value.days ?? undefined,
    })
  }

  // 初始：先拉全部公开（可选）
  onMounted(async () => {
    await fetchTripsByApi()
  })
</script>

<style scoped>
.filter-container {
  padding: 0 20px;
  margin: 16px 0 6px;
}

.filter-row {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0 20px;
  gap: 16px;
}


.swiper-card {
  background: #F3F2FD;
  height: 30vh;
  width: 40vh;
  display: flex;
  align-items: stretch;
  box-shadow: 0px 0px 2px 5px #F3F2FD;
  margin: 20px auto;
}

.trip-row {
  padding: 0 16px;
  margin-bottom: 20px;
}

:deep(.v-col) {
  padding: 0 10px;
  margin-bottom: 20px;
}

.main {
  background-color: #ffffff;
  min-height: 100vh;
}
</style>
