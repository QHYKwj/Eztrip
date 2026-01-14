<template>
  <div class="map-wrap">
    <div ref="container" class="map-container" />

    <!-- 可选：简单搜索（输入关键字后回车） -->
    <div v-if="enableSearch" class="map-search">
      <input
        v-model="keyword"
        class="map-search-input"
        placeholder="搜索地点（回车）"
        @keydown.enter="doSearch"
      >
    </div>
  </div>
</template>

<script>
  import AMapLoader from '@amap/amap-jsapi-loader'

  export default {
    name: 'TripMapInteractive',
    props: {
      // 初始中心点
      lng: { type: Number, default: 113.2644 }, // 广州大概经度
      lat: { type: Number, default: 23.1291 }, // 广州大概纬度
      zoom: { type: Number, default: 12 },

      // 是否允许在地图上点选打点
      pickable: { type: Boolean, default: true },

      // 是否显示搜索框（可选）
      enableSearch: { type: Boolean, default: true },

      // 如果你希望根据“tag/行程点”渲染多个 marker，可以传这个
      // [{ id, name, lng, lat }]
      markers: { type: Array, default: () => [] },
    },
    emits: ['update:center', 'pick', 'marker-moved'],
    data () {
      return {
        AMap: null,
        map: null,
        mainMarker: null,
        keyword: '',
        placeSearch: null,
        renderedMarkers: new Map(),
      }
    },
    watch: {
      // 外部 markers 变了就重绘
      markers: {
        deep: true,
        handler () {
          this.renderMarkers()
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
      async initMap () {
        // ✅ JSAPI 2.0 通常需要配置安全密钥（securityJsCode）
        // 你如果没用到，也可以先不配；但很多项目需要
        window._AMapSecurityConfig = { securityJsCode: '3d64bb5617949c03d8e7dac21479d2da' }

        this.AMap = await AMapLoader.load({
          key: 'd185585a4be1f46dc467ccb305c00357', // 建议放到 .env 里
          version: '2.0',
          plugins: [
            'AMap.ToolBar',
            'AMap.Scale',
            'AMap.PlaceSearch',
          ],
        })

        this.map = new this.AMap.Map(this.$refs.container, {
          viewMode: '2D',
          zoom: this.zoom,
          center: [this.lng, this.lat],
          resizeEnable: true,
        })

        // 控件：缩放/比例尺
        this.map.addControl(new this.AMap.ToolBar())
        this.map.addControl(new this.AMap.Scale())

        // 监听：地图拖动结束，把新的中心点回传
        this.map.on('dragend', () => {
          const c = this.map.getCenter()
          this.$emit('update:center', { lng: c.lng, lat: c.lat })
        })

        // ✅ 主 marker（点击地图放一个点；并允许拖动这个点）
        this.mainMarker = new this.AMap.Marker({
          position: [this.lng, this.lat],
          draggable: true,
        })
        this.map.add(this.mainMarker)

        this.mainMarker.on('dragend', e => {
          const p = e.lnglat
          this.$emit('marker-moved', { lng: p.lng, lat: p.lat })
        })

        // 点击地图：把主 marker 放到点击位置（=“鼠标标点”）
        if (this.pickable) {
          this.map.on('click', e => {
            const p = e.lnglat
            this.mainMarker.setPosition([p.lng, p.lat])
            this.$emit('pick', { lng: p.lng, lat: p.lat })
          })
        }

        // 搜索服务
        this.placeSearch = new this.AMap.PlaceSearch({
          pageSize: 5,
          citylimit: false,
        })

        // 初次渲染外部 markers
        this.renderMarkers()
      },

      // 可选：搜索关键字 -> 地图移动到第一个结果
      doSearch () {
        const kw = (this.keyword || '').trim()
        if (!kw || !this.placeSearch) return

        this.placeSearch.search(kw, (status, result) => {
          if (status !== 'complete' || !result?.poiList?.pois?.length) return
          const poi = result.poiList.pois[0]
          const lng = poi.location.lng
          const lat = poi.location.lat
          this.map.setCenter([lng, lat])
          this.map.setZoom(14)

          // 同时把主 marker 移过去
          if (this.mainMarker) this.mainMarker.setPosition([lng, lat])
          this.$emit('pick', { lng, lat, name: poi.name })
        })
      },

      // 根据 props.markers 渲染多个点（比如你的 tag 自动标点）
      renderMarkers () {
        if (!this.map || !this.AMap) return

        const nextIds = new Set(this.markers.map(m => String(m.id)))

        // 删除不存在的
        for (const [id, marker] of this.renderedMarkers.entries()) {
          if (!nextIds.has(id)) {
            this.map.remove(marker)
            this.renderedMarkers.delete(id)
          }
        }

        // 新增/更新
        for (const m of this.markers) {
          const id = String(m.id)
          const pos = [Number(m.lng), Number(m.lat)]
          if (this.renderedMarkers.has(id)) {
            this.renderedMarkers.get(id).setPosition(pos)
          } else {
            const mk = new this.AMap.Marker({
              position: pos,
              title: m.name || '',
              anchor: 'bottom-center',
            })
            this.map.add(mk)
            this.renderedMarkers.set(id, mk)
          }
        }
      },
    },
  }
</script>

<style scoped>
.map-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 400px;
  border-radius: 12px;
  overflow: hidden;
}
.map-container {
  width: 100%;
  height: 100%;
}
.map-search {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  pointer-events: none;
}
.map-search-input {
  width: 100%;
  max-width: 420px;
  pointer-events: auto;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.12);
  outline: none;
  background: white;
}
</style>
