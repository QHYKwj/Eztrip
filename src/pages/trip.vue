<template>
  <v-container class="py-6">
    <v-row align="center" class="mb-2">
      <v-col cols="12" md="8">
        <div class="d-flex align-center">
          <h2 class="text-h5 font-weight-bold">
            {{ tripDetail?.trip_name || '行程详情' }}
          </h2>

          <v-chip
            v-if="tripDetail?.is_ai === 1"
            class="ai-badge font-weight-bold mr-1 ml-3"
            color="purple-darken-2"
            prepend-icon="mdi-robot-excited"
            size="small"
            variant="elevated"
          >
            AI 智能生成
          </v-chip>

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
        <v-col class="d-flex flex-column" cols="12" md="5">
          <v-card class="rounded-lg shadow-sm border w-100" elevation="0">
            <v-card-title class="d-flex align-center justify-space-between bg-grey-lighten-4 py-3">
              <span class="text-subtitle-1 font-weight-bold">行程基本信息</span>
              <v-chip v-if="showFavoriteCount" color="primary" size="small" variant="flat">
                <v-icon icon="mdi-heart" size="14" start />
                {{ favoriteCount }} 人收藏
              </v-chip>
            </v-card-title>

            <v-card-text class="pa-6">
              <template v-if="!editing">
                <v-row>
                  <v-col class="py-3" cols="12">
                    <div class="text-subtitle-1 text-grey-darken-1">行程名称</div>
                    <div class="text-h6 font-weight-bold">{{ tripDetail.trip_name }}</div>
                  </v-col>

                  <v-col class="py-3" cols="12">
                    <div class="text-subtitle-1 text-grey-darken-1">目的地</div>
                    <div class="text-h6 font-weight-bold">
                      <v-icon class="mr-1" color="primary">mdi-map-marker</v-icon>
                      {{ tripDetail.destination }}
                    </div>
                  </v-col>

                  <v-col class="py-3" cols="6">
                    <div class="text-subtitle-1 text-grey-darken-1">开始日期</div>
                    <div class="text-body-1 font-weight-medium">{{ tripDetail.start_date }}</div>
                  </v-col>

                  <v-col class="py-3" cols="6">
                    <div class="text-subtitle-1 text-grey-darken-1">结束日期</div>
                    <div class="text-body-1 font-weight-medium">{{ tripDetail.end_date }}</div>
                  </v-col>

                  <v-col class="py-3" cols="12">
                    <div class="text-subtitle-1 text-grey-darken-1">审核状态</div>
                    <v-chip class="mt-1" :color="statusColor" label size="small">
                      {{ statusText }}
                    </v-chip>
                  </v-col>
                  <v-col class="py-2" cols="12">
                    <v-btn
                      block
                      :color="favorited ? 'grey-darken-1' : 'red-darken-1'"
                      :loading="favoriting"
                      :prepend-icon="favorited ? 'mdi-heart-off' : 'mdi-heart'"
                      variant="elevated"
                      @click="toggleFavorite"
                    >
                      {{ favorited ? '取消收藏' : '收藏行程' }}
                    </v-btn>
                    <!-- 🌟 增加删除按钮 (仅拥有者或管理员 id=1 可见) 🌟 -->
                    <v-btn
                      v-if="canEdit || userId === 1"
                      block
                      color="error"
                      prepend-icon="mdi-delete"
                      variant="tonal"
                      @click="confirmDeleteTrip"
                    >
                      删除此行程
                    </v-btn>

                    <!-- 烟花画布（覆盖在卡片内部底部，不影响布局） -->
                    <div v-show="fireworks.show" class="fireworks-wrap">
                      <canvas ref="fireCanvas" class="fireworks-canvas" />
                    </div>
                  </v-col>
                  <v-card
                    v-if="tripDetail.remarks && typeof tripDetail.remarks === 'object'"
                    class="rounded-lg shadow-sm border w-100 mt-4"
                    elevation="0"
                  >
                    <v-card-title class="d-flex align-center py-3" style="background-color: #F3F2FD; color: #742DD8;">
                      <v-icon class="mr-2" icon="mdi-robot-outline" />
                      <span class="text-subtitle-1 font-weight-bold">行程贴士与避坑指南</span>
                    </v-card-title>

                    <v-card-text class="pa-5">
                      <v-row>
                        <!-- 概述与基本建议 -->
                        <v-col cols="12" md="6">
                          <div class="mb-4">
                            <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-2">
                              <v-icon class="mr-1" color="primary" size="small">mdi-flag-variant-outline</v-icon> 行程概述
                            </div>
                            <div class="text-body-2 text-grey-darken-1">{{ tripDetail.remarks.overview }}</div>
                          </div>
                          <div class="mb-4">
                            <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-2">
                              <v-icon class="mr-1" color="success" size="small">mdi-weather-partly-cloudy</v-icon> 最佳出行时间
                            </div>
                            <div class="text-body-2 text-grey-darken-1">{{ tripDetail.remarks.best_time }}</div>
                          </div>
                          <div class="mb-4">
                            <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-2">
                              <v-icon class="mr-1" color="warning" size="small">mdi-currency-cny</v-icon> 预估预算
                            </div>
                            <div class="text-body-2 text-grey-darken-1">{{ tripDetail.remarks.budget }}</div>
                          </div>
                        </v-col>

                        <!-- 住宿与美食 -->
                        <v-col cols="12" md="6">
                          <div class="mb-4">
                            <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-2">
                              <v-icon class="mr-1" color="indigo" size="small">mdi-bed</v-icon> 住宿建议
                            </div>
                            <div class="text-body-2 text-grey-darken-1">{{ tripDetail.remarks.accommodation }}</div>
                          </div>
                          <div class="mb-4">
                            <div class="text-subtitle-2 font-weight-bold mb-1 text-grey-darken-2">
                              <v-icon class="mr-1" color="deep-orange" size="small">mdi-silverware-variant</v-icon> 美食推荐
                            </div>
                            <div class="text-body-2 text-grey-darken-1">{{ tripDetail.remarks.food }}</div>
                          </div>
                        </v-col>

                        <v-divider class="my-2" />

                        <!-- 避坑提示 (Tips) -->
                        <v-col cols="12">
                          <div class="text-subtitle-2 font-weight-bold mb-2 text-grey-darken-2">
                            <v-icon class="mr-1" color="error" size="small">mdi-alert-circle-outline</v-icon> 避坑与注意事项
                          </div>
                          <v-list class="pa-0" density="compact">
                            <v-list-item
                              v-for="(tip, idx) in tripDetail.remarks.tips"
                              :key="'tip-'+idx"
                              class="px-0 min-h-0"
                            >
                              <template #prepend>
                                <v-icon class="mr-2" color="error" size="x-small">mdi-asterisk</v-icon>
                              </template>
                              <v-list-item-title class="text-body-2 text-grey-darken-1" style="white-space: normal;">
                                {{ tip }}
                              </v-list-item-title>
                            </v-list-item>
                          </v-list>
                        </v-col>

                        <!-- 行李清单 (Packing) -->
                        <v-col cols="12">
                          <div class="text-subtitle-2 font-weight-bold mb-2 text-grey-darken-2">
                            <v-icon class="mr-1" color="teal" size="small">mdi-bag-checked</v-icon> 专属行李清单
                          </div>
                          <div class="d-flex flex-wrap gap-2">
                            <v-chip
                              v-for="(item, idx) in tripDetail.remarks.packing"
                              :key="'pack-'+idx"
                              class="mb-2 mr-2"
                              color="teal-darken-1"
                              size="small"
                              variant="outlined"
                            >
                              {{ item }}
                            </v-chip>
                          </div>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>

                  <!-- 兼容旧版本的纯文本 Markdown 渲染 (可选) -->
                  <v-card
                    v-else-if="tripDetail.remarks && typeof tripDetail.remarks === 'string'"
                    class="rounded-lg shadow-sm border w-100 mt-4"
                    elevation="0"
                  >
                    <v-card-title class="bg-grey-lighten-4 py-3 text-subtitle-1 font-weight-bold">AI 行程贴士</v-card-title>
                    <v-card-text class="pa-6" style="white-space: pre-wrap;">{{ tripDetail.remarks }}</v-card-text>
                  </v-card>
                </v-row>
              </template>

              <template v-else>
                <v-form v-model="formValid">
                  <v-row>
                    <v-col class="py-2" cols="12">
                      <v-text-field
                        v-model="editForm.trip_name"
                        density="comfortable"
                        label="行程名称"
                        prepend-inner-icon="mdi-rename-box"
                        :rules="[rules.required]"
                        variant="outlined"
                      />
                    </v-col>

                    <v-col class="py-2" cols="12">
                      <v-text-field
                        v-model="editForm.destination"
                        density="comfortable"
                        label="目的地"
                        prepend-inner-icon="mdi-map-marker"
                        :rules="[rules.required]"
                        variant="outlined"
                      />
                    </v-col>

                    <v-col class="py-2" cols="6">
                      <v-text-field
                        v-model="editForm.start_date"
                        density="comfortable"
                        label="开始日期"
                        prepend-inner-icon="mdi-calendar-start"
                        :rules="[rules.required, rules.date]"
                        variant="outlined"
                      />
                    </v-col>

                    <v-col class="py-2" cols="6">
                      <v-text-field
                        v-model="editForm.end_date"
                        density="comfortable"
                        label="结束日期"
                        prepend-inner-icon="mdi-calendar-end"
                        :rules="[rules.required, rules.date]"
                        variant="outlined"
                      />
                    </v-col>
                    <!-- 🌟 新增：AI 行程锦囊编辑区 🌟 -->
                    <v-col cols="12">
                      <v-divider class="mb-4" />
                      <div class="text-subtitle-2 font-weight-bold mb-3 text-primary">修改 AI 行程锦囊</div>
                    </v-col>

                    <!-- 确保 remarks 存在且是个对象才能编辑 -->
                    <template v-if="tripDetail.remarks && typeof tripDetail.remarks === 'object'">
                      <v-col cols="12" md="6">
                        <v-textarea
                          v-model="tripDetail.remarks.overview"
                          auto-grow
                          density="compact"
                          label="行程概述"
                          rows="2"
                          variant="outlined"
                        />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field v-model="tripDetail.remarks.best_time" density="compact" label="最佳出行时间" variant="outlined" />
                        <v-text-field v-model="tripDetail.remarks.budget" density="compact" label="预估预算" variant="outlined" />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="tripDetail.remarks.accommodation"
                          auto-grow
                          density="compact"
                          label="住宿建议"
                          rows="2"
                          variant="outlined"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="tripDetail.remarks.food"
                          auto-grow
                          density="compact"
                          label="美食推荐"
                          rows="2"
                          variant="outlined"
                        />
                      </v-col>
                      <v-col cols="12">
                        <!-- combobox 支持输入后回车变成 chip 数组 -->
                        <v-combobox
                          v-model="tripDetail.remarks.tips"
                          chips
                          clearable
                          closable-chips
                          density="compact"
                          label="避坑提示 (输入后回车添加)"
                          multiple
                          variant="outlined"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-combobox
                          v-model="tripDetail.remarks.packing"
                          chips
                          clearable
                          closable-chips
                          density="compact"
                          label="行李清单 (输入后回车添加)"
                          multiple
                          variant="outlined"
                        />
                      </v-col>
                    </template>

                    <v-col class="py-2" cols="12">
                      <v-switch
                        v-model="editForm.is_public"
                        color="success"
                        inset
                        label="是否公开"
                      />
                    </v-col>

                    <v-col class="py-2" cols="12">
                      <v-select
                        v-model="editForm.publish_action"
                        density="comfortable"
                        item-title="text"
                        item-value="value"
                        :items="publishActions"
                        label="发布操作"
                        prepend-inner-icon="mdi-upload"
                        variant="outlined"
                      />
                    </v-col>
                  </v-row>
                </v-form>
              </template>
            </v-card-text>
          </v-card>

          <div class="mt-4">
            <TripPlanBoard
              :editable="canEdit"
              :trip-id="tripId"
              :user-id="userId"
            />
          </div>
        </v-col>

        <v-col class="d-flex" cols="12" md="7">
          <v-card class="rounded-lg border w-100 d-flex flex-column" elevation="0">
            <v-card-title class="text-subtitle-2 text-grey-darken-1">目的地地图</v-card-title>
            <v-card-text class="pa-0 flex-grow-1">
              <v-skeleton-loader v-if="mapLoading" height="100%" type="image" />
              <!--              <v-img-->
              <!--                v-else-->
              <!--                class="bg-grey-lighten-3 fill-height"-->
              <!--                cover-->
              <!--                min-height="400"-->
              <!--                :src="mapUrl"-->
              <!--              />-->
              <TripMapInteractive
                v-else
                :enable-search="true"
                :lat="Number(tripDetail.lat)"
                :lng="Number(tripDetail.lng)"
                :markers="tagMarkers"
                :pickable="true"
                :zoom="14"
                @map-right-click="handleMapRightClick"
                @pick="handleMapPick"
              />

            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <v-dialog v-model="mapAddDialog.show" max-width="440">
      <v-card class="rounded-lg pa-2">
        <v-card-title class="d-flex align-center font-weight-bold text-subtitle-1 pt-3">
          <v-icon class="mr-2" color="primary">mdi-map-marker-plus</v-icon>
          添加到具体行程路线
        </v-card-title>

        <v-card-text class="py-3">
          <div class="text-caption text-grey-darken-1 mb-4">
            已拾取经纬度: {{ mapAddDialog.lng?.toFixed(5) }}, {{ mapAddDialog.lat?.toFixed(5) }}
          </div>

          <v-text-field
            v-model="mapAddDialog.title"
            autofocus
            density="comfortable"
            label="打卡点名称 / 景点名"
            placeholder="例如：珠江夜游码头"
            variant="outlined"
          />

          <v-select
            v-model="mapAddDialog.dayIndex"
            density="comfortable"
            item-title="text"
            item-value="value"
            :items="dayOptions"
            label="选择加入到第几天"
            variant="outlined"
          />

          <v-select
            v-model="mapAddDialog.placeType"
            density="comfortable"
            :items="['景点', '餐饮', '住宿', '购物', '交通', '休闲']"
            label="分类标签"
            variant="outlined"
          />
        </v-card-text>

        <v-card-actions class="px-4 pb-3 justify-end">
          <v-btn color="grey" variant="text" @click="mapAddDialog.show = false">取消</v-btn>
          <v-btn
            color="primary"
            :disabled="!mapAddDialog.title.trim() || !mapAddDialog.dayIndex"
            :loading="mapAddDialog.loading"
            variant="elevated"
            @click="submitMapAddTag"
          >
            确认加入
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 保存结果提示 -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="2200">
      {{ snack.text }}
    </v-snackbar>
  </v-container>
</template>

<script>
  import axios from 'axios'
  import TripMapInteractive from '@/components/TripMapInteractive.vue'
  import TripPlanBoard from '@/components/TripPlanBoard.vue'
  export default {
    name: 'Trip',
    components: { TripMapInteractive, TripPlanBoard },
    data () {
      return {
        tagMarkers: [], // 未来你从后端取“某个 trip 的 tag 点位列表”
        // 收藏状态
        favorited: false,
        favoriting: false,
        favoriteIds: new Set(),
        favoriteIdsLoaded: false,

        fireworks: {
          show: false,
          rafId: null,
          timer: null,
        },

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
        // 🌟 新增：地图添加点位弹窗状态
        mapAddDialog: {
          show: false,
          lng: null,
          lat: null,
          title: '',
          dayIndex: 1,
          placeType: '景点',
          loading: false,
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
      // 🌟 根据开始和结束日期计算一共有多少天选项
      dayOptions () {
        if (!this.tripDetail?.start_date || !this.tripDetail?.end_date) return [{ text: '第 1 天', value: 1 }]
        const start = new Date(this.tripDetail.start_date)
        const end = new Date(this.tripDetail.end_date)
        const days = Math.max(1, Math.floor((end - start) / (1000 * 60 * 60 * 24)) + 1)
        return Array.from({ length: days }, (_, i) => ({
          text: `第 ${i + 1} 天`,
          value: i + 1,
        }))
      },
    },

    watch: {
      '$route.params.tripId': {
        async handler () {
          this.syncRouteParams()

          // ✅ 重置 UI 状态（防止旧页面残留）
          this.stopFireworks()
          this.favorited = false
          this.favoriting = false
          this.mapUrl = ''
          this.favoriteCount = 0
          this.tripDetail = null
          this.error = null
          this.editing = false

          await this.fetchTripDetail()
        },
      },
    },

    async created () {
      this.userId = this.getUserIdFromStorage()
      this.syncRouteParams()

      // 先拉收藏列表（兜底），再拉详情
      await this.fetchUserFavoriteIds()
      await this.fetchTripDetail()
    },
    beforeUnmount () {
      this.stopFireworks()
    },

    methods: {
      // 🌟 处理地图右键点击
      handleMapRightClick ({ lng, lat }) {
        // 如果是收藏的他人行程（不可编辑），给出提示后直接拦截
        if (!this.canEdit) {
          this.showSnack('收藏的行程为只读，不可在地图上添加路线', 'warning')
          return
        }

        this.mapAddDialog.lng = Number(lng)
        this.mapAddDialog.lat = Number(lat)
        this.mapAddDialog.title = ''
        this.mapAddDialog.dayIndex = 1
        this.mapAddDialog.placeType = '景点'
        this.mapAddDialog.show = true
      },

      // 🌟 提交将右键点位加入路线
      async submitMapAddTag () {
        if (!this.mapAddDialog.title.trim()) return

        this.mapAddDialog.loading = true
        try {
          const payload = {
            user_id: Number(this.userId),
            trip_id: Number(this.tripId),
            day_index: Number(this.mapAddDialog.dayIndex),
            title: this.mapAddDialog.title.trim(),
            place_type: this.mapAddDialog.placeType,
            lng: this.mapAddDialog.lng, // 传入精准经纬度
            lat: this.mapAddDialog.lat,
          }

          await axios.post('/api/trip_plan/item/add', payload)

          this.showSnack(`🎉 已成功加入第 ${payload.day_index} 天行程！`, 'success')
          this.mapAddDialog.show = false

          // 重新拉取地图标注列表，地图立刻画出最新折线
          await this.fetchPlanMarkers()
        } catch (error) {
          console.error('地图添加点位失败:', error)
          this.showSnack(error?.response?.data?.detail || '添加失败，请重新试一次', 'error')
        } finally {
          this.mapAddDialog.loading = false
        }
      },

      handleMapPick (p) {
        // p = {lng, lat, name?}
        // 你可以：弹窗问“要不要把这个点作为一个tag加入第X天”
        console.log('用户点选坐标：', p)
      },
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

      // 🌟 新增：删除行程功能 🌟
      async confirmDeleteTrip () {
        const isConfirm = window.confirm('确定要永久删除这个行程吗？该操作不可恢复！')
        if (!isConfirm) return

        try {
          await axios.delete('/api/trip/delete', {
            params: { trip_id: this.tripId, user_id: this.userId },
          })

          this.showSnack('行程已成功删除！', 'success')
          setTimeout(() => {
            this.$router.push('/plan')
          }, 1000)
        } catch (error) {
          console.error('删除失败:', error)
          this.showSnack('删除失败: ' + (error.response?.data?.detail || error.message), 'error')
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
        // ✅ 防报错：如果旧数据 remarks 为空或纯文本，给它初始化一个标准的空字典
        if (!this.tripDetail.remarks || typeof this.tripDetail.remarks !== 'object') {
          this.tripDetail.remarks = {
            overview: '', best_time: '', budget: '', accommodation: '', food: '', packing: [], tips: [],
          }
        }
      },
      // 🌟 修改：取消编辑时，重新拉取详情以丢弃未保存的修改 🌟
      async cancelEdit () {
        this.editing = false
      },

      showSnack (text, color = 'success') {
        this.snack.text = text
        this.snack.color = color
        this.snack.show = true
      },

      async fetchTripDetail () {
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
        this.favoriteCount = 0

        try {
          const res = await axios.get('/api/trip/detail', {
            params: { user_id: this.userId, trip_id: this.tripId },
          })

          this.tripDetail = res.data
          this.favorited = !!this.tripDetail?.is_collected

          if (this.favoriteIdsLoaded && this.userId && this.favoriteIds.has(Number(this.tripId))) this.favorited = true

          if (this.showFavoriteCount) {
            await this.fetchFavoriteCount()
          }
        } catch (error) {
          console.error(error)
          this.error = '获取行程详情失败'
        } finally {
          // 🌟 1. 首先尽快将 loading 设为 false，让页面的主体文字和左侧信息秒开！
          this.loading = false
          this.editing = false
        }

        // 🌟 2. 页面已经展示后，在后台异步拉取地图标记点（就算点很多，也不卡页面文字加载）
        if (this.tripDetail) {
          this.fetchPlanMarkers()
          if (this.tripDetail.lng && this.tripDetail.lat) {
            this.fetchMapUrl(this.tripDetail.lng, this.tripDetail.lat)
          }
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
            // ✅ 透传修改后的 AI 锦囊给后端
            remarks: this.tripDetail.remarks,
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
      getUserId () {
        // 你已经有 getUserIdFromStorage，但这里收藏逻辑用这个更通用
        const raw = sessionStorage.getItem('user') || localStorage.getItem('user')
        if (!raw) return null
        try {
          const u = JSON.parse(raw)
          return u.user_id || u.id || null
        } catch {
          return null
        }
      },

      // ✅ 获取“当前用户收藏的 trip_id 列表”（带 sessionStorage 缓存）
      async fetchUserFavoriteIds () {
        const userId = this.getUserId()
        if (!userId) {
          this.favoriteIds = new Set()
          this.favoriteIdsLoaded = true
          return
        }

        const cacheKey = `favorite_trip_ids_${userId}`
        const ttlMs = 60 * 1000

        // 1) 读缓存
        try {
          const cachedRaw = sessionStorage.getItem(cacheKey)
          if (cachedRaw) {
            const cached = JSON.parse(cachedRaw)
            if (cached?.ts && Array.isArray(cached?.trip_ids) && (Date.now() - cached.ts) < ttlMs) {
              this.favoriteIds = new Set(cached.trip_ids.map(Number))
              this.favoriteIdsLoaded = true
              return
            }
          }
        } catch {
          // ignore
        }

        // 2) 请求后端
        try {
          const res = await axios.post('/api/collect/favorite/list', { user_id: userId })
          if (res.data?.code === 200 && Array.isArray(res.data?.data?.trip_ids)) {
            const ids = res.data.data.trip_ids.map(Number)
            this.favoriteIds = new Set(ids)
            this.favoriteIdsLoaded = true
            sessionStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), trip_ids: ids }))
          } else {
            this.favoriteIds = new Set()
            this.favoriteIdsLoaded = true
          }
        } catch (error) {
          console.error('获取用户收藏列表失败:', error)
          this.favoriteIds = new Set()
          this.favoriteIdsLoaded = true
        }
      },

      // ✅ 统一入口：收藏/取消收藏切换
      async toggleFavorite () {
        const userId = this.getUserId()
        const tripId = Number(this.tripId)

        if (!userId) {
          this.showSnack('请先登录再收藏', 'error')
          return
        }
        if (!tripId) {
          this.showSnack('行程ID缺失，无法操作', 'error')
          return
        }

        // 防重复点击
        if (this.favoriting) return

        await (this.favorited ? this.unfavoriteTrip(userId, tripId) : this.favoriteTrip(userId, tripId))
      },

      // ✅ 收藏
      async favoriteTrip (userId, tripId) {
        this.favoriting = true
        try {
          const res = await axios.post('/api/collect/favorite/add', {
            user_id: userId,
            trip_id: tripId,
          })

          if (res.data?.code === 200) {
            this.favorited = true

            // 同步本地集合 + 缓存
            const cacheKey = `favorite_trip_ids_${userId}`
            this.favoriteIds.add(Number(tripId))
            sessionStorage.setItem(cacheKey, JSON.stringify({
              ts: Date.now(),
              trip_ids: Array.from(this.favoriteIds),
            }))

            this.showSnack('收藏成功 🎉', 'success')
            await this.fetchFavoriteCount()
            this.playFireworks()
            return
          }

          this.showSnack(res.data?.message || '收藏失败', 'warning')
        } catch (error) {
          // 400 = 重复收藏（你已说明）
          if (error.response?.status === 400) {
            this.favorited = true
            const cacheKey = `favorite_trip_ids_${userId}`
            this.favoriteIds.add(Number(tripId))
            sessionStorage.setItem(cacheKey, JSON.stringify({
              ts: Date.now(),
              trip_ids: Array.from(this.favoriteIds),
            }))
            this.showSnack('你已经收藏过这个行程啦 ❤️', 'info')
            await this.fetchFavoriteCount()
            return
          }

          console.error('收藏失败:', error)
          this.showSnack('收藏失败，请稍后再试', 'error')
        } finally {
          this.favoriting = false
        }
      },

      // ✅ 取消收藏
      async unfavoriteTrip (userId, tripId) {
        this.favoriting = true
        try {
          const res = await axios.post('/api/collect/favorite/remove', {
            user_id: userId,
            trip_id: tripId,
          })

          if (res.data?.code === 200) {
            this.favorited = false

            // 同步本地集合 + 缓存
            const cacheKey = `favorite_trip_ids_${userId}`
            this.favoriteIds.delete(Number(tripId))
            sessionStorage.setItem(cacheKey, JSON.stringify({
              ts: Date.now(),
              trip_ids: Array.from(this.favoriteIds),
            }))

            this.showSnack('已取消收藏', 'success')
            await this.fetchFavoriteCount()
            return
          }

          this.showSnack(res.data?.message || '取消失败', 'warning')
        } catch (error) {
          // 400 = 未收藏无需取消
          if (error.response?.status === 400) {
            this.favorited = false
            const cacheKey = `favorite_trip_ids_${userId}`
            this.favoriteIds.delete(Number(tripId))
            sessionStorage.setItem(cacheKey, JSON.stringify({
              ts: Date.now(),
              trip_ids: Array.from(this.favoriteIds),
            }))
            this.showSnack('你还没收藏这个行程', 'info')
            await this.fetchFavoriteCount()
            return
          }

          console.error('取消收藏失败:', error)
          this.showSnack('取消失败，请稍后再试', 'error')
        } finally {
          this.favoriting = false
        }
      },

      // =======================
      // 🎆 烟花效果（canvas 粒子）
      // =======================
      playFireworks () {
        this.stopFireworks()
        this.fireworks.show = true

        this.$nextTick(() => {
          const canvas = this.$refs.fireCanvas
          if (!canvas) return

          const rect = canvas.getBoundingClientRect()
          canvas.width = Math.floor(rect.width)
          canvas.height = Math.floor(rect.height)

          const ctx = canvas.getContext('2d')
          const W = canvas.width
          const H = canvas.height

          const particles = []
          const bursts = 4
          for (let b = 0; b < bursts; b++) {
            const cx = W * (0.25 + 0.5 * Math.random())
            const cy = H * (0.25 + 0.35 * Math.random())
            const n = 60
            for (let i = 0; i < n; i++) {
              const a = Math.random() * Math.PI * 2
              const sp = 2 + Math.random() * 4
              particles.push({
                x: cx,
                y: cy,
                vx: Math.cos(a) * sp,
                vy: Math.sin(a) * sp,
                life: 60 + Math.random() * 30,
                r: 2 + Math.random() * 2,
                color: ['#ff5252', '#ffd740', '#69f0ae', '#40c4ff', '#b388ff'][Math.floor(Math.random() * 5)],
              })
            }
          }

          const step = () => {
            ctx.clearRect(0, 0, W, H)
            ctx.globalCompositeOperation = 'lighter'

            for (const p of particles) {
              p.life -= 1
              p.vx *= 0.98
              p.vy *= 0.98
              p.vy += 0.06
              p.x += p.vx
              p.y += p.vy

              if (p.life > 0) {
                ctx.beginPath()
                ctx.fillStyle = p.color
                ctx.globalAlpha = Math.max(0, p.life / 90)
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
                ctx.fill()
              }
            }

            ctx.globalAlpha = 1
            ctx.globalCompositeOperation = 'source-over'

            if (particles.some(p => p.life > 0)) {
              this.fireworks.rafId = requestAnimationFrame(step)
            }
          }

          step()

          this.fireworks.timer = setTimeout(() => {
            this.stopFireworks()
          }, 2200)
        })
      },

      stopFireworks () {
        if (this.fireworks.rafId) cancelAnimationFrame(this.fireworks.rafId)
        if (this.fireworks.timer) clearTimeout(this.fireworks.timer)
        this.fireworks.rafId = null
        this.fireworks.timer = null
        this.fireworks.show = false
      },

      // 在 trip.vue 的 methods 中新增此方法：
      async fetchPlanMarkers () {
        try {
          const res = await axios.get('/api/trip_plan/get', {
            params: { user_id: this.userId || 1, trip_id: this.tripId },
          })
          const planData = res.data
          const markersList = []

          if (planData && Array.isArray(planData.days)) {
            for (const day of planData.days) {
              if (Array.isArray(day.items)) {
                for (const [index, item] of day.items.entries()) {
                  // 确保有合法的坐标值
                  if (item.lng && item.lat) {
                    markersList.push({
                      id: item.id,
                      name: item.title,
                      lng: Number(item.lng),
                      lat: Number(item.lat),
                      day: day.day_index, // 第几天
                      seq: index + 1, // 当天第几个打卡点
                      place_type: item.place_type,
                    })
                  }
                }
              }
            }
          }
          // 赋值给绑定的数组传给地图
          this.tagMarkers = markersList
        } catch (error) {
          console.error('获取行程地图标记失败:', error)
        }
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
.fireworks-wrap {
  position: relative;
  width: 100%;
  height: 140px;
  margin-top: 10px;
  border-radius: 12px;
  overflow: hidden;
}

.fireworks-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* AI 专属芯片微渐变发光效果 */
.ai-badge {
  background: linear-gradient(135deg, #7b1fa2 0%, #ba68c8 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 2px 6px rgba(156, 39, 176, 0.35);
  animation: ai-pulse 2.5s infinite;
}

@keyframes ai-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(186, 104, 200, 0.5);
  }
  70% {
    box-shadow: 0 0 0 6px rgba(186, 104, 200, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(186, 104, 200, 0);
  }
}
</style>
