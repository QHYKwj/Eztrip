<template>
  <v-card
    class="trip-card w-100 mx-auto my-4"
    :loading="loading"
    max-width="600"
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

    <!-- 图片 -->
    <v-img height="250" :src="trip.image || trip.imageUrl || defaultImage" />

    <!-- 标题 + 收藏 -->
    <v-card-title class="d-flex align-center justify-space-between">
      <span>{{ trip.trip_name || trip.name || '默认行程' }}</span>
    </v-card-title>

    <v-card-text>
      <!-- ❤️ 红色爱心 + 收藏人数 -->
      <div class="d-flex align-center">
        <v-icon
          class="mr-1"
          color="red"
          :icon="favorited ? 'mdi-heart' : 'mdi-heart-outline'"
        />
        <span class="text-body-2">{{ favoriteCount }}</span>
      </div>
      <!-- 类型 -->
      <div class="my-2 text-subtitle-1">
        {{ typeText }}
      </div>

      <!-- 描述 -->
      <div class="my-2 text-subtitle-1">目的地：{{ trip.destination }}</div>
      <div class="my-2 text-subtitle-1">行程时间：{{ trip.days }}天</div>
    </v-card-text>

    <v-divider class="mx-4" />

    <v-card-actions>
      <v-spacer />
      <v-btn
        color="deep-purple lighten-2"
        :loading="favoriting"
        variant="text"
        @click.stop="favoriteTrip"
      >
        一键收藏
      </v-btn>
    </v-card-actions>

    <!-- Snackbar 提示 -->
    <v-snackbar v-model="snack.show" :color="snack.color" timeout="2200">
      {{ snack.text }}
    </v-snackbar>

    <!-- 🎆 烟花层（canvas） -->
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
    },
    data: () => ({
      loading: false,

      defaultImage: 'https://picsum.photos/1920/1083?random.jpg',

      favoriteCount: 0,
      favoriting: false,
      favorited: false, // 本地态：收藏成功后置 true（也会尝试从 trip.is_collected 初始化）
      favoriteIds: new Set(), // 当前用户收藏的 trip_id 集合
      favoriteIdsLoaded: false, // 是否加载过
      snack: { show: false, text: '', color: 'success' },

      fireworks: {
        show: false,
        rafId: null,
        timer: null,
      },
    }),

    computed: {
      // ✅ 类型：优先用 trip.class(1-4)，否则用 trip.style/ trip.type 文本兜底
      typeText () {
        const cls = Number(this.trip.class)
        const map = {
          1: '⛱️ 休闲',
          2: '🍜 美食',
          3: '💼 冒险',
          4: '👨‍👩‍👧‍👦 文化',
        }
        if (map[cls]) return map[cls]

        // 兼容你父组件传的 style / type
        const s = this.trip.style || this.trip.type || ''
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
      // ✅ 点击卡片跳转详情
      handleCardClick () {
        const tripId = this.trip.trip_id || this.trip.id
        const tripName = this.trip.trip_name || this.trip.name

        if (!tripId || !tripName) {
          console.warn('行程ID或名称缺失，无法跳转:', this.trip)
          return
        }

        this.$router.push({
          name: 'Trip',
          params: { tripId: tripId },
          query: { tripName: encodeURIComponent(tripName) },
        })
      },
      // ✅ 初始化是否已收藏：优先用后端 list 确认；其次才用 trip.is_collected
      async initFavoritedState () {
        const tripId = Number(this.trip.trip_id || this.trip.id)
        if (!tripId) return

        // 1) 如果列表接口带了 is_collected，直接用（最快）
        if (typeof this.trip.is_collected === 'boolean') {
          this.favorited = this.trip.is_collected
          return
        }

        // 2) 否则：用 /favorite/list 确认（带缓存）
        if (!this.favoriteIdsLoaded) {
          await this.fetchUserFavoriteIds()
        }
        this.favorited = this.favoriteIds.has(tripId)
      },

      // ✅ 获取收藏人数
      async fetchFavoriteCount () {
        const tripId = this.trip.trip_id || this.trip.id
        if (!tripId) return

        try {
          const res = await axios.get('/api/trip/favorite-count', {
            params: { trip_id: tripId },
          })
          // 后端 return {"trip_id":..., "count": ...}
          this.favoriteCount = Number(res.data?.count ?? 0)
        } catch (error) {
          // 不要影响卡片展示
          console.error('获取收藏人数失败:', error)
        }
      },

      // ✅ 从 storage 里拿 user_id（兼容 sessionStorage / localStorage）
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

      // ✅ 一键收藏
      async favoriteTrip () {
        const userId = this.getUserId()
        const tripId = this.trip.trip_id || this.trip.id

        if (!userId) {
          this.showSnack('请先登录再收藏', 'error')
          return
        }
        if (!tripId) {
          this.showSnack('行程ID缺失，无法收藏', 'error')
          return
        }

        // 已收藏，直接提示（前端兜底）
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

          // ✅ 正常收藏成功
          if (res.data?.code === 200) {
            this.favorited = true
            // 同步本地收藏集合 + 缓存（避免下一张卡片还不知道）
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

          // ⚠️ 非 200，但有 message
          this.showSnack(res.data?.message || '收藏失败', 'warning')

        } catch (error) {
          /**
           * ⚠️ 关键：处理 400 = 重复收藏
           */
          if (error.response?.status === 400) {
            this.favorited = true // 强制同步为已收藏态
            const cacheKey = `favorite_trip_ids_${userId}`
            this.favoriteIds.add(Number(tripId))
            sessionStorage.setItem(cacheKey, JSON.stringify({
              ts: Date.now(),
              trip_ids: Array.from(this.favoriteIds),
            }))
            this.showSnack('你已经收藏过这个行程啦 ❤️', 'info')
            await this.fetchFavoriteCount() // 确保数量是最新的
            return
          }

          // ❌ 其它错误（500 / 网络）
          console.error('收藏失败:', error)
          this.showSnack('收藏失败，请稍后再试', 'error')

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

        // 等 DOM 渲染
        this.$nextTick(() => {
          const canvas = this.$refs.fireCanvas
          if (!canvas) return

          const rect = canvas.getBoundingClientRect()
          canvas.width = Math.floor(rect.width)
          canvas.height = Math.floor(rect.height)

          const ctx = canvas.getContext('2d')
          const W = canvas.width
          const H = canvas.height

          // 生成粒子
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
                // 随机亮色（不写固定色值会太淡，所以这里给几个高亮色）
                // 你如果不想指定颜色，我也可以改成纯白粒子
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
              p.vy += 0.06 // 重力
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

            // 继续动画直到粒子死完
            if (particles.some(p => p.life > 0)) {
              this.fireworks.rafId = requestAnimationFrame(step)
            }
          }

          step()

          // 2.2s 后关闭
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
      // ✅ 获取“当前用户收藏的 trip_id 列表”（带 sessionStorage 缓存）
      // 只要在第一个卡片请求成功，后续卡片都能直接复用缓存
      async fetchUserFavoriteIds () {
        const userId = this.getUserId()
        if (!userId) {
          this.favoriteIds = new Set()
          this.favoriteIdsLoaded = true
          return
        }

        const cacheKey = `favorite_trip_ids_${userId}`
        const ttlMs = 60 * 1000 // 60 秒缓存（你也可以调大，比如 5 分钟）

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
          // ignore cache parse error
        }

        // 2) 请求后端
        try {
          const res = await axios.post('/api/collect/favorite/list', { user_id: userId })
          if (res.data?.code === 200 && Array.isArray(res.data?.data?.trip_ids)) {
            const ids = res.data.data.trip_ids.map(Number)
            this.favoriteIds = new Set(ids)
            this.favoriteIdsLoaded = true

            // 写缓存
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

/* 🎆 烟花层 */
.fireworks-layer {
  position: absolute;
  inset: 0;
  pointer-events: none; /* 不阻挡点击 */
}
.fireworks-canvas {
  width: 100%;
  height: 100%;
}
</style>
