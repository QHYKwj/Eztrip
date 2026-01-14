<template>
  <v-card class="rounded-lg border w-100" elevation="0">
    <v-card-title class="d-flex align-center justify-space-between bg-grey-lighten-4 py-3">
      <span class="text-subtitle-1 font-weight-bold">详细行程计划</span>
      <v-chip size="small" variant="outlined">共 {{ totalDays }} 天</v-chip>
    </v-card-title>

    <v-card-text class="pa-4">
      <v-skeleton-loader v-if="loading" type="article" />

      <v-alert v-else-if="error" type="error" variant="tonal">
        {{ error }}
      </v-alert>

      <div v-else class="plan-table">
        <div
          v-for="day in days"
          :key="day.day_index"
          class="plan-row"
        >
          <div class="day-col">
            <div class="day-title">第 {{ day.day_index }} 天</div>
            <div class="day-date">{{ day.plan_date || '-' }}</div>
          </div>

          <div class="tags-col">
            <div class="tags-line">
              <template v-if="day.items && day.items.length > 0">
                <template v-for="(it, idx) in day.items" :key="it.id">
                  <v-chip
                    class="mr-2"
                    color="deep-purple"
                    size="small"
                    variant="tonal"
                  >
                    {{ it.title }}
                    <v-btn
                      v-if="editable"
                      class="ml-1"
                      icon="mdi-close"
                      size="x-small"
                      variant="text"
                      @click.stop="removeItem(it.id)"
                    />
                  </v-chip>

                  <v-icon
                    v-if="idx !== day.items.length - 1"
                    class="mr-2"
                    color="grey"
                    size="18"
                  >
                    mdi-arrow-right
                  </v-icon>
                </template>
              </template>

              <div v-else class="empty-hint">（还没安排）</div>
            </div>

            <div v-if="editable" class="actions mt-2">
              <v-btn
                prepend-icon="mdi-plus"
                size="small"
                variant="outlined"
                @click="openAdd(day.day_index)"
              >
                添加地点/Tag
              </v-btn>
            </div>
          </div>
        </div>
      </div>

      <v-snackbar v-model="snack.show" :color="snack.color" timeout="2200">
        {{ snack.text }}
      </v-snackbar>

      <!-- 添加弹窗 -->
      <v-dialog v-model="addDialog" max-width="420">
        <v-card>
          <v-card-title>添加 Tag</v-card-title>
          <v-card-text>
            <div class="text-caption text-grey mb-2">第 {{ addDayIndex }} 天</div>
            <v-text-field
              v-model="addTitle"
              density="comfortable"
              label="地点/Tag 名称"
              placeholder="例如：广州塔"
              variant="outlined"
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn variant="text" @click="addDialog=false">取消</v-btn>
            <v-btn color="primary" :loading="saving" @click="confirmAdd">确定</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card-text>
  </v-card>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'TripPlanBoard',
    props: {
      userId: { type: [Number, String], required: true },
      tripId: { type: [Number, String], required: true },
      editable: { type: Boolean, default: false }, // 只有 owner 才 true
    },
    data () {
      return {
        loading: false,
        saving: false,
        error: null,

        totalDays: 0,
        days: [],

        snack: { show: false, text: '', color: 'success' },

        addDialog: false,
        addDayIndex: 1,
        addTitle: '',
      }
    },
    watch: {
      tripId: {
        immediate: true,
        handler () {
          this.loadPlan()
        },
      },
    },
    methods: {
      showSnack (text, color = 'success') {
        this.snack.text = text
        this.snack.color = color
        this.snack.show = true
      },

      async loadPlan () {
        if (!this.tripId || !this.userId) return
        this.loading = true
        this.error = null
        try {
          const res = await axios.get('/api/trip_plan/get', {
            params: { user_id: this.userId, trip_id: this.tripId },
          })
          this.totalDays = res.data?.total_days || 0
          this.days = res.data?.days || []
        } catch (error) {
          console.error(error)
          this.error = '加载行程计划失败'
        } finally {
          this.loading = false
        }
      },

      openAdd (dayIndex) {
        this.addDayIndex = dayIndex
        this.addTitle = ''
        this.addDialog = true
      },

      async confirmAdd () {
        const title = (this.addTitle || '').trim()
        if (!title) {
          this.showSnack('请输入 Tag 名称', 'error')
          return
        }

        this.saving = true
        try {
          await axios.post('/api/trip_plan/item/add', {
            user_id: this.userId,
            trip_id: Number(this.tripId),
            day_index: Number(this.addDayIndex),
            title,
          })
          this.showSnack('添加成功')
          this.addDialog = false
          await this.loadPlan()
        } catch (error) {
          console.error(error)
          const msg = error.response?.data?.detail || '添加失败'
          this.showSnack(msg, 'error')
        } finally {
          this.saving = false
        }
      },

      async removeItem (itemId) {
        this.saving = true
        try {
          await axios.post('/api/trip_plan/item/delete', {
            user_id: this.userId,
            trip_id: Number(this.tripId),
            item_id: Number(itemId),
          })
          this.showSnack('删除成功')
          await this.loadPlan()
        } catch (error) {
          console.error(error)
          const msg = error.response?.data?.detail || '删除失败'
          this.showSnack(msg, 'error')
        } finally {
          this.saving = false
        }
      },
    },
  }
</script>

<style scoped>
.plan-table {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 14px;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 12px;
  background: #fff;
}

.day-col {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.day-title {
  font-weight: 700;
}

.day-date {
  color: #777;
  font-size: 12px;
  margin-top: 4px;
}

.tags-col {
  display: flex;
  flex-direction: column;
}

.tags-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.empty-hint {
  color: #999;
  font-size: 13px;
}
</style>
