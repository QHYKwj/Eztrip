<template>
  <div class="page-wrapper">
    <!-- 采用与首页统一的流式对称布局 -->
    <v-container class="py-6 px-md-10 px-4" fluid>

      <!-- 1. 顶部导览 Banner 区 -->
      <v-card class="plan-header-card pa-6 rounded-xl elevation-2 mb-8 text-white d-flex flex-column flex-md-row justify-space-between align-md-center">
        <div>
          <div class="d-flex align-center mb-2">
            <v-icon class="mr-2" icon="mdi-map-check-outline" size="32" />
            <h1 class="text-h4 font-weight-bold">我的旅行管理中心</h1>
          </div>
          <p class="text-body-1 opacity-90 mb-0">
            集中管理你创建的专属行程与从社区收藏的优质打卡路线
          </p>
        </div>

        <div class="mt-4 mt-md-0 d-flex align-center gap-3">
          <v-chip class="font-weight-bold" color="white" size="large" variant="outlined">
            <v-icon icon="mdi-folder-outline" start />
            共 {{ myTrips.length + favoriteTrips.length }} 个路线
          </v-chip>
          <v-btn
            class="text-primary font-weight-bold"
            color="white"
            prepend-icon="mdi-plus-circle"
            size="large"
            variant="elevated"
            @click="showCreateDialog = true"
          >
            发起新行程
          </v-btn>
        </div>
      </v-card>

      <!-- 骨架屏加载状态 -->
      <v-row v-if="loading" class="mb-6">
        <v-col
          v-for="n in 4"
          :key="n"
          cols="12"
          lg="3"
          md="4"
          sm="6"
        >
          <v-skeleton-loader class="rounded-lg" type="card, article" />
        </v-col>
      </v-row>

      <!-- 正常展示区 -->
      <template v-else>
        <!-- 2. 我创建的行程模块 -->
        <div class="trip-section mb-8">
          <div class="section-header d-flex align-center justify-space-between mb-4">
            <div class="d-flex align-center cursor-pointer" @click="myTripsExpanded = !myTripsExpanded">
              <v-icon class="mr-2" color="#903DFE" icon="mdi-briefcase-account" size="26" />
              <h3 class="text-h5 font-weight-bold text-grey-darken-3 mb-0 mr-3">我创建的路线</h3>
              <v-chip class="font-weight-bold" color="#903DFE" size="small" variant="flat">
                {{ myTrips.length }}
              </v-chip>
            </div>

            <v-btn
              color="grey-darken-1"
              icon
              variant="text"
              @click="myTripsExpanded = !myTripsExpanded"
            >
              <v-icon>{{ myTripsExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            </v-btn>
          </div>

          <v-expand-transition>
            <div v-show="myTripsExpanded">
              <v-row v-if="myTrips.length > 0">
                <v-col
                  v-for="(trip, index) in myTrips"
                  :key="trip.trip_id || index"
                  cols="12"
                  lg="3"
                  md="4"
                  sm="6"
                  xl="2"
                >
                  <TripCard :trip="trip" />
                </v-col>
              </v-row>

              <!-- 精美空状态 -->
              <v-card v-else class="empty-card pa-10 rounded-xl text-center border elevation-0 bg-grey-lighten-5">
                <v-icon class="mb-3" color="grey-lighten-1" icon="mdi-map-marker-plus-outline" size="64" />
                <h4 class="text-h6 font-weight-bold text-grey-darken-2 mb-1">还没有定制过专属行程</h4>
                <p class="text-body-2 text-grey mb-4">借助 AI 与高德地图，仅需几分钟即可快速生成路线</p>
                <v-btn color="#903DFE" prepend-icon="mdi-plus" variant="flat" @click="showCreateDialog = true">
                  立即定制路线
                </v-btn>
              </v-card>
            </div>
          </v-expand-transition>
        </div>

        <v-divider class="mb-8" />

        <!-- 3. 我收藏的行程模块 -->
        <div class="trip-section mb-10">
          <div class="section-header d-flex align-center justify-space-between mb-4">
            <div class="d-flex align-center cursor-pointer" @click="favoriteTripsExpanded = !favoriteTripsExpanded">
              <v-icon class="mr-2" color="#E91E63" icon="mdi-heart-multiple" size="26" />
              <h3 class="text-h5 font-weight-bold text-grey-darken-3 mb-0 mr-3">我收藏的路线</h3>
              <v-chip class="font-weight-bold" color="pink" size="small" variant="flat">
                {{ favoriteTrips.length }}
              </v-chip>
            </div>

            <v-btn
              color="grey-darken-1"
              icon
              variant="text"
              @click="favoriteTripsExpanded = !favoriteTripsExpanded"
            >
              <v-icon>{{ favoriteTripsExpanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
            </v-btn>
          </div>

          <v-expand-transition>
            <div v-show="favoriteTripsExpanded">
              <v-row v-if="favoriteTrips.length > 0">
                <v-col
                  v-for="(trip, index) in favoriteTrips"
                  :key="trip.trip_id || index"
                  cols="12"
                  lg="3"
                  md="4"
                  sm="6"
                  xl="2"
                >
                  <TripCard :trip="trip" />
                </v-col>
              </v-row>

              <!-- 精美空状态 -->
              <v-card v-else class="empty-card pa-10 rounded-xl text-center border elevation-0 bg-grey-lighten-5">
                <v-icon class="mb-3" color="grey-lighten-1" icon="mdi-heart-broken-outline" size="64" />
                <h4 class="text-h6 font-weight-bold text-grey-darken-2 mb-1">暂无心仪的收藏路线</h4>
                <p class="text-body-2 text-grey mb-4">去灵感广场逛逛，将达人们分享的好去处一键收进口袋</p>
                <v-btn color="pink" prepend-icon="mdi-compass-outline" to="/home" variant="tonal">
                  探索灵感广场
                </v-btn>
              </v-card>
            </div>
          </v-expand-transition>
        </div>
      </template>
    </v-container>

    <!-- 挂载新建行程对话框，实现页内交互闭环 -->
    <CreateTripDialog
      v-model="showCreateDialog"
      @trip-created="loadTrips"
    />
  </div>
</template>

<script setup>
  import axios from 'axios'
  import { computed, onMounted, ref } from 'vue'
  import CreateTripDialog from '@/components/createTripDialog.vue'
  import TripCard from '@/components/TripCard.vue'

  const myTripsExpanded = ref(true)
  const favoriteTripsExpanded = ref(true)
  const showCreateDialog = ref(false)

  const rawTrips = ref([])
  const loading = ref(false)

  const defaultImage = 'https://picsum.photos/1920/1083?random.jpg'

  // 从本地缓存读取 user_id
  function getUserIdFromStorage () {
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user')
    if (!userStr) return null
    try {
      const user = JSON.parse(userStr)
      return user.user_id || user.id || null
    } catch {
      return null
    }
  }

  // 加载行程主数据
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

  // 映射处理为 TripCard 标准格式
  const mappedTrips = computed(() => {
    const userId = getUserIdFromStorage()

    return rawTrips.value.map(t => ({
      trip_id: t.trip_id,
      trip_name: t.trip_name || t.title,
      destination: t.destination,
      days: t.days,
      class: t.class,
      class_text: t.class_text,
      is_collected: !!t.is_collected,
      owner_user_id: t.owner_user_id,

      // 兼容底层变量
      id: t.trip_id,
      name: t.trip_name || t.title,
      imageUrl: t.image || defaultImage,
      style: t.class_text || '',
      desc: t.destination ? `目的地：${t.destination}` : '',
      start_date: t.start_date,
      end_date: t.end_date,
      editable: userId != null && Number(t.owner_user_id) === Number(userId),
    }))
  })

  // 过滤我创建的
  const myTrips = computed(() => {
    const userId = getUserIdFromStorage()
    if (!userId) return []
    return mappedTrips.value.filter(t => Number(t.owner_user_id) === Number(userId))
  })

  // 过滤我收藏的
  const favoriteTrips = computed(() => {
    return mappedTrips.value.filter(t => t.is_collected)
  })

  onMounted(() => {
    loadTrips()
  })
</script>

<style scoped>
.page-wrapper {
  background-color: #FAF8FF;
  min-height: 100vh;
  width: 100%;
}

/* 顶部导览卡片紫渐变 */
.plan-header-card {
  background: linear-gradient(135deg, #6A4AC5 0%, #903DFE 100%);
}

.cursor-pointer {
  cursor: pointer;
  user-select: none;
}

.gap-3 {
  gap: 12px;
}
</style>
