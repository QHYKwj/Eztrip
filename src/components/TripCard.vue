<template>
  <v-card
    class="trip-card w-100 mx-auto my-4"
    :loading="loading"
    max-width="600"
  >
    <template #progress>
      <v-progress-linear
        color="deep-purple"
        height="10"
        indeterminate
      />
    </template>

    <v-img height="250" :src="trip.imageUrl" />

    <v-card-title>{{ trip.name }}</v-card-title>

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
          :value="trip.rating"
        />

        <div class="grey--text ms-4">
           {{ trip.rating }} (413)
        </div>
      </v-row>

      <div class="my-4 text-subtitle-1">
        {{ trip.type }}
      </div>

      <div>{{ trip.desc }}</div>
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
        @click="reserve"
      >
        Reserve
      </v-btn>
    </v-card-actions>
  </v-card>
</template>


<script>
export default {
  props: {
    trip: {
      type: Object,
      required: true,
      default: () => ({
        imageUrl: 'https://cdn.vuetifyjs.com/images/cards/default.jpg',
        name: '默认行程',
        rating: 4.0,
        type: '$ • 未知类型',
        desc: '暂无描述'
      })
    }
  },
  data: () => ({
    loading: false,
    selection: 1
  }),
  methods: {
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
  height: 100%; /* 确保卡片高度一致 */
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease; /* 平滑过渡效果 */
}

/* 鼠标悬浮效果优化 */
.trip-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(157, 113, 164, 0.37);
  border-color: #d8b4fe;
}

/* 卡片内容区域自动填充空间 */
:deep(.v-card-text) {
  flex-grow: 1;
}

/* 调整图片样式 */
:deep(.v-img) {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  object-fit: cover; /* 图片自适应裁剪 */
}
</style>