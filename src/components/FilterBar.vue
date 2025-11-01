<template>
  <v-card class="filter-card" elevation="0">
    <v-card-text class="filter-content">
      <v-row dense :gutter="16">
        <!-- 时间筛选 -->
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedTime"
            :items="timeOptions"
            :label="selectedTime ? '' : '选择时间'"
            placeholder="不限时间"
            clearable
            solo
            @change="handleFilterChange"
          />
        </v-col>

        <!-- 地点筛选 -->
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedLocation"
            :items="locationOptions"
            :label="selectedLocation ? '' : '选择地点'"
            placeholder="不限地点"
            clearable
            solo
            @change="handleFilterChange"
          />
        </v-col>

        <!-- 风格筛选 -->
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedStyle"
            :items="styleOptions"
            :label="selectedStyle ? '' : '选择风格'"
            placeholder="不限风格"
            clearable
            solo
            @change="handleFilterChange"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue';

const timeOptions = ['1天', '2天', '3天', '4-7天', '7天以上'];
const locationOptions = ['国内', '国外'];
const styleOptions = ['休闲', '美食', '冒险', '文化'];

const selectedTime = ref(null);
const selectedLocation = ref(null);
const selectedStyle = ref(null);

const timeValueMap = { '1天': '1', '2天': '2', '3天': '3', '4-7天': '4-7', '7天以上': '7+' };
const locationValueMap = { '国内': 'domestic', '国外': 'abroad' };
const styleValueMap = { '休闲': 'leisure', '美食': 'food', '冒险': 'adventure', '文化': 'culture' };

const emit = defineEmits(['filter']);
const handleFilterChange = () => {
  emit('filter', {
    time: selectedTime.value ? timeValueMap[selectedTime.value] : null,
    location: selectedLocation.value ? locationValueMap[selectedLocation.value] : null,
    style: selectedStyle.value ? styleValueMap[selectedStyle.value] : null
  });
};
</script>

<style scoped>
/* 筛选栏整体 */
.filter-card {
  background-color: white;
  padding: 13px 16px 0;
  margin: 16px 0;
  border-radius: 12px;
  border: 1px solid #dcdcdc; 
}

/* 容器字体基础设置（进一步缩小） */
.filter-content {
  font-size: 0.7rem; /* 设置为0.7rem以适应小字体，原来是0.2rem，过小，适当调整 */
  padding: 0;
}

/* 输入框容器样式 */
:deep(.v-select.solo) {
  .v-select__slot {
    background-color: white !important; 
    border-radius: 18px;
    min-height: 30px; /* 轻微缩小高度，配合小字体 */
  }

  /* 输入框内文字（选中项/占位符） */
  .v-select__selection,
  .v-select__placeholder {
    font-size: 0.7rem !important; /* 输入框文字缩小到0.7rem */
    line-height: 1.2; /* 调整行高，避免文字溢出 */
  }
}

/* 下拉选项文字：同步缩小 */
:deep(.v-list-item) {
  font-size: 0.7rem !important; /* 下拉选项文字缩小 */
}

/* 清除按钮（×）适配小尺寸 */
:deep(.v-select__clear) {
  height: 24px;
  width: 24px;
}

/* 调整下拉菜单的背景色和边框 */
:deep(.v-select__menu) {
  background-color: white !important;
  border-radius: 8px; /* 可以设置为圆角，使菜单和输入框匹配 */
}

</style>