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

    <v-row v-else>
      <!-- 左侧：信息 + 编辑 -->
      <v-col cols="12" md="6">
        <v-card class="mb-4" variant="tonal">
          <v-card-title class="d-flex align-center justify-space-between">
            基本信息
            <v-chip
              v-if="showFavoriteCount"
              color="primary"
              size="small"
              variant="outlined"
            >
              收藏人数：{{ favoriteCount }}
            </v-chip>
            <v-chip
              v-else
              color="grey"
              size="small"
              variant="outlined"
            >
              {{ favoriteHint }}
            </v-chip>
          </v-card-title>

          <v-card-text>
            <!-- 展示模式 -->
            <template v-if="!editing">
              <div class="info-row">
                <span class="label">名称：</span>
                <span>{{ tripDetail.trip_name }}</span>
              </div>
              <div class="info-row">
                <span class="label">目的地：</span>
                <span>{{ tripDetail.destination }}</span>
              </div>
              <div class="info-row">
                <span class="label">开始日期：</span>
                <span>{{ tripDetail.start_date }}</span>
              </div>
              <div class="info-row">
                <span class="label">结束日期：</span>
                <span>{{ tripDetail.end_date }}</span>
              </div>
              <div class="info-row">
                <span class="label">更新时间：</span>
                <span>{{ tripDetail.updated_at || '-' }}</span>
              </div>

              <v-divider class="my-4" />

              <div class="info-row">
                <span class="label">审核：</span>
                <span>{{ statusText }}</span>
              </div>
              <div v-if="tripDetail.publish_status === 'rejected'" class="mt-2 text-error">
                未通过原因：{{ tripDetail.review_comment || '（无）' }}
              </div>
            </template>

            <!-- 编辑模式 -->
            <template v-else>
              <v-form ref="formRef" v-model="formValid" lazy-validation>
                <v-text-field
                  v-model="editForm.trip_name"
                  density="comfortable"
                  label="行程名称"
                  :rules="[rules.required]"
                  variant="outlined"
                />
                <v-text-field
                  v-model="editForm.destination"
                  density="comfortable"
                  label="目的地"
                  :rules="[rules.required]"
                  variant="outlined"
                />

                <v-row>
                  <!-- 开始日期 -->
                  <v-col cols="12" md="6">
                    <v-menu
                      v-model="menuStart"
                      :close-on-content-click="false"
                      min-width="auto"
                      transition="scale-transition"
                    >
                      <template #activator="{ props }">
                        <v-text-field
                          v-bind="props"
                          v-model="editForm.start_date"
                          density="comfortable"
                          label="开始日期"
                          prepend-inner-icon="mdi-calendar-start"
                          readonly
                          :rules="[rules.required]"
                          variant="outlined"
                        />
                      </template>

                      <v-date-picker
                        :model-value="parseYMD(editForm.start_date)"
                        @update:model-value="onPickStart"
                      />
                    </v-menu>
                  </v-col>

                  <!-- 结束日期 -->
                  <v-col cols="12" md="6">
                    <v-menu
                      v-model="menuEnd"
                      :close-on-content-click="false"
                      min-width="auto"
                      transition="scale-transition"
                    >
                      <template #activator="{ props }">
                        <v-text-field
                          v-bind="props"
                          v-model="editForm.end_date"
                          density="comfortable"
                          label="结束日期"
                          prepend-inner-icon="mdi-calendar-end"
                          readonly
                          :rules="[rules.required, rules.dateOrder]"
                          variant="outlined"
                        />
                      </template>

                      <v-date-picker
                        :min="parseYMD(editForm.start_date)"
                        :model-value="parseYMD(editForm.end_date)"
                        @update:model-value="onPickEnd"
                      />
                    </v-menu>
                  </v-col>
                </v-row>

                <!-- ✅ 收藏行程完全不可编辑：公开/发布禁用 -->
                <v-switch
                  v-model="editForm.is_public"
                  color="success"
                  :disabled="!canEdit"
                  inset
                  label="公开（允许他人看到并收藏）"
                />

                <v-select
                  v-model="editForm.publish_action"
                  density="comfortable"
                  :disabled="!canEdit"
                  hint="选择提交审核/取消发布"
                  item-title="text"
                  item-value="value"
                  :items="publishActions"
                  label="发布操作"
                  persistent-hint
                  variant="outlined"
                />

                <div v-if="!canEdit" class="text-caption text-grey-darken-1 mt-2">
                  该行程为收藏行程：只能查看，不能修改公开与审核状态
                </div>
              </v-form>
            </template>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- 右侧：地图 -->
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
.info-row {
  display: flex;
  margin-bottom: 8px;
}
.label {
  width: 90px;
  color: #666;
  font-weight: 600;
}
</style>
