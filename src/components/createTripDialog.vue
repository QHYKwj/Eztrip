<template>
  <v-dialog
    max-width="600px"
    :model-value="modelValue"
    persistent
    transition="dialog-bottom-transition"
    @update:model-value="handleClose"
  >
    <v-card class="rounded-lg">
      <!-- 1. 美化的头部：使用 Toolbar 添加背景色和标题 -->
      <v-toolbar color="#6A4AC5" density="compact">
        <v-icon class="ml-4" icon="mdi-airplane-takeoff" />
        <v-toolbar-title class="text-subtitle-1 font-weight-bold">
          开启新旅程
        </v-toolbar-title>
        <v-spacer />
        <v-btn icon @click="handleClose">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card-text class="pa-6">
        <v-form ref="formRef" v-model="isFormValid" lazy-validation>
          <!-- 行程名称 -->
          <v-text-field
            v-model="form.tripName"
            class="mb-2"
            color="deep-purple"
            density="comfortable"
            label="行程名称"
            placeholder="例如：暑期日本七日游"
            prepend-inner-icon="mdi-rename-box"
            :rules="rules.required"
            variant="outlined"
          />

          <!-- 目的地 -->
          <v-text-field
            v-model="form.destination"
            class="mb-2"
            color="deep-purple"
            density="comfortable"
            label="目的地"
            placeholder="例如：东京"
            prepend-inner-icon="mdi-map-marker"
            :rules="rules.required"
            variant="outlined"
          />

          <!-- 行程类型选择 -->
          <div class="text-subtitle-2 text-grey-darken-1 mb-2">行程类型</div>
          <v-chip-group
            v-model="form.class"
            column
            :rules="rules.required"
            selected-class="text-deep-purple-accent-3"
          >
            <v-chip filter value="1" variant="outlined">⛱️ 休闲</v-chip>
            <v-chip filter value="2" variant="outlined">🍜 美食</v-chip>
            <v-chip filter value="3" variant="outlined">💼 冒险</v-chip>
            <v-chip filter value="4" variant="outlined">👨‍👩‍👧‍👦 文化</v-chip>
          </v-chip-group>

          <!-- 日期选择区域：并排显示 -->
          <v-row>
            <v-col cols="12" md="6">
              <v-menu
                v-model="menuStart"
                :close-on-content-click="false"
                min-width="auto"
                transition="scale-transition"
              >
                <template #activator="{ props }">
                  <v-text-field
                    v-bind="props"
                    color="deep-purple"
                    density="comfortable"
                    label="开始日期"
                    :model-value="formattedStartDate"
                    prepend-inner-icon="mdi-calendar-start"
                    readonly
                    :rules="rules.required"
                    variant="outlined"
                  />
                </template>
                <v-date-picker
                  v-model="form.startDate"
                  color="deep-purple"
                  @update:model-value="menuStart = false"
                />
              </v-menu>
            </v-col>

            <v-col cols="12" md="6">
              <v-menu
                v-model="menuEnd"
                :close-on-content-click="false"
                min-width="auto"
                transition="scale-transition"
              >
                <template #activator="{ props }">
                  <v-text-field
                    v-bind="props"
                    color="deep-purple"
                    density="comfortable"
                    label="结束日期"
                    :model-value="formattedEndDate"
                    prepend-inner-icon="mdi-calendar-end"
                    readonly
                    :rules="[...rules.required, rules.dateOrder]"
                    variant="outlined"
                  />
                </template>
                <v-date-picker
                  v-model="form.endDate"
                  color="deep-purple"
                  :min="form.startDate"
                  @update:model-value="menuEnd = false"
                />
              </v-menu>
            </v-col>
          </v-row>

          <!-- 备注/描述 -->
          <v-textarea
            v-model="form.description"
            class="mt-4"
            color="deep-purple"
            density="comfortable"
            label="备注信息 (可选)"
            placeholder="写下你的旅行计划..."
            prepend-inner-icon="mdi-text"
            rows="3"
            variant="outlined"
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="text"
          @click="handleClose"
        >
          取消
        </v-btn>
        <v-btn
          color="#903DFE"
          :loading="loading"
          prepend-icon="mdi-check"
          variant="elevated"
          @click="saveTrip"
        >
          创建行程
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
  import axios from 'axios'
  import { computed, defineEmits, defineProps, reactive, ref } from 'vue'

  // --- Props & Emits ---
  const props = defineProps({
    modelValue: Boolean,
  })
  const emit = defineEmits(['update:modelValue', 'tripCreated'])

  // --- State ---
  const formRef = ref(null)
  const isFormValid = ref(false)
  const loading = ref(false)
  const menuStart = ref(false)
  const menuEnd = ref(false)

  // 使用 reactive 聚合表单数据，管理更方便
  const form = reactive({
    tripName: '',
    destination: '',
    startDate: null,
    endDate: null,
    tags: [],
    description: '',
    class: null, // 新增的行程类型
  })

  // --- 校验规则 ---
  const rules = {
    required: [v => !!v || '此项为必填项'],
    dateOrder: v => {
      if (!form.startDate || !form.endDate) return true
      return new Date(form.endDate) >= new Date(form.startDate) || '结束日期不能早于开始日期'
    },
  }

  // --- Computed: 格式化日期显示 ---
  function formatDate (date) {
    if (!date) return ''
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const formattedStartDate = computed(() => formatDate(form.startDate))
  const formattedEndDate = computed(() => formatDate(form.endDate))

  // --- Methods ---

  // 关闭并重置
  function handleClose () {
    emit('update:modelValue', false)
    setTimeout(() => {
      resetForm() // 延迟重置，避免弹窗关闭时内容突然清空的视觉闪烁
    }, 300)
  }

  // 重置表单
  function resetForm () {
    form.tripName = ''
    form.destination = ''
    form.startDate = null
    form.endDate = null
    form.tags = []
    form.description = ''
    form.class = null
    if (formRef.value) formRef.value.resetValidation()
  }

  // 提交保存
  // 在 script setup 中

  async function saveTrip() {
    // 1. 触发表单校验
    const { valid } = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    try {
      // 2. 获取用户数据
      const user = JSON.parse(sessionStorage.getItem('user'))
      // 如果没有登录，为了测试方便，暂时允许不传 id (后端默认了1)，或者提示登录
      const userId = user && user.user_id ? user.user_id : 1

      // 3. 构造符合后端 Pydantic 模型 (TripCreate) 的 JSON 对象
      const payload = {
        tripName: form.tripName,       // 对应后端: tripName
        destination: form.destination, // 对应后端: destination
        startDate: formatDate(form.startDate),
        endDate: formatDate(form.endDate),
        description: form.description || '', // 对应后端: description
        // 关键：后端是根据 tags 列表来判断 class 的
        // 假设 form.tags 是 ['休闲', '美食'] 这样的数组
        tags: form.tags || [],
        owner_user_id: userId
      }

      // 4. 发送 JSON 请求 (axios 默认就是 json，不需要 new FormData)
      const response = await axios.post('/api/trip/create', payload)

      console.log('创建成功:', response.data)

      // 5. 成功回调
      // 注意：把后端返回的 trip_id 带上，方便父组件刷新或跳转
      emit('tripCreated', {
        ...form,
        id: response.data.trip_id
      })

      loading.value = false
      handleClose()

    } catch (error) {
      console.error('创建行程失败', error)
      alert('创建失败，请检查网络或后端日志')
      loading.value = false
    }
  }

</script>

<style scoped>
/* 微调输入框样式，使其更清爽 */
.v-text-field :deep(.v-field__input) {
  padding-top: 10px;
  padding-bottom: 10px;
}
</style>
