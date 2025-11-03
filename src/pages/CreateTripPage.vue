<template>
  <v-main>
    <v-container fluid>
      <!-- 新增：添加一个按钮，点击后显示对话框 -->
      <v-btn color="purple" @click="showDialog = true">
        打开创建行程对话框
      </v-btn>
      <!-- 原来的对话框组件，通过v-model控制显示 -->
      <CreateTripDialog v-model="showDialog" @trip-created="handleTripCreated" />
    </v-container>
  </v-main>
</template>

<script setup>
  import { ref } from 'vue'
  import CreateTripDialog from '@/components/createTripDialog.vue'

  const showDialog = ref(false) // 控制对话框显示的状态

  // 处理行程创建成功的回调（可选，根据业务需求扩展）
  function handleTripCreated (tripData) {
    console.log('父组件收到行程数据：', tripData)
  // 这里可以做后续逻辑，比如跳转到行程列表页
  }
</script>
