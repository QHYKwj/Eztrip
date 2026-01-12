<template>
  <v-container class="py-6">
    <v-row align="center" class="mb-2">
      <v-col cols="12" md="8">
        <div class="d-flex align-center">
          <h2 class="text-h5 font-weight-bold">
            {{ tripDetail?.trip_name || '行程详情' }}
          </h2>

          <v-chip
            class="ml-3"
            :color="statusColor"
            size="small"
            variant="outlined"
          >
            {{ statusText }}
          </v-chip>

          <v-chip
            class="ml-2"
            :color="tripDetail?.is_public ? 'success' : 'grey'"
            size="small"
            variant="outlined"
          >
            {{ tripDetail?.is_public ? '公开' : '未公开' }}
          </v-chip>
        </div>

        <div class="text-grey-darken-1 mt-1">
          Trip ID：{{ tripId }} · 创建时间：{{ tripDetail?.created_at || '-' }}
        </div>
      </v-col>

      <v-col class="d-flex justify-end" cols="12" md="4">
        <!-- ✅ 只有 owner 才显示编辑按钮；收藏行程显示只读 -->
        <v-btn
          v-if="!editing && canEdit"
          color="primary"
          prepend-icon="mdi-pencil"
          variant="elevated"
          @click="enterEdit"
        >
          编辑
        </v-btn>

        <v-btn
          v-else-if="!editing && !canEdit"
          color="grey"
          prepend-icon="mdi-lock"
          variant="outlined"
          @click="showSnack('收藏行程不可编辑', 'error')"
        >
          只读
        </v-btn>

        <template v-else>
          <v-btn
            class="mr-2"
            color="grey"
            variant="text"
            @click="cancelEdit"
          >
            取消
          </v-btn>
          <v-btn
            color="primary"
            :loading="saving"
            prepend-icon="mdi-content-save"
            variant="elevated"
            @click="saveEdit"
          >
            保存
          </v-btn>
        </template>
      </v-col>
    </v-row>

    <!-- 加载 / 错误 -->
    <v-row v-if="loading">
      <v-col cols="12">
        <v-skeleton-loader type="article" />
      </v-col>
    </v-row>

    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert dense type="error" variant="tonal">
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>
    <div v-else class="trip-body">
  <v-row class="d-flex align-stretch fill-height">
    <v-col cols="12" md="5" class="d-flex">
        <v-card class="rounded-lg shadow-sm border w-100" elevation="0">
          <v-card-title class="d-flex align-center justify-space-between bg-grey-lighten-4 py-3">
            <span class="text-subtitle-1 font-weight-bold">行程基本信息</span>
            <v-chip v-if="showFavoriteCount" color="primary" size="small" variant="flat">
              <v-icon start icon="mdi-heart" size="14"></v-icon>
              {{ favoriteCount }} 人收藏
            </v-chip>
          </v-card-title>

          <v-card-text class="pa-6">
            <template v-if="!editing">
              <v-row>
                <v-col cols="12" class="py-3">
                  <div class="text-subtitle-1 text-grey-darken-1">行程名称</div>
                  <div class="text-h6 font-weight-bold">{{ tripDetail.trip_name }}</div>
                </v-col>
                
                <v-col cols="12" class="py-3">
                  <div class="text-subtitle-1 text-grey-darken-1">目的地</div>
                  <div class="text-h6 font-weight-bold">
                    <v-icon color="primary" class="mr-1">mdi-map-marker</v-icon>
                    {{ tripDetail.destination }}
                  </div>
                </v-col>

                <v-col cols="6" class="py-3">
                  <div class="text-subtitle-1 text-grey-darken-1">开始日期</div>
                  <div class="text-body-1 font-weight-medium">{{ tripDetail.start_date }}</div>
                </v-col>

                <v-col cols="6" class="py-3">
                  <div class="text-subtitle-1 text-grey-darken-1">结束日期</div>
                  <div class="text-body-1 font-weight-medium">{{ tripDetail.end_date }}</div>
                </v-col>

                <v-col cols="12" class="py-3">
                  <div class="text-subtitle-1 text-grey-darken-1">审核状态</div>
                  <v-chip :color="statusColor" size="small" label class="mt-1">
                    {{ statusText }}
                  </v-chip>
                </v-col>
              </v-row>
            </template>

            <template v-else>
              </template>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="7" class="d-flex">
        <v-card class="rounded-lg border w-100 d-flex flex-column" elevation="0">
          <v-card-title class="text-subtitle-2 text-grey-darken-1">目的地地图</v-card-title>
          <v-card-text class="pa-0 flex-grow-1">
            <v-skeleton-loader v-if="mapLoading" type="image" height="100%" />
            <v-img
              v-else
              :src="mapUrl"
              cover
              class="bg-grey-lighten-3 fill-height"
              min-height="400"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
    <!-- 保存结果提示 -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="2200">
      {{ snack.text }}
    </v-snackbar>
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
        tripDetail: null,

        mapUrl: '',
        favoriteCount: 0,

        loading: false,
        mapLoading: false,
        error: null,

        menuStart: false,
        menuEnd: false,

        editing: false,
        saving: false,
        formValid: false,

        editForm: {
          trip_name: '',
          destination: '',
          start_date: '',
          end_date: '',
          is_public: true,
          publish_action: 'keep',
        },

        publishActions: [
          { text: '不更改发布状态', value: 'keep' },
          { text: '提交审核（申请发布）', value: 'submit' },
          { text: '取消发布（变为草稿）', value: 'unpublish' },
        ],

        snack: { show: false, text: '', color: 'success' },

        rules: {
          required: v => !!v || '必填',
          date: v => /^\d{4}-\d{2}-\d{2}$/.test(v) || '日期格式应为 YYYY-MM-DD',
          dateOrder: () => true,
        },
      }
    },

    computed: {
      // ✅ 是否允许编辑：只有 owner 才可以
      canEdit () {
        // 先用后端明确返回的 is_owner
        if (typeof this.tripDetail?.is_owner === 'boolean') return this.tripDetail.is_owner
        // 兜底：用 owner_user_id 比对
        if (this.tripDetail?.owner_user_id != null && this.userId != null) {
          return Number(this.tripDetail.owner_user_id) === Number(this.userId)
        }
        return false
      },

      statusText () {
        const s = this.tripDetail?.publish_status
        if (s === 'draft') return '未发布（草稿）'
        if (s === 'pending') return '待审核'
        if (s === 'published') return '已发布'
        if (s === 'rejected') return '未通过'
        return '未知状态'
      },
      statusColor () {
        const s = this.tripDetail?.publish_status
        if (s === 'draft') return 'grey'
        if (s === 'pending') return 'warning'
        if (s === 'published') return 'success'
        if (s === 'rejected') return 'error'
        return 'grey'
      },

      showFavoriteCount () {
        return !!(this.tripDetail?.is_public && this.tripDetail?.publish_status === 'published')
      },
      favoriteHint () {
        if (!this.tripDetail) return '-'
        if (!this.tripDetail.is_public) return '未公开'
        if (this.tripDetail.publish_status !== 'published') return `未发布（${this.statusText}）`
        return '-'
      },
    },

    watch: {
      '$route.params.tripId' () {
        this.syncRouteParams()
        this.fetchTripDetail()
      },
    },

    created () {
      this.userId = this.getUserIdFromStorage()
      this.syncRouteParams()
      this.fetchTripDetail()
    },

    methods: {
      syncRouteParams () {
        this.tripId = this.$route.params.tripId
      },

      getUserIdFromStorage () {
        // 修改为 sessionStorage
        const userStr = sessionStorage.getItem('user')
        if (!userStr) return null
        try {
          const user = JSON.parse(userStr)
          return user.user_id || null
        } catch {
          return null
        }
      },

      enterEdit () {
        // ✅ 收藏行程不可编辑：不允许进入编辑态
        if (!this.canEdit) {
          this.showSnack('收藏行程不可编辑', 'error')
          return
        }

        this.editing = true
        this.editForm.trip_name = this.tripDetail.trip_name
        this.editForm.destination = this.tripDetail.destination
        this.editForm.start_date = this.tripDetail.start_date
        this.editForm.end_date = this.tripDetail.end_date
        this.editForm.is_public = !!this.tripDetail.is_public
        this.editForm.publish_action = 'keep'
      },

      cancelEdit () {
        this.editing = false
      },

      showSnack (text, color = 'success') {
        this.snack.text = text
        this.snack.color = color
        this.snack.show = true
      },

      async fetchTripDetail () {
        // 如果没有 userId，先尝试获取一次（防止刷新页面丢失）
        if (!this.userId) {
          this.userId = this.getUserIdFromStorage()
        }

        if (!this.tripId) {
          this.error = '未指定行程 ID。'
          return
        }

        this.loading = true
        this.error = null
        this.tripDetail = null
        this.mapUrl = ''
        this.favoriteCount = 0

        try {
          // ✅ 修改这里：直接把 tripId 拼接到 URL 后面
          const res = await axios.get(`/api/trip/detail/${this.tripId}`)

          // 后端返回的数据包了一层 { data: ... }
          this.tripDetail = res.data.data

          // 这里要做个字段映射，因为后端返回的是 title，前端用的是 trip_name
          this.tripDetail.trip_name = this.tripDetail.title

          // 如果需要地图经纬度逻辑，后面可以补，目前先注释掉防报错
          if (this.tripDetail.lng && this.tripDetail.lat) {
            await this.fetchMapUrl(this.tripDetail.lng, this.tripDetail.lat)
          }

          if (this.showFavoriteCount) {
            await this.fetchFavoriteCount()
          }
        } catch (error) {
          console.error(error)
          this.error = '获取行程详情失败'
        } finally {
          this.loading = false
          this.editing = false
        }
      },

      async fetchMapUrl (lng, lat) {
        this.mapLoading = true
        try {
          const res = await axios.get('/api/map/url', {
            params: { lng, lat, zoom: 14, width: 600, height: 300 },
          })
          this.mapUrl = res.data.url
        } catch (error) {
          console.error('获取地图失败', error)
        } finally {
          this.mapLoading = false
        }
      },

      async fetchFavoriteCount () {
        try {
          const res = await axios.get('/api/trip/favorite-count', {
            params: { trip_id: this.tripId },
          })
          this.favoriteCount = res.data.count || 0
        } catch (error) {
          console.error('获取收藏人数失败', error)
        }
      },

      async saveEdit () {
        // ✅ 双保险：收藏行程不允许保存
        if (!this.canEdit) {
          this.showSnack('收藏行程不可编辑', 'error')
          return
        }

        if (!/^\d{4}-\d{2}-\d{2}$/.test(this.editForm.start_date)
          || !/^\d{4}-\d{2}-\d{2}$/.test(this.editForm.end_date)) {
          this.showSnack('日期格式应为 YYYY-MM-DD', 'error')
          return
        }
        if (new Date(this.editForm.end_date) < new Date(this.editForm.start_date)) {
          this.showSnack('结束日期不能早于开始日期', 'error')
          return
        }

        this.saving = true
        try {
          const payload = {
            user_id: this.userId,
            trip_id: Number(this.tripId),
            trip_name: this.editForm.trip_name,
            destination: this.editForm.destination,
            start_date: this.editForm.start_date,
            end_date: this.editForm.end_date,
            is_public: this.editForm.is_public ? 1 : 0,
            publish_action: this.editForm.publish_action,
          }

          await axios.put('/api/trip/update', payload)

          this.showSnack('保存成功')
          await this.fetchTripDetail()
        } catch (error) {
          console.error(error)
          this.showSnack('保存失败，请检查后端日志', 'error')
        } finally {
          this.saving = false
        }
      },

      parseYMD (ymd) {
        if (!ymd) return null
        const [y, m, d] = String(ymd).split('-').map(Number)
        if (!y || !m || !d) return null
        return new Date(y, m - 1, d)
      },

      formatYMD (val) {
        const d = new Date(val)
        const y = d.getFullYear()
        const m = String(d.getMonth() + 1).padStart(2, '0')
        const day = String(d.getDate()).padStart(2, '0')
        return `${y}-${m}-${day}`
      },

      onPickStart (val) {
        this.editForm.start_date = this.formatYMD(val)
        if (this.editForm.end_date && this.editForm.end_date < this.editForm.start_date) {
          this.editForm.end_date = this.editForm.start_date
        }
        this.menuStart = false
      },

      onPickEnd (val) {
        this.editForm.end_date = this.formatYMD(val)
        this.menuEnd = false
      },
    },
  }
</script>

<style scoped>
.v-container.fill-height {
  min-height: calc(100vh - 64px - 48px) !important; 
  align-items: stretch;
}

:deep(.v-img__img) {
  object-fit: cover;
}

.v-card {
  display: flex;
  flex-direction: column;
}

.info-group .text-h5 {
  margin-bottom: 24px;
}

.fill-height {
  height: 100% !important;
}
.trip-body {
  display: flex;
  flex: 1;
  min-height: calc(100vh - 64px - 48px);
}
</style>
