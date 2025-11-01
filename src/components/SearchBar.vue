<template>
  <div class="search-bar-container">
    <!-- 搜索输入框 -->
    <input
      type="text"
      v-model="searchQuery"
      :placeholder="placeholder"
      class="search-input"
      @keyup.enter="handleSearch"
      @input="handleInput"
    />
    
    <!-- 功能按钮区 -->
    <div class="search-actions">
      <!-- 清除按钮（输入不为空时显示） -->
      <button 
        class="action-btn clear-btn" 
        @click="handleClear" 
        v-if="searchQuery"
        aria-label="清除搜索内容"
      >
        <svg-icon type="mdi" :path="mdiClose" size="20" />
      </button>
      
      <!-- 搜索按钮 -->
      <button 
        class="action-btn search-btn" 
        @click="handleSearch"
        aria-label="执行搜索"
      >
        <svg-icon type="mdi" :path="mdiMagnify" size="22" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SvgIcon from '@jamescoyle/vue-icon'; // 导入Vue Icon组件
import { mdiClose, mdiMagnify } from '@mdi/js'; // 导入MDI图标路径

// 响应式搜索值
const searchQuery = ref('');

// 组件参数（支持自定义占位符）
const props = defineProps({
  placeholder: {
    type: String,
    default: '搜索目的地、行程模板...'
  }
});

// 组件事件（向父组件传递搜索结果）
const emit = defineEmits(['search', 'input']);

// 处理搜索逻辑
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    emit('search', searchQuery.value.trim());
  }
};

// 清除输入内容
const handleClear = () => {
  searchQuery.value = '';
  emit('input', ''); // 通知父组件内容已清空
};

// 实时输入反馈
const handleInput = () => {
  emit('input', searchQuery.value);
};
</script>

<style scoped>
.search-bar-container {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 500px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 6px 12px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 0;
  font-size: 14px;
  color: #333;
}

.search-input::placeholder {
  color: #999;
  font-size: 13px;
}

.search-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  padding: 4px;
  color: #666;
  transition: color 0.2s;
}

.action-btn:hover {
  color: #7437f0; /* 主题色（可根据项目调整） */
}

.clear-btn {
  color: #999;
}

/* 确保SVG图标垂直居中 */
svg {
  vertical-align: middle;
}
</style>