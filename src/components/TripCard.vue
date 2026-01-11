<template>
  <v-card
    class="trip-card w-100 mx-auto my-4"
    :loading="loading"
    max-width="600"
    @click="handleCardClick" 
    style="cursor: pointer;" 
  >
    <template #progress>
      <v-progress-linear
        color="deep-purple"
        height="10"
        indeterminate
      />
    </template>
    <!-- 适配父组件/后端的图片字段 -->
    <v-img height="250" :src="trip.image || trip.imageUrl || defaultImage" />
    <!-- 适配行程名称字段 -->
    <v-card-title>{{ trip.trip_name || trip.name || '默认行程' }}</v-card-title>
    <v-card-text>
      <v-row
        align="center"
        class="mx-0"
      >
        <v-rating
          color="amber"
          dense
          half-increments
          readonly
          size="14"
          :value="trip.rating || 4.0"
        />
        <div class="grey--text ms-4">
           {{ trip.rating || 4.0 }} (413)
        </div>
      </v-row>
      <div class="my-4 text-subtitle-1">
        {{ trip.type || '$ • 未知类型' }}
      </div>
      <div>{{ trip.desc || '暂无描述' }}</div>
    </v-card-text>
    <v-divider class="mx-4" />
    <v-card-title>Tonight's availability</v-card-title>
    <v-card-text>
      <v-chip-group
        v-model="selection"
        active-class="deep-purple accent-4 white--text"
        column
      >
        <v-chip>5:30PM</v-chip>
        <v-chip>7:30PM</v-chip>
        <v-chip>8:00PM</v-chip>
        <v-chip>9:00PM</v-chip>
      </v-chip-group>
    </v-card-text>
    <v-card-actions>
      <v-btn
        color="deep-purple lighten-2"
        text
        @click.stop="reserve" 
      >
        Reserve
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'TripCard',
  props: {
    trip: {
      type: Object,
      required: true,
      default: () => ({
        // 兼容父组件传递的 id/name
        id: '',
        name: '',
        // 兼容后端返回的字段
        trip_id: '',
        trip_name: '默认行程',
        image: '',
        imageUrl: 'https://cdn.vuetifyjs.com/images/cards/default.jpg',
        rating: 4.0,
        type: '$ • 未知类型',
        desc: '暂无描述'
      })
    }
  },
  data: () => ({
    loading: false,
    selection: 1,
    defaultImage: 'https://cdn.vuetifyjs.com/images/cards/default.jpg'
  }),
  methods: {
    // 核心：修改点击跳转逻辑，兼容多字段格式
    handleCardClick() {
      // 优先取后端字段，没有则取父组件映射的字段
      const tripId = this.trip.trip_id || this.trip.id;
      const tripName = this.trip.trip_name || this.trip.name;

      // 校验必要参数，避免无效跳转
      if (!tripId || !tripName) {
        console.warn('行程ID或名称缺失，无法跳转:', this.trip);
        return;
      }

      // 路由跳转（确保路由配置中存在 name: 'Trip' 的路由）
      this.$router.push({
        name: 'Trip',
        params: { tripId: tripId },
        query: { tripName: encodeURIComponent(tripName) } // 编码处理特殊字符
      });
    },
    reserve() {
      this.loading = true;
      setTimeout(() => (this.loading = false), 2000);
    }
  }
};
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
</style>