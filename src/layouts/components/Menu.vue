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
          <v-icon class="arrow-icon" small>
            {{ expand ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </v-icon>
        </div>
      </v-list-item>

      <!-- 我的行程（二级，动态列表） -->
      <v-expand-transition>
        <div v-if="expand">
          <v-list-item
            v-for="trip in myTrips"
            :key="trip.trip_id"
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
          <v-icon class="arrow-icon" small>
            {{ expand2 ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </v-icon>
        </div>
      </v-list-item>

      <!-- 收藏（二级，动态列表） -->
      <v-expand-transition>
        <div v-if="expand2">
          <v-list-item
            v-for="trip in favoriteTrips"
            :key="trip.trip_id"
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
    </v-list>
  </v-navigation-drawer>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'Menu',
    data () {
      return {
        expand: false,
        expand2: false,
        selectedTripId: null, // 当前选中的 trip_id
        myTrips: [], // 我的行程
        favoriteTrips: [], // 收藏行程
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
      // 从 localStorage 里拿 user_id（第 4 部分会讲登录时怎么存）
      getUserIdFromStorage () {
        const userStr = localStorage.getItem('user')
        if (!userStr) return null
        try {
          const user = JSON.parse(userStr)
          return user.user_id || user.id || null
        } catch {
          return null
        }
      },
      async loadTrips () {
        const userId = this.getUserIdFromStorage()
        if (!userId) {
          console.warn('未获取到 user_id，可能尚未登录')
          return
        }

        try {
          const res = await axios.get('/api/trips', {
            params: { user_id: userId },
          })
          const trips = res.data || []

          // 根据 is_collected 字段拆分我的行程 & 收藏，并按 trip_id 排序
          this.myTrips = trips
            .filter(t => !t.is_collected)
            .sort((a, b) => a.trip_id - b.trip_id)

          this.favoriteTrips = trips
            .filter(t => t.is_collected)
            .sort((a, b) => a.trip_id - b.trip_id)
        } catch (error) {
          console.error('加载行程失败', error)
        }
      },
      // 点击某个行程
      selectTrip (trip) {
        this.selectedTripId = trip.trip_id
        // 通知父组件（如果你有用）
        this.$emit('select', trip)

        // 跳转到 /trip/:tripId
        // 同时把 trip_name 作为 query 带给 trip.vue
        this.$router.push({
          name: 'Trip',
          params: { tripId: trip.trip_id },
          query: { tripName: trip.trip_name },
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
