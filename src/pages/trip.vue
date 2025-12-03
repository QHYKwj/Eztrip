<template>
  <v-container class="py-6">
    <v-row>
      <v-col cols="12">
        <h2 class="text-h5 font-weight-bold mb-4">
          {{ tripDetail?.trip_name || tripNameFromRoute || '行程详情' }}
        </h2>
      </v-col>
    </v-row>

    <!-- 加载中 / 错误提示 -->
    <v-row v-if="loading">
      <v-col cols="12">
        <v-skeleton-loader type="article" />
      </v-col>
    </v-row>

    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert dense type="error">
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- 正常内容 -->
    <v-row v-else>
      <v-col cols="12" md="6">
        <v-card class="mb-4" variant="tonal">
          <v-card-title>基本信息</v-card-title>
          <v-card-text>
            <div class="info-row">
              <span class="label">名称：</span>
              <span>{{ tripDetail.trip_name }}</span>
            </div>
            <div class="info-row">
              <span class="label">目的地：</span>
              <span>{{ tripDetail.destination }}</span>
            </div>
            <div class="info-row">
              <span class="label">开始时间：</span>
              <span>{{ tripDetail.start_time }}</span>
            </div>
            <div class="info-row">
              <span class="label">结束时间：</span>
              <span>{{ tripDetail.end_time }}</span>
            </div>
            <div class="info-row">
              <span class="label">创建时间：</span>
              <span>{{ tripDetail.created_at }}</span>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 高德静态地图 -->
      <v-col class="d-flex flex-column align-center" cols="12" md="6">
        <v-card class="w-100">
          <v-card-title>目的地地图</v-card-title>
          <v-card-text class="d-flex justify-center">
            <v-skeleton-loader
              v-if="mapLoading"
              height="300"
              type="image"
              width="600"
            />
            <v-img
              v-else
              class="rounded-lg elevation-2"
              cover
              height="300"
              :src="mapUrl"
              width="600"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'Trip',
    data () {
      return {
        userId: null,
        tripId: null,
        tripNameFromRoute: '',
        tripDetail: null,
        mapUrl: '',
        loading: false,
        mapLoading: false,
        error: null,
      }
    },
    created () {
      this.tripId = this.$route.params.tripId
      this.tripNameFromRoute = this.$route.query.tripName || ''
      this.userId = this.getUserIdFromStorage()

      if (!this.userId) {
        this.error = '未登录或 user_id 丢失，请重新登录。'
        return
      }

      if (!this.tripId) {
        this.error = '未指定行程 ID。'
        return
      }

      this.fetchTripDetail()
    },
    methods: {
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
      async fetchTripDetail () {
        this.loading = true
        this.error = null
        try {
          const res = await axios.get('/api/trip/detail', {
            params: {
              user_id: this.userId,
              trip_id: this.tripId,
              trip_name: this.tripNameFromRoute || undefined,
            },
          })
          this.tripDetail = res.data

          // 后端返回的经纬度字段名按你真实情况调整
          const lng = this.tripDetail.lng
          const lat = this.tripDetail.lat

          if (lng && lat) {
            this.fetchMapUrl(lng, lat)
          }
        } catch (error) {
          console.error(error)
          this.error = '获取行程详情失败'
        } finally {
          this.loading = false
        }
      },
      async fetchMapUrl (lng, lat) {
        this.mapLoading = true
        try {
          const res = await axios.get('/api/map/url', {
            params: {
              lng,
              lat,
              zoom: 14,
              width: 600,
              height: 300,
              label: this.tripDetail.destination?.[0] || 'A',
            },
          })
          this.mapUrl = res.data.url
        } catch (error) {
          console.error('获取地图失败', error)
        } finally {
          this.mapLoading = false
        }
      },
    },
  }
</script>

<style scoped>
.info-row {
  display: flex;
  margin-bottom: 6px;
}
.label {
  width: 80px;
  color: #666;
  font-weight: 500;
}
</style>
