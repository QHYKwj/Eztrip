<template>
  <v-card class="filter-card" elevation="0">
    <v-card-text class="filter-content">
      <v-row dense :gutter="16">
        <!-- 时间筛选 (保持下拉) -->
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedTime"
            :items="timeOptions"
            :label="selectedTime ? '' : '选择时间'"
            placeholder="不限时间"
            clearable
            solo
            hide-details
            density="compact"
            @update:modelValue="handleFilterChange"
          />
        </v-col>

        <!-- 地点筛选 (改为输入框) -->
        <v-col cols="12" md="4">
          <v-text-field
            v-model="selectedLocation"
            label="输入目的地"
            placeholder="例如：成都"
            clearable
            solo
            hide-details
            density="compact"
            prepend-inner-icon="mdi-map-marker-outline"
            @update:modelValue="handleFilterChange"
          />
        </v-col>

        <!-- 风格筛选 (保持下拉) -->
        <v-col cols="12" md="4">
          <v-select
            v-model="selectedStyle"
            :items="styleOptions"
            :label="selectedStyle ? '' : '选择风格'"
            placeholder="不限风格"
            clearable
            solo
            hide-details
            density="compact"
            @update:modelValue="handleFilterChange"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue';

const timeOptions = ['1天', '2天', '3天', '4-7天', '7天以上'];
// 注意：locationOptions 已移除，因为改为输入型
const styleOptions = ['休闲', '美食', '冒险', '文化'];

const selectedTime = ref(null);
const selectedLocation = ref(''); // 改为空字符串默认值
const selectedStyle = ref(null);

const timeValueMap = { '1天': '1', '2天': '2', '3天': '3', '4-7天': '4-7', '7天以上': '7+' };
// locationValueMap 已移除，直接传字符串
const styleValueMap = { '休闲': 'leisure', '美食': 'food', '冒险': 'adventure', '文化': 'culture' };

const emit = defineEmits(['filter']);

const handleFilterChange = () => {
  // 为了防止输入时频繁触发，你可以考虑在这里加防抖(debounce)，但目前先保持实时响应
  emit('filter', {
    time: selectedTime.value ? timeValueMap[selectedTime.value] : null,
    location: selectedLocation.value || null, // 直接传递用户输入的文字
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

.filter-content {
  font-size: 0.7rem;
  padding: 0;
}

/*
   核心修改：同时选中 v-select 和 v-text-field
   确保输入框和下拉框样式完全一致
*/
:deep(.v-select.solo),
:deep(.v-text-field.solo) {
  .v-input__control {
    min-height: 30px !important; /* 强制统一高度 */
  }

  .v-field__field,
  .v-select__slot,
  .v-input__slot {
    background-color: white !important;
    border-radius: 18px;
    min-height: 30px;
    padding: 0 8px; /* 稍微增加内边距 */
    box-shadow: none !important; /* 去除默认阴影 */
  }

  /* 输入框内文字、占位符 */
  input,
  .v-select__selection,
  .v-field__input {
    font-size: 0.7rem !important;
    min-height: 30px !important;
    padding-top: 0;
    padding-bottom: 0;
    align-items: center;
    display: flex;
  }

  /* 占位符颜色微调 */
  ::placeholder {
    font-size: 0.7rem;
    opacity: 0.6;
  }
}

/* 下拉选项文字 */
:deep(.v-list-item) {
  font-size: 0.7rem !important;
}

/* 图标大小适配 */
:deep(.v-icon) {
  font-size: 16px; /* 调整图标大小以适应小输入框 */
  opacity: 0.6;
}

/* 下拉菜单背景 */
:deep(.v-overlay__content) {
  background-color: white !important;
  border-radius: 8px;
}
</style>
