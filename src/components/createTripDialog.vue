<template>
  <v-dialog
    max-width="700px"
    :model-value="modelValue"
    persistent
    transition="dialog-bottom-transition"
    @update:model-value="handleClose"
  >
    <v-card class="rounded-lg">
      <!-- 头部：使用 Toolbar 添加背景色和标题 -->
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

      <v-card-text class="pa-6" style="max-height: 75vh; overflow-y: auto;">
        <v-form ref="formRef" v-model="isFormValid" lazy-validation>

          <div class="text-subtitle-2 font-weight-bold text-primary mb-3">基本信息</div>

          <v-row>
            <!-- 行程名称 -->
            <v-col class="py-1" cols="12" md="6">
              <v-text-field
                v-model="form.tripName"
                color="deep-purple"
                density="comfortable"
                label="行程名称"
                placeholder="例如：暑期日本七日游"
                prepend-inner-icon="mdi-rename-box"
                :rules="rules.required"
                variant="outlined"
              />
            </v-col>

            <!-- 目的地 -->
            <v-col class="py-1" cols="12" md="6">
              <v-text-field
                v-model="form.destination"
                color="deep-purple"
                density="comfortable"
                label="目的地"
                placeholder="例如：东京"
                prepend-inner-icon="mdi-map-marker"
                :rules="rules.required"
                variant="outlined"
              />
            </v-col>

            <!-- 日期选择区域 -->
            <v-col class="py-1" cols="12" md="6">
              <v-menu v-model="menuStart" :close-on-content-click="false" min-width="auto" transition="scale-transition">
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
                <v-date-picker v-model="form.startDate" color="deep-purple" @update:model-value="menuStart = false" />
              </v-menu>
            </v-col>

            <v-col class="py-1" cols="12" md="6">
              <v-menu v-model="menuEnd" :close-on-content-click="false" min-width="auto" transition="scale-transition">
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
                <v-date-picker v-model="form.endDate" color="deep-purple" :min="form.startDate" @update:model-value="menuEnd = false" />
              </v-menu>
            </v-col>

            <!-- 行程类型选择 -->
            <v-col class="py-1" cols="12">
              <div class="text-subtitle-2 text-grey-darken-1 mb-1">行程类型</div>
              <v-chip-group v-model="form.class" column :rules="rules.required" selected-class="text-deep-purple-accent-3">
                <v-chip filter value="1" variant="outlined">⛱️ 休闲</v-chip>
                <v-chip filter value="2" variant="outlined">🍜 美食</v-chip>
                <v-chip filter value="3" variant="outlined">💼 冒险</v-chip>
                <v-chip filter value="4" variant="outlined">👨‍👩‍👧‍👦 文化</v-chip>
              </v-chip-group>
            </v-col>
          </v-row>

          <v-divider class="my-4" />
          <div class="text-subtitle-2 font-weight-bold text-primary mb-3">行程规划详情 (选填)</div>

          <!-- 🌟 结构化锦囊表单区 🌟 -->
          <v-row>
            <v-col class="py-1" cols="12">
              <v-textarea
                v-model="form.remarks.overview"
                auto-grow
                color="deep-purple"
                density="comfortable"
                label="行程概述"
                placeholder="简单记录一下这次旅行的目的或期待..."
                prepend-inner-icon="mdi-flag-variant-outline"
                rows="2"
                variant="outlined"
              />
            </v-col>

            <v-col class="py-1" cols="12" md="6">
              <v-text-field
                v-model="form.remarks.best_time"
                color="deep-purple"
                density="comfortable"
                label="最佳出行时间"
                placeholder="例如：10月-11月秋高气爽"
                prepend-inner-icon="mdi-weather-partly-cloudy"
                variant="outlined"
              />
            </v-col>

            <v-col class="py-1" cols="12" md="6">
              <v-text-field
                v-model="form.remarks.budget"
                color="deep-purple"
                density="comfortable"
                label="预估预算"
                placeholder="例如：约5000元"
                prepend-inner-icon="mdi-currency-cny"
                variant="outlined"
              />
            </v-col>

            <v-col class="py-1" cols="12">
              <v-textarea
                v-model="form.remarks.accommodation"
                auto-grow
                color="deep-purple"
                density="comfortable"
                label="住宿建议"
                placeholder="你想住在哪个区域？"
                prepend-inner-icon="mdi-bed"
                rows="1"
                variant="outlined"
              />
            </v-col>

            <v-col class="py-1" cols="12">
              <v-textarea
                v-model="form.remarks.food"
                auto-grow
                color="deep-purple"
                density="comfortable"
                label="美食推荐"
                placeholder="一定要去打卡的餐厅或小吃"
                prepend-inner-icon="mdi-silverware-variant"
                rows="1"
                variant="outlined"
              />
            </v-col>

            <!-- 数组输入框：避坑与行李 -->
            <v-col class="py-1" cols="12">
              <v-combobox
                v-model="form.remarks.tips"
                chips
                clearable
                closable-chips
                color="deep-purple"
                density="comfortable"
                label="避坑提示 (输入后按回车添加)"
                multiple
                prepend-inner-icon="mdi-alert-circle-outline"
                variant="outlined"
              />
            </v-col>

            <v-col class="py-1" cols="12">
              <v-combobox
                v-model="form.remarks.packing"
                chips
                clearable
                closable-chips
                color="deep-purple"
                density="comfortable"
                label="行李清单 (输入后按回车添加)"
                multiple
                prepend-inner-icon="mdi-bag-checked"
                variant="outlined"
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey-darken-1" variant="text" @click="handleClose">取消</v-btn>
        <v-btn
          color="#903DFE"
          :loading="loading"
          prepend-icon="mdi-check"
          variant="elevated"
          @click="saveTrip"
        >创建行程</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
  import axios from 'axios'
  import { computed, defineEmits, defineProps, reactive, ref } from 'vue'

  const props = defineProps({
    modelValue: Boolean,
  })
  const emit = defineEmits(['update:modelValue', 'tripCreated'])

  const formRef = ref(null)
  const isFormValid = ref(false)
  const loading = ref(false)
  const menuStart = ref(false)
  const menuEnd = ref(false)

  // 🌟 将 description 升级为结构化的 remarks 对象
  const form = reactive({
    tripName: '',
    destination: '',
    startDate: null,
    endDate: null,
    class: null,
    remarks: {
      overview: '',
      best_time: '',
      budget: '',
      accommodation: '',
      food: '',
      tips: [],
      packing: [],
    },
  })

  const rules = {
    required: [v => !!v || '此项为必填项'],
    dateOrder: v => {
      if (!form.startDate || !form.endDate) return true
      return new Date(form.endDate) >= new Date(form.startDate) || '结束日期不能早于开始日期'
    },
  }

  function formatDate (date) {
    if (!date) return ''
    const d = new Date(date)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const formattedStartDate = computed(() => formatDate(form.startDate))
  const formattedEndDate = computed(() => formatDate(form.endDate))

  function handleClose () {
    emit('update:modelValue', false)
    setTimeout(() => {
      resetForm()
    }, 300)
  }

  function resetForm () {
    form.tripName = ''
    form.destination = ''
    form.startDate = null
    form.endDate = null
    form.class = null
    // 🌟 重置结构化对象
    form.remarks = {
      overview: '',
      best_time: '',
      budget: '',
      accommodation: '',
      food: '',
      tips: [],
      packing: [],
    }
    if (formRef.value) formRef.value.resetValidation()
  }

  async function saveTrip () {
    const { valid } = await formRef.value.validate()
    if (!valid) return

    loading.value = true

    try {
      const user = JSON.parse(sessionStorage.getItem('user') || 'null')
      const userId = user && user.user_id ? user.user_id : null

      if (!userId) {
        alert('请先登录再创建行程')
        loading.value = false
        return
      }

      const payload = {
        owner_user_id: userId,
        title: form.tripName,
        destination: form.destination,
        start_date: formatDate(form.startDate),
        end_date: formatDate(form.endDate),
        class_type: Number(form.class),
        is_public: 0,
        remarks: form.remarks, // ✅ 直接将填好的对象传给后端
      }

      const response = await axios.post('/api/user/trips/create', payload) // 确保路由匹配你的后端

      emit('tripCreated', {
        ...payload,
        trip_id: response.data.trip_id,
      })

      handleClose()
    } catch (error) {
      console.error('创建行程失败', error)
      alert('创建失败，请检查网络或后端日志')
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
.v-text-field :deep(.v-field__input),
.v-textarea :deep(.v-field__input) {
  padding-top: 8px;
  padding-bottom: 8px;
}
</style>
