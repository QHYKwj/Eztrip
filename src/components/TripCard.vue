<template>
  <v-card
    class="trip-card w-100 mx-auto my-4"
    :loading="loading"
    style="cursor: pointer;"
    @click="handleCardClick"
  >
    <template #progress>
      <v-progress-linear
        color="deep-purple"
        height="10"
        indeterminate
      />
    </template>
    <v-img height="250" :src="renderTrip.image || renderTrip.imageUrl || defaultImage" />
    <v-card-title class="d-flex align-center justify-space-between">
      <span>{{ renderTrip.trip_name || renderTrip.name || '默认行程' }}</span>
    </v-card-title>
    <v-card-text>
      <div class="d-flex align-center">
        <v-icon
          class="mr-1"
          color="red"
          :icon="favorited ? 'mdi-heart' : 'mdi-heart-outline'"
        />
        <span class="text-body-2">{{ favoriteCount }}</span>
      </div>
      <div class="my-2 text-subtitle-1">
        {{ typeText }}
      </div>
      <div class="my-2 text-subtitle-1">目的地：{{ renderTrip.destination }}</div>
      <div class="my-2 text-subtitle-1">行程时间：{{ renderTrip.days }}天</div>
    </v-card-text>
    <v-divider class="mx-4" />
    <v-card-actions class="px-4 py-2 d-flex justify-space-between">
      <v-btn
        color="deep-purple lighten-2"
        :loading="favoriting"
        variant="text"
        @click.stop="favoriteTrip"
      >
        一键收藏
      </v-btn>

      <v-btn
        color="primary"
        variant="tonal"
        size="small"
        prepend-icon="mdi-source-fork"
        :loading="forking"
        @click.stop="handleForkTrip"
      >
        一键复刻路线
      </v-btn>
    </v-card-actions>
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="2200">
      {{ snack.text }}
    </v-snackbar>
    <div v-show="fireworks.show" class="fireworks-layer" @click.stop>
      <canvas ref="fireCanvas" class="fireworks-canvas" />
    </div>
  </v-card>
</template>

<script>
import axios from 'axios'

export default {
  name: 'TripCard',
  props: {
    // 原有完整trip对象，所有列表页面继续使用，保留required不改动
    trip: {
      type: Object,
      required: true,
      default: () => ({
        id: '',
        name: '',
        destination: '',
        trip_id: '',
        trip_name: '默认行程',
        image: '',
        imageUrl: 'https://picsum.photos/1920/1071?random.jpg',
        desc: '暂无描述',
        class: null,
        style: '',
        days: '',
      }),
    },
    // 新增AI对话页面专用独立参数，非必填，不影响原有页面
    aiTripId: {
      type: Number,
      default: null,
    },
    aiTitle: {
      type: String,
      default: '',
    },
    aiDestination: {
      type: String,
      default: '',
    },
    aiDays: {
      type: Number,
      default: null,
    },
  },
  data: () => ({
    loading: false,
    defaultImage: 'https://picsum.photos/1920/1083?random.jpg',
    favoriteCount: 0,
    favoriting: false,
    favorited: false,
    forking: false, // ✅ 新增：控制复刻按钮的加载状态
    favoriteIds: new Set(),
    favoriteIdsLoaded: false,
    snack: { show: false, text: '', color: 'success' },
    fireworks: {
      show: false,
      rafId: null,
      timer: null,
    },
  }),
  computed: {
    // 核心兼容层：区分AI传参/正常列表传参，不修改原trip变量
    renderTrip () {
      if (this.aiTripId || this.aiTitle || this.aiDestination || this.aiDays) {
        return {
          trip_id: this.aiTripId,
          id: this.aiTripId,
          trip_name: this.aiTitle || '未命名行程',
          name: this.aiTitle || '未命名行程',
          destination: this.aiDestination || '未知目的地',
          days: this.aiDays || 1,
          imageUrl: this.defaultImage,
          image: '',
          class: null,
          style: '',
        }
      }
      return this.trip
    },
    typeText () {
      const cls = Number(this.renderTrip.class)
      const map = {
        1: '⛱️ 休闲',
        2: '🍜 美食',
        3: '💼 冒险',
        4: '👨‍👩‍👧‍👦 文化',
      }
      if (map[cls]) return map[cls]
      const s = this.renderTrip.style || this.renderTrip.type || ''
      if (s.includes('休闲')) return '⛱️ 休闲'
      if (s.includes('美食')) return '🍜 美食'
      if (s.includes('冒险')) return '💼 冒险'
      if (s.includes('文化')) return '👨‍👩‍👧‍👦 文化'
      return '🏷️ 未知类型'
    },
  },
  watch: {
    trip: {
      deep: true,
      immediate: true,
      async handler () {
        await this.fetchUserFavoriteIds()
        await this.initFavoritedState()
        await this.fetchFavoriteCount()
      },
    },
    aiTripId: {
      handler () {
        this.initFavoritedState()
        this.fetchFavoriteCount()
      },
    },
  },
  async mounted () {
    await this.fetchUserFavoriteIds()
    await this.initFavoritedState()
    await this.fetchFavoriteCount()
  },
  beforeUnmount () {
    this.stopFireworks()
  },
  methods: {
    handleCardClick () {
      const tripId = this.renderTrip.trip_id || this.renderTrip.id
      const tripName = this.renderTrip.trip_name || this.renderTrip.name
      if (!tripId || !tripName) {
        console.warn('行程ID或名称缺失，无法跳转:', this.renderTrip)
        return
      }
      this.$router.push({
        name: 'Trip',
        params: { tripId: tripId },
        query: { tripName: encodeURIComponent(tripName) },
      })
    },
    async initFavoritedState () {
      const tripId = Number(this.renderTrip.trip_id || this.renderTrip.id)
      if (!tripId) return
      if (typeof this.renderTrip.is_collected === 'boolean') {
        this.favorited = this.renderTrip.is_collected
        return
      }
      if (!this.favoriteIdsLoaded) {
        await this.fetchUserFavoriteIds()
      }
      this.favorited = this.favoriteIds.has(tripId)
    },
    async fetchFavoriteCount () {
      const tripId = this.renderTrip.trip_id || this.renderTrip.id
      if (!tripId) return
      try {
        const res = await axios.get('/api/trip/favorite-count', {
          params: { trip_id: tripId },
        })
        this.favoriteCount = Number(res.data?.count ?? 0)
      } catch (error) {
        console.error('获取收藏人数失败:', error)
      }
    },
    getUserId () {
      const ss = sessionStorage.getItem('user')
      const ls = localStorage.getItem('user')
      const raw = ss || ls
      if (!raw) return null
      try {
        const u = JSON.parse(raw)
        return u.user_id || u.id || null
      } catch {
        return null
      }
    },
    showSnack (text, color = 'success') {
      this.snack.text = text
      this.snack.color = color
      this.snack.show = true
    },

    // ✅ 新增：处理复刻操作
    async handleForkTrip () {
      const userId = this.getUserId()
      const tripId = this.renderTrip.trip_id || this.renderTrip.id

      if (!userId) {
        this.showSnack('请先登录再复刻行程', 'error')
        return
      }
      if (!tripId) {
        this.showSnack('行程ID缺失，无法复刻', 'error')
        return
      }

      // 校验是否是自己创建的行程
      if (this.renderTrip.owner_user_id && Number(this.renderTrip.owner_user_id) === Number(userId)) {
        this.showSnack('这是您自己创建的行程，无需复刻哦！', 'info')
        return
      }

      this.forking = true
      try {
        const res = await axios.post(`/api/user/trips/${tripId}/fork`, null, {
          params: { user_id: userId },
        })

        this.showSnack('🎉 路线复刻成功！已加入您的行程列表', 'success')

        // 如果后端返回了新建行程的ID，延时后自动前往详情页方便用户调整
        if (res.data?.new_trip_id) {
          setTimeout(() => {
            this.$router.push({
              name: 'Trip',
              params: { tripId: res.data.new_trip_id },
            })
          }, 1200)
        }
      } catch (error) {
        console.error('复刻失败:', error)
        const detail = error.response?.data?.detail || error.response?.data?.message || '复刻失败，请稍后重试'
        this.showSnack(detail, 'error')
      } finally {
        this.forking = false
      }
    },

    async favoriteTrip () {
      const userId = this.getUserId()
      const tripId = this.renderTrip.trip_id || this.renderTrip.id
      if (!userId) {
        this.showSnack('请先登录再收藏', 'error')
        return
      }
      if (!tripId) {
        this.showSnack('行程ID缺失，无法收藏', 'error')
        return
      }
      if (this.favorited) {
        this.showSnack('你已经收藏过这个行程啦 ❤️', 'info')
        return
      }
      this.favoriting = true
      try {
        const res = await axios.post('/api/collect/favorite/add', {
          user_id: userId,
          trip_id: tripId,
        })
        if (res.data?.code === 200) {
          this.favorited = true
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
    async fetchUserFavoriteIds () {
      const userId = this.getUserId()
      if (!userId) {
        this.favoriteIds = new Set()
        this.favoriteIdsLoaded = true
        return
      }
      const cacheKey = `favorite_trip_ids_${userId}`
      const ttlMs = 60 * 1000
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
      } catch {}
      try {
        const res = await axios.post('/api/collect/favorite/list', { user_id: userId })
        if (res.data?.code === 200 && Array.isArray(res.data?.data?.trip_ids)) {
          const ids = res.data.data.trip_ids.map(Number)
          this.favoriteIds = new Set(ids)
          sessionStorage.setItem(cacheKey, JSON.stringify({
            ts: Date.now(),
            trip_ids: ids
          }))
        } else {
          this.favoriteIds = new Set()
        }
        this.favoriteIdsLoaded = true
      } catch (error) {
        console.error('获取用户收藏列表失败:', error)
        this.favoriteIds = new Set()
        this.favoriteIdsLoaded = true
      }
    },
  },
}
</script>

<style scoped>
.trip-card {
  border: 1px solid #f7e1ff;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}
.trip-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(157, 113, 164, 0.37);
  border-color: #d8b4fe;
}
:deep(.v-card-text) {
  flex-grow: 1;
}
:deep(.v-img) {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  object-fit: cover;
}
.fireworks-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.fireworks-canvas {
  width: 100%;
  height: 100%;
}
</style>
