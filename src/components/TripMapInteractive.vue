<template>
  <div class="map-wrap">
    <div ref="container" class="map-container" @contextmenu.prevent />

    <div class="map-header-tools">
      <div v-if="enableSearch" class="map-search">
        <input
          v-model="keyword"
          class="map-search-input"
          placeholder="搜索并聚焦地点（回车）"
          @keydown.enter="doSearch"
        >
      </div>

      <div v-if="markers && markers.length > 0" class="day-legend">
        <div v-for="d in activeDays" :key="d" class="legend-item">
          <span class="legend-color" :style="{ backgroundColor: getDayColor(d) }" />
          <span>第 {{ d }} 天</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import AMapLoader from '@amap/amap-jsapi-loader'

  export default {
    name: 'TripMapInteractive',
    props: {
      lng: { type: Number, default: 113.2644 },
      lat: { type: Number, default: 23.1291 },
      zoom: { type: Number, default: 12 },
      pickable: { type: Boolean, default: false }, // 详情页展示默认关闭手动打点
      enableSearch: { type: Boolean, default: true },
      markers: { type: Array, default: () => [] },
    },
    emits: ['update:center', 'pick', 'marker-moved', 'map-right-click'],
    data () {
      return {
        AMap: null,
        map: null,
        mainMarker: null,
        keyword: '',
        placeSearch: null,
        renderedMarkers: [],
        renderedLines: [],
        // 多天行程专属配色方案
        dayColors: [
          '#2196F3', // D1 蓝色
          '#9C27B0', // D2 紫色
          '#FF9800', // D3 橙色
          '#4CAF50', // D4 绿色
          '#F44336', // D5 红色
          '#00BCD4', // D6 青色
          '#E91E63', // D7 粉色
        ],
      }
    },
    computed: {
      activeDays () {
        const days = new Set(this.markers.map(m => m.day || 1))
        return Array.from(days).sort((a, b) => a - b)
      },
    },
    watch: {
      markers: {
        deep: true,
        handler () {
          this.renderMarkersAndRoutes()
        },
      },
    },
    async mounted () {
      await this.initMap()
    },
    beforeUnmount () {
      if (this.map) this.map.destroy()
    },
    methods: {
      getDayColor (dayIndex = 1) {
        const idx = (dayIndex - 1) % this.dayColors.length
        return this.dayColors[idx] || '#742DD8'
      },

      async initMap () {
        window._AMapSecurityConfig = { securityJsCode: '3d64bb5617949c03d8e7dac21479d2da' }

        this.AMap = await AMapLoader.load({
          key: 'd185585a4be1f46dc467ccb305c00357',
          version: '2.0',
          plugins: ['AMap.ToolBar', 'AMap.Scale', 'AMap.PlaceSearch'],
        })

        this.map = new this.AMap.Map(this.$refs.container, {
          viewMode: '2D',
          zoom: this.zoom,
          center: [this.lng, this.lat],
          resizeEnable: true,
          doubleClickZoom: false,
        })

        this.map.addControl(new this.AMap.ToolBar())
        this.map.addControl(new this.AMap.Scale())

        // 🌟 封装拾取坐标函数，同时支持鼠标右键(rightclick)和双击左键(dblclick)
        const handleMapClickPick = (e) => {
          const p = e.lnglat
          console.log('📍 地图拾取坐标:', p.lng, p.lat)
          this.$emit('map-right-click', { lng: p.lng, lat: p.lat })
        }

        this.map.on('rightclick', handleMapClickPick)
        this.map.on('dblclick', handleMapClickPick)

        // 如果允许用户单独点击选点（在编辑或新建模式时）
        if (this.pickable) {
          this.mainMarker = new this.AMap.Marker({
            position: [this.lng, this.lat],
            draggable: true,
          })
          this.map.add(this.mainMarker)

          this.map.on('click', e => {
            const p = e.lnglat
            this.mainMarker.setPosition([p.lng, p.lat])
            this.$emit('pick', { lng: p.lng, lat: p.lat })
          })
        }

        this.placeSearch = new this.AMap.PlaceSearch({ pageSize: 5, citylimit: false })
        this.renderMarkersAndRoutes()
      },

      doSearch () {
        const kw = (this.keyword || '').trim()
        if (!kw || !this.placeSearch) return

        this.placeSearch.search(kw, (status, result) => {
          if (status !== 'complete' || !result?.poiList?.pois?.length) return
          const poi = result.poiList.pois[0]
          const lng = poi.location.lng
          const lat = poi.location.lat
          this.map.setCenter([lng, lat])
          this.map.setZoom(15)
          if (this.mainMarker) this.mainMarker.setPosition([lng, lat])
          this.$emit('pick', { lng, lat, name: poi.name })
        })
      },

      // 🌟 核心：按天渲染不同颜色标记点 + 方向连线
      renderMarkersAndRoutes () {
        if (!this.map || !this.AMap) return

        // 1. 清除旧的点和折线
        this.map.remove(this.renderedMarkers)
        this.map.remove(this.renderedLines)
        this.renderedMarkers = []
        this.renderedLines = []

        if (!this.markers || this.markers.length === 0) return

        // 2. 将数据按第几天 (day) 分组
        const dayGroups = {}
        for (const m of this.markers) {
          const d = m.day || 1
          if (!dayGroups[d]) dayGroups[d] = []
          dayGroups[d].push(m)
        }

        // 3. 遍历每一天分别画点和路线
        for (const dayStr of Object.keys(dayGroups)) {
          const dayIndex = Number(dayStr)
          const color = this.getDayColor(dayIndex)
          const items = dayGroups[dayStr]

          const pathCoords = []

          for (const m of items) {
            const pos = [Number(m.lng), Number(m.lat)]
            pathCoords.push(pos)

            // 创建漂亮的定制化 HTML 标记
            const markerHtml = `
              <div class="custom-trip-marker" style="background-color: ${color}; border-color: white;">
                <span class="marker-badge">D${m.day || 1}</span>
                <span class="marker-seq">${m.seq || ''}</span>
                <div class="marker-tooltip">${m.name || ''}</div>
              </div>
            `

            const marker = new this.AMap.Marker({
              position: pos,
              content: markerHtml,
              offset: new this.AMap.Pixel(-18, -36), // 将点位锚定在中心底端
              zIndex: 100 + (m.seq || 1),
            })

            this.map.add(marker)
            this.renderedMarkers.push(marker)
          }

          // 4. 当这一天有 2 个及以上景点时，画方向连接折线
          if (pathCoords.length >= 2) {
            const polyline = new this.AMap.Polyline({
              path: pathCoords,
              showDir: true, // 显示白色路线行进小箭头
              strokeColor: color, // 使用对应天的配色
              strokeWeight: 6, // 线粗
              strokeOpacity: 0.85, // 透明度
              lineJoin: 'round', // 圆滑转角
            })
            this.map.add(polyline)
            this.renderedLines.push(polyline)
          }
        }

        // 5. 自动缩放视野，把所有行程点一览无遗地展示在中间
        this.$nextTick(() => {
          if (this.renderedMarkers.length > 0) {
            this.map.setFitView(this.renderedMarkers, false, [50, 50, 50, 50])
          }
        })
      },
    },
  }
</script>

<style scoped>
.map-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 450px;
  border-radius: 12px;
  overflow: hidden;
}
.map-container {
  width: 100%;
  height: 100%;
}
.map-header-tools {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  z-index: 10;
}
.map-search {
  pointer-events: auto;
}
.map-search-input {
  width: 100%;
  max-width: 320px;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.1);
  outline: none;
  background: white;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  font-size: 13px;
}
.day-legend {
  pointer-events: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  padding: 6px 12px;
  border-radius: 8px;
  width: fit-content;
  box-shadow: 0 2px 6px rgba(0,0,0,0.08);
  font-size: 12px;
  font-weight: 600;
  color: #444;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}
.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

/* 🌟 自定义地图标记样式 */
:deep(.custom-trip-marker) {
  position: relative;
  display: flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
  font-size: 12px;
  border: 2px solid white;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
  cursor: pointer;
  transition: transform 0.2s ease;
}
:deep(.custom-trip-marker:hover) {
  transform: scale(1.15);
  z-index: 999;
}
:deep(.marker-badge) {
  font-size: 10px;
  opacity: 0.9;
  margin-right: 3px;
}
:deep(.marker-seq) {
  font-size: 13px;
}
/* 鼠标悬浮时展示景点完整名称气泡 */
:deep(.marker-tooltip) {
  display: none;
  position: absolute;
  bottom: 115%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  font-size: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}
:deep(.custom-trip-marker:hover .marker-tooltip) {
  display: block;
}
</style>
