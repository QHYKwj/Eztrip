<template>
  <v-navigation-drawer class="drawer" elevation="0" permanent>
    <v-container class="logo-container">
      <img alt="Logo" class="logo" src="@/assets/logo2.svg">
    </v-container>

    <v-list density="comfortable">
      <v-list-subheader class="menu-title">所有行程</v-list-subheader>

      <!-- 我的行程（一级） -->
      <v-list-item class="menu-item level-1 clickable" @click="toggleExpand">
        <div class="menu-line level-1-line">
          <v-icon class="item-icon">mdi-briefcase</v-icon>
          <span class="item-title">我的行程</span>
          <v-spacer />
          <v-icon class="arrow-icon" size="small">
            {{ expand ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </v-icon>
        </div>
      </v-list-item>

      <!-- 我的行程（二级，动态列表） -->
      <v-expand-transition>
        <div v-if="expand">
          <v-list-item
            v-for="trip in myTrips"
            :key="'my-' + trip.trip_id"
            class="menu-item level-2 clickable"
            @click="selectTrip(trip)"
          >
            <div class="menu-line level-2-line">
              <v-icon class="item-icon">mdi-map-marker</v-icon>
              <span
                :class="[
                  'item-title',
                  selectedTripId === trip.trip_id ? 'selected' : ''
                ]"
              >
                {{ trip.trip_name }}
              </span>
            </div>
          </v-list-item>

          <div v-if="myTrips.length === 0" class="empty-tip level-2-line">
            暂无行程
          </div>
        </div>
      </v-expand-transition>

      <!-- 收藏（一级） -->
      <v-list-item class="menu-item level-1 clickable" @click="toggleExpand2">
        <div class="menu-line level-1-line">
          <v-icon class="item-icon">mdi-star</v-icon>
          <span class="item-title">收藏</span>
          <v-spacer />
          <v-icon class="arrow-icon" size="small">
            {{ expand2 ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </v-icon>
        </div>
      </v-list-item>

      <!-- 收藏（二级，动态列表） -->
      <v-expand-transition>
        <div v-if="expand2">
          <v-list-item
            v-for="trip in favoriteTrips"
            :key="'fav-' + trip.trip_id"
            class="menu-item level-2 clickable"
            @click="selectTrip(trip)"
          >
            <div class="menu-line level-2-line">
              <v-icon class="item-icon">mdi-map-marker</v-icon>
              <span
                :class="[
                  'item-title',
                  selectedTripId === trip.trip_id ? 'selected' : ''
                ]"
              >
                {{ trip.trip_name }}
              </span>
            </div>
          </v-list-item>

          <div v-if="favoriteTrips.length === 0" class="empty-tip level-2-line">
            暂无收藏
          </div>
        </div>
      </v-expand-transition>

      <!-- 可选：加载/错误提示 -->
      <div v-if="loading" class="empty-tip" style="padding: 8px 16px;">
        正在加载...
      </div>
      <div v-if="errorMsg" class="empty-tip" style="padding: 8px 16px; color: #c62828;">
        {{ errorMsg }}
      </div>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'Menu',
    data () {
      return {
        expand: true,
        expand2: true,
        selectedTripId: null,

        myTrips: [],
        favoriteTrips: [],

        loading: false,
        errorMsg: '',
      }
    },
    created () {
      this.loadTrips()
    },
    methods: {
      toggleExpand () {
        this.expand = !this.expand
      },
      toggleExpand2 () {
        this.expand2 = !this.expand2
      },

      // 从 sessionStorage 里获取 user_id
      getUserIdFromStorage () {
        const userStr = sessionStorage.getItem('user')
        if (!userStr) return null
        try {
          const user = JSON.parse(userStr)
          return user.user_id || user.id || null
        } catch {
          return null
        }
      },

      // 加载：后端一次返回“我的 + 收藏”
      async loadTrips () {
        const userId = this.getUserIdFromStorage() || 1 // 你调试用的默认 1
        this.loading = true
        this.errorMsg = ''

        try {
          // ✅ 对齐后端：GET /api/trips/list?user_id=xxx
          const res = await axios.get('/api/user/trips/list', {
            params: { user_id: userId },
          })

          // 你的后端返回的是数组 trips（不是 {trips: [...] }）
          const trips = Array.isArray(res.data) ? res.data : []

          // 保险：统一字段（你后端已经是 trip_id / trip_name / owner_user_id / is_collected）
          const normalized = trips.map(t => ({
            trip_id: t.trip_id,
            trip_name: t.trip_name,
            destination: t.destination,
            start_date: t.start_date,
            end_date: t.end_date,
            owner_user_id: t.owner_user_id,
            is_collected: !!t.is_collected,

            // ✅ 前端常用：是否可编辑（你之前提到“自己的行程可编辑，收藏/别人的只读”）
            editable: Number(t.owner_user_id) === Number(userId),
          }))

          // 分组：我的 / 收藏
          this.myTrips = normalized.filter(t => Number(t.owner_user_id) === Number(userId))
          this.favoriteTrips = normalized.filter(t => t.is_collected)

          // 如果当前已在 Trip 详情页，尝试从路由里回显选中项
          const routeTripId = this.$route?.params?.tripId
          if (routeTripId != null) {
            const idNum = Number(routeTripId)
            if (!Number.isNaN(idNum)) this.selectedTripId = idNum
          }
        } catch (error) {
          console.error('加载行程失败', error)
          this.errorMsg = error?.response?.data?.detail || '加载行程失败，请检查后端接口/路由前缀'
          this.myTrips = []
          this.favoriteTrips = []
        } finally {
          this.loading = false
        }
      },

      // 点击某个行程
      selectTrip (trip) {
        this.selectedTripId = trip.trip_id

        // ✅ 把完整 trip（含 editable）抛给父组件/详情页用
        this.$emit('select', trip)

        this.$router.push({
          name: 'Trip',
          params: { tripId: trip.trip_id },
          query: {
            tripName: trip.trip_name,
            editable: trip.editable ? '1' : '0', // 可选：也塞进 query，详情页更好拿
          },
        })
      },
    },
  }
</script>

<style scoped>
.drawer {
  background-color: #F3F2FD !important;
  border: none !important;
  box-shadow: none !important;
}

/* logo */
.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 0;
}
.logo {
  width: 120px;
  height: auto;
}

.menu-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-top: 8px;
  margin-bottom: 4px;
}

/* 通用菜单项样式 */
.menu-item {
  transition: background-color 0.2s;
  border-radius: 8px;
}
.menu-item:hover {
  background-color: #E7E6FB;
}

.menu-line {
  display: flex;
  align-items: center;
  width: 100%;
}

.level-1-line {
  padding-left: 16px;
}
.level-2-line {
  padding-left: 48px;
}

.item-icon {
  margin-right: 8px;
  color: #555;
}

.item-title {
  font-size: 14px;
  color: #333;
}
.arrow-icon {
  color: #555;
}

/* 选中样式 */
.selected {
  font-weight: bold;
  color: #3F51B5;
}

.clickable {
  cursor: pointer;
}

.empty-tip {
  font-size: 13px;
  color: #888;
  padding: 4px 0 8px;
}
</style>
