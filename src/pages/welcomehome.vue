<template>
  <div class="page-wrapper">
    <v-container class="py-6 px-md-10 px-4" fluid>

      <v-row align="stretch" class="mb-8">
        <v-col cols="12" lg="8" md="7">
          <v-card class="showcase-card elevation-3 rounded-xl overflow-hidden h-100">
            <div class="swiper-wrapper">
              <SwiperCard />
            </div>
          </v-card>
        </v-col>

        <v-col class="d-flex flex-column justify-space-between" cols="12" lg="4" md="5">
          <v-card class="welcome-banner pa-6 rounded-xl elevation-3 d-flex flex-column justify-center flex-grow-1 text-white">
            <div class="d-flex align-center mb-3">
              <v-icon class="mr-2" icon="mdi-compass-outline" size="36" />
              <h1 class="text-h4 font-weight-bold">探索 Eztrip</h1>
            </div>
            <p class="text-body-1 mb-6 opacity-90">
              融合 AI 智能生成与高德地图精准规划，定制属于你的独一无二旅程。让每一次出发都简单、高效、省心！
            </p>
            <div class="d-flex gap-3">
              <v-btn
                class="text-primary font-weight-bold"
                color="white"
                prepend-icon="mdi-plus-circle"
                size="large"
                variant="elevated"
                @click="openCreateDialog"
              >
                立即发起行程
              </v-btn>
              <v-btn
                color="white"
                size="large"
                to="/AI"
                variant="outlined"
              >
                咨询 AI 导游
              </v-btn>
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-card border class="mb-10 pa-6 rounded-xl elevation-1 guide-container">
        <div class="d-flex align-center mb-4">
          <v-icon class="mr-2" color="#903DFE" icon="mdi-school" size="28" />
          <h2 class="text-h5 font-weight-bold text-grey-darken-3">3步轻松玩转平台</h2>
        </div>

        <v-row>
          <v-col cols="12" md="4">
            <v-sheet class="pa-4 rounded-lg bg-grey-lighten-4 h-100 border">
              <div class="d-flex align-center mb-2">
                <v-avatar class="text-white font-weight-bold mr-2 text-caption" color="#903DFE" size="28">1</v-avatar>
                <span class="font-weight-bold text-subtitle-1">定制基础行程</span>
              </div>
              <p class="text-body-2 text-grey-darken-2 lh-md">
                您可以随时在侧边栏或直接点击这里
                <v-chip
                  class="mx-1 font-weight-bold cursor-pointer hover-pulse"
                  color="#903DFE"
                  prepend-icon="mdi-plus"
                  size="small"
                  variant="flat"
                  @click="openCreateDialog"
                >
                  创建新行程
                </v-chip>
                唤起新建窗口，设定目的地与出行天数。
              </p>
            </v-sheet>
          </v-col>

          <v-col cols="12" md="4">
            <v-sheet class="pa-4 rounded-lg bg-grey-lighten-4 h-100 border">
              <div class="d-flex align-center mb-2">
                <v-avatar class="text-white font-weight-bold mr-2 text-caption" color="#3F51B5" size="28">2</v-avatar>
                <span class="font-weight-bold text-subtitle-1">AI 赋能 + 高德定位</span>
              </div>
              <p class="text-body-2 text-grey-darken-2 lh-md">
                在行程规划页面，使用
                <v-chip
                  class="mx-1 font-weight-bold cursor-pointer"
                  color="#3F51B5"
                  prepend-icon="mdi-robot"
                  size="small"
                  to="/AI"
                  variant="flat"
                >
                  AI 规划导游
                </v-chip>
                生成行程细节，并联动高德地图打卡路线路线。
              </p>
            </v-sheet>
          </v-col>

          <v-col cols="12" md="4">
            <v-sheet class="pa-4 rounded-lg bg-grey-lighten-4 h-100 border">
              <div class="d-flex align-center mb-2">
                <v-avatar class="text-white font-weight-bold mr-2 text-caption" color="#00897B" size="28">3</v-avatar>
                <span class="font-weight-bold text-subtitle-1">社区发现与复刻</span>
              </div>
              <p class="text-body-2 text-grey-darken-2 lh-md">
                遇到心仪的优质达人路线？直接点击行程卡片右上方的
                <v-chip
                  class="mx-1 font-weight-bold cursor-pointer"
                  color="#00897B"
                  prepend-icon="mdi-star"
                  size="small"
                  variant="flat"
                  @click="scrollToTrips"
                >
                  收藏路线
                </v-chip>
                保存至侧边栏，随时借鉴与复刻。
              </p>
            </v-sheet>
          </v-col>
        </v-row>
      </v-card>

      <div id="trips-section" class="d-flex align-center justify-space-between mb-4 px-2">
        <div>
          <h2 class="text-h5 font-weight-bold text-grey-darken-3">热门行程灵感广场</h2>
          <span class="text-caption text-grey">探索达人们分享的精选旅行路线</span>
        </div>
      </div>

      <v-card class="pa-4 mb-6 rounded-xl elevation-1">
        <div class="d-flex flex-wrap align-center gap-4">
          <div style="flex: 1; min-width: 280px;">
            <FilterBar @filter="handleTripFilter" />
          </div>
          <v-btn
            class="px-6 rounded-lg font-weight-bold ml-2"
            color="#903DFE"
            :loading="searching"
            prepend-icon="mdi-magnify"
            size="large"
            variant="elevated"
            @click="handleSearchClick"
          >
            查询路线
          </v-btn>
        </div>
      </v-card>

      <v-row gutter="20">
        <v-col
          v-for="(trip, index) in trips"
          :key="trip.trip_id || index"
          cols="12"
          lg="3"
          md="4"
          sm="6"
        >
          <TripCard :trip="trip" />
        </v-col>

        <v-col v-if="trips.length === 0 && !searching" class="text-center py-16" cols="12">
          <v-icon class="mb-3" color="grey-lighten-1" icon="mdi-map-search-outline" size="64" />
          <div class="text-grey-darken-1 text-h6">暂无符合条件的行程，来做第一个分享的人吧！</div>
          <v-btn class="mt-4" color="#903DFE" variant="tonal" @click="openCreateDialog">立即创建</v-btn>
        </v-col>
      </v-row>
    </v-container>

    <CreateTripDialog
      v-model="showCreateDialog"
      @trip-created="handleTripCreated"
    />
  </div>
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
  const showCreateDialog = ref(false) // 控制创建弹窗

  const defaultImage = 'https://picsum.photos/1920/1073?random.jpg'

  // 筛选条件状态
  const filtersState = ref({
    destination: '',
    class_type: null,
    days: null,
  })

  // 唤起创建行程对话框
  function openCreateDialog () {
    showCreateDialog.value = true
  }

  // 页面滚动到行程列表区
  function scrollToTrips () {
    const el = document.querySelector('#trips-section')
    if (el) el.scrollIntoView({ behavior: 'smooth' })
  }

  // 创建成功回调
  function handleTripCreated (newTrip) {
    // 自动刷新一下列表
    fetchTripsByApi()
  }

  // class 数字 -> 文本
  function getClassText (classVal) {
    const map = { 1: '休闲', 2: '美食', 3: '商务', 4: '家庭' }
    return map[classVal] || ''
  }

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

  async function fetchTripsByApi (params = {}) {
    searching.value = true
    try {
      const res = await axios.get('/api/public_trips/search_trips', {
        params: { limit: 200, offset: 0, ...params },
      })
      trips.value = adaptTrips(res.data || [])
    } catch (error) {
      console.error('获取公开行程失败:', error)
      trips.value = []
    } finally {
      searching.value = false
    }
  }

  function handleTripFilter (filters) {
    const styleMap = {
      休闲: 1, leisure: 1,
      美食: 2, food: 2,
      商务: 3, business: 3,
      家庭: 4, family: 4,
    }
    filtersState.value.destination = (filters.location || '').trim()
    filtersState.value.class_type = styleMap[filters.style] ?? null

    const daysVal = filters.time
    filtersState.value.days
      = daysVal != null && String(daysVal).trim() !== '' && !Number.isNaN(Number(daysVal))
        ? Number(daysVal)
        : null
  }

  async function handleSearchClick () {
    await fetchTripsByApi({
      destination: filtersState.value.destination || undefined,
      class_type: filtersState.value.class_type ?? undefined,
      days: filtersState.value.days ?? undefined,
    })
  }

  onMounted(async () => {
    await fetchTripsByApi()
  })
</script>

<style scoped>
.page-wrapper {
  background-color: #FAF8FF;
  min-height: 100vh;
  width: 100%;
}

/* 轮播卡片高度优化 */
.showcase-card {
  height: 380px;
  background: #000;
}
.swiper-wrapper {
  height: 100%;
  width: 100%;
}

/* 右侧迎新 Banner 渐变紫 */
.welcome-banner {
  background: linear-gradient(135deg, #6A4AC5 0%, #903DFE 100%);
  height: 380px;
}

/* 鼠标悬停时的动效提示 */
.cursor-pointer {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.cursor-pointer:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(144, 61, 254, 0.3);
}

.lh-md {
  line-height: 1.8 !important;
}

.gap-3 {
  gap: 12px;
}
</style>
