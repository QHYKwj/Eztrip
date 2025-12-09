<template>
  <div class="profile-container">
    <!-- 顶部导航栏 -->
    <v-app-bar
      elevation="0"
      style="background-color: #F3F2FD; border-bottom: 1px solid #DBD1EF"
    >
      <v-app-bar-nav-icon style="color: #675096" @click="$router.go(-1)" />
      <v-toolbar-title style="color: #675096; font-weight: 600">个人信息</v-toolbar-title>
    </v-app-bar>

    <v-container class="profile-content" fluid>
      <!-- 加个加载 & 错误提示 -->
      <v-row v-if="loading">
        <v-col cols="12">
          <v-skeleton-loader type="article" />
        </v-col>
      </v-row>

      <v-row v-else-if="error">
        <v-col cols="12">
          <v-alert dense type="error">{{ error }}</v-alert>
        </v-col>
      </v-row>

      <template v-else>
        <!-- 1. 头像与基础信息区 -->
        <div class="profile-header">
          <div class="avatar-border">
            <v-img
              class="rounded-circle"
              height="120"
              :src="profile.avatar || defaultAvatar"
              width="120"
            />
          </div>

          <div class="profile-basic">
            <h2 class="profile-name" style="color: #444">
              {{ profile.username || '未命名用户' }}
            </h2>
            <p class="profile-role" style="color: #675096">
              {{ roleText }}
            </p>
          </div>

          <div class="profile-btn-group">
            <!-- 编辑 / 保存 按钮 -->
            <v-btn
              rounded
              size="small"
              :loading="saving"
              :disabled="saving"
              style="background-color: #742DD8; color: white; margin-right: 8px"
              @click="handleEditOrSave"
            >
              <v-icon left>
                {{ isEditing ? 'mdi-content-save' : 'mdi-pencil' }}
              </v-icon>
              {{ isEditing ? '保存' : '编辑信息' }}
            </v-btn>

            <v-btn
              rounded
              size="small"
              style="background-color: #675096; color: white; border: 1px solid #DBD1EF"
              @click="logout"
            >
              <v-icon left>mdi-logout</v-icon>注销
            </v-btn>
          </div>
        </div>

        <!-- 2. 基本信息卡片（改成表单） -->
        <v-card
          class="profile-card"
          outlined
          style="border-color: #DBD1EF; margin-top: 24px"
        >
          <v-card-title style="color: #675096; font-weight: 500">
            <v-icon left>mdi-account-details</v-icon>基本信息
          </v-card-title>
          <v-card-text>
            <v-form ref="form" v-model="formValid">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.phone_num"
                    :disabled="!isEditing"
                    :rules="phoneRules"
                    label="手机号"
                    variant="outlined"
                    density="comfortable"
                    clearable
                    placeholder="请输入手机号"
                  />
                </v-col>

                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.email"
                    :disabled="!isEditing"
                    :rules="emailRules"
                    label="邮箱"
                    variant="outlined"
                    density="comfortable"
                    clearable
                    placeholder="请输入邮箱"
                  />
                </v-col>

                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.birthday"
                    :disabled="!isEditing"
                    label="生日"
                    variant="outlined"
                    density="comfortable"
                    type="date"
                    hint="YYYY-MM-DD"
                    persistent-hint
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- 3. 行程统计卡片 -->
        <v-card
          class="profile-card"
          outlined
          style="border-color: #DBD1EF; margin-top: 16px"
        >
          <v-card-title style="color: #675096; font-weight: 500">
            <v-icon left>mdi-map-location-dot</v-icon>行程统计
          </v-card-title>
          <v-card-text>
            <div class="stats-grid">
              <div class="stat-item">
                <p class="stat-value" style="color: #742DD8; font-size: 24px; font-weight: 600">
                  {{ stats.completed_trips }}
                </p>
                <p class="stat-label" style="color: #444">已完成行程</p>
              </div>
              <div class="stat-item">
                <p class="stat-value" style="color: #742DD8; font-size: 24px; font-weight: 600">
                  {{ stats.upcoming_trips }}
                </p>
                <p class="stat-label" style="color: #444">待出发行程</p>
              </div>
              <div class="stat-item">
                <p class="stat-value" style="color: #742DD8; font-size: 24px; font-weight: 600">
                  {{ stats.collected_trips }}
                </p>
                <p class="stat-label" style="color: #444">收藏行程</p>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </template>
    </v-container>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ProfilePage',
  data () {
    return {
      loading: false,
      saving: false,
      error: null,
      defaultAvatar: 'https://randomuser.me/api/portraits/men/85.jpg',

      profile: {
        user_id: null,
        username: '',
        email: '',
        phone_num: '',
        birthday: '',
        avatar: '',
        admin_id: null,
      },

      // 表单数据（用来编辑）
      form: {
        phone_num: '',
        email: '',
        birthday: '',
      },

      stats: {
        completed_trips: 0,
        upcoming_trips: 0,
        collected_trips: 0,
      },

      isEditing: false,
      formValid: true,

      // 表单验证规则
      phoneRules: [
        v => !v || /^\d{11}$/.test(v) || '手机号必须为 11 位数字',
      ],
      emailRules: [
        v => !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || '邮箱格式不正确',
      ],
    }
  },
  computed: {
    roleText () {
      if (this.profile.admin_id !== null && this.profile.admin_id !== undefined) {
        return '管理员'
      }
      return '普通用户'
    },
  },
  created () {
    this.loadProfile()
  },
  methods: {
    getUserFromStorage () {
      const str = localStorage.getItem('user')
      if (!str) return null
      try {
        return JSON.parse(str)
      } catch {
        return null
      }
    },
    async loadProfile () {
      const user = this.getUserFromStorage()
      if (!user || !user.user_id) {
        this.error = '未登录，请先登录'
        return
      }

      this.loading = true
      this.error = null
      try {
        const res = await axios.get(`/api/profile/${user.user_id}`)
        const data = res.data

        this.profile = {
          user_id: data.user_id,
          username: data.username,
          email: data.email,
          phone_num: data.phone_num,
          birthday: data.birthday,
          avatar: data.avatar,
          admin_id: data.admin_id,
        }

        // 初始化表单值
        this.form.phone_num = this.profile.phone_num || ''
        this.form.email = this.profile.email || ''
        this.form.birthday = this.profile.birthday || ''

        this.stats = {
          completed_trips: data.stats.completed_trips,
          upcoming_trips: data.stats.upcoming_trips,
          collected_trips: data.stats.collected_trips,
        }
      } catch (error) {
        console.error(error)
        this.error = '加载个人信息失败'
      } finally {
        this.loading = false
      }
    },
    async handleEditOrSave () {
      // 1. 当前是“查看模式”，点击切换到“编辑模式”
      if (!this.isEditing) {
        this.isEditing = true
        // 确保表单里的值和 profile 同步
        this.form.phone_num = this.profile.phone_num || ''
        this.form.email = this.profile.email || ''
        this.form.birthday = this.profile.birthday || ''
        return
      }

      // 2. 当前是“编辑模式”，点击则尝试保存
      if (!this.$refs.form) return

      const ok = await this.$refs.form.validate()
      if (!ok) {
        // Vuetify 3 的 validate 返回 true/false
        // 这里简单 alert 一下
        alert('请检查表单是否填写正确')
        return
      }

      // 调用后端更新
      await this.saveProfile()
    },
    async saveProfile () {
      if (!this.profile.user_id) {
        alert('用户信息缺失，请重新登录')
        return
      }

      this.saving = true
      try {
        const formData = new FormData()
        // 只有有值的才提交（也可以全部提交）
        formData.append('phone_num', this.form.phone_num || '')
        formData.append('email', this.form.email || '')
        formData.append('birthday', this.form.birthday || '')

        await axios.put(`/api/profile/${this.profile.user_id}`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })

        // 更新本地 profile 数据
        this.profile.phone_num = this.form.phone_num
        this.profile.email = this.form.email
        this.profile.birthday = this.form.birthday

        this.isEditing = false
        alert('个人信息已保存')
      } catch (error) {
        console.error(error)
        alert('保存失败，请稍后再试')
      } finally {
        this.saving = false
      }
    },
    logout () {
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
  },
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background-color: #FAFAFA;
}

.profile-content {
  padding: 79px 24px 24px;
  max-width: 800px;
  margin: 0 auto;
}

.avatar-border {
  border: 3px solid white;
  border-radius: 50%;
  padding: 3px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.profile-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.profile-basic {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 24px;
  text-align: center;
}

@media (max-width: 600px) {
  .profile-header {
    justify-content: center;
    text-align: center;
  }
  .profile-btn-group {
    flex-direction: column;
    width: 100%;
    max-width: 200px;
  }
  .profile-content {
    padding-top: 60px;
  }
}
</style>
