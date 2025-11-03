<!-- components/createTripDialog.vue -->
<template>
  <!-- v-dialog 使用 v-model 的语法糖是 :model-value 和 @update:model-value -->
  <v-dialog
    max-width="500px"
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-card>
      <v-card-title class="text-h5">创建行程</v-card-title>
      <v-card-text>
        <v-form>
          <v-text-field v-model="tripName" label="行程名称" />
          <v-text-field v-model="destination" label="目的地" />
          <v-date-picker v-model="startDate" label="开始日期" />
          <v-date-picker v-model="endDate" label="结束日期" />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer /> <!-- 将按钮推到右边 -->
        <v-btn text @click="closeDialog">取消</v-btn>
        <v-btn color="purple" dark @click="saveTrip">创建</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
  import { defineEmits, defineProps, ref } from 'vue'

  // 定义 props，modelValue 用于 v-model 绑定
  const props = defineProps({
    modelValue: Boolean, // 接收父组件传入的布尔值，控制对话框显示
  })

  // 定义事件，update:modelValue 用于 v-model 的更新，tripCreated 用于通知父组件行程已创建
  const emit = defineEmits(['update:modelValue', 'tripCreated'])

  const tripName = ref('')
  const destination = ref('')
  const startDate = ref(null)
  const endDate = ref(null)

  // 关闭对话框并重置表单
  function closeDialog () {
    emit('update:modelValue', false) // 通知父组件关闭对话框
    resetForm()
  }

  // 保存行程数据
  function saveTrip () {
    // 这里可以添加您的数据验证和后端API调用逻辑
    console.log('行程信息:', {
      tripName: tripName.value,
      destination: destination.value,
      startDate: startDate.value,
      endDate: endDate.value,
    })

    // 假设数据已成功处理，通知父组件并关闭对话框
    emit('tripCreated', {
      tripName: tripName.value,
      destination: destination.value,
      startDate: startDate.value,
      endDate: endDate.value,
    })
    closeDialog()
  }

  // 重置表单字段
  function resetForm () {
    tripName.value = ''
    destination.value = ''
    startDate.value = null
    endDate.value = null
  }
</script>
