<template>
  <div class="app-container">
    <div class="background" />
    <div class="background1" />
    <div class="background2" />
    <div class="content">
      <v-container style="margin-top: 10%">
        <v-row class="d-flex justify-center align-center fill-height">
          <v-col cols="12" lg="4" md="6">
            <v-card class="login-card">
              <img alt="Logo" class="logo" src="@/assets/logo2.svg">
              <v-card-title>Register</v-card-title>

              <v-card-text>
                <!-- 关键：submit.prevent，阻止原生提交刷新 -->
                <v-form ref="formRef" v-model="valid" lazy-validation @submit.prevent="register">
                  <v-text-field
                    v-model="name"
                    :counter="10"
                    :error-messages="nameErrors"
                    label="Name"
                    required
                    :rules="nameRules"
                    type="text"
                  />
                  <v-text-field
                    v-model="email"
                    :error-messages="emailErrors"
                    label="Email"
                    required
                    :rules="emailRules"
                    type="email"
                  />
                  <v-text-field
                    v-model="password"
                    :error-messages="passwordErrors"
                    label="Password"
                    required
                    :rules="passwordRules"
                    type="password"
                  />
                  <v-text-field
                    v-model="password2"
                    :error-messages="password2Errors"
                    label="Confirm Password"
                    required
                    :rules="getPassword2Rules()"
                    type="password"
                  />

                  <!-- 关键：按钮不要 type=submit，避免浏览器默认提交 -->
                  <v-btn
                    style="margin-bottom: 10px"
                    type="button"
                    :loading="loading"
                    :disabled="loading"
                    @click="register"
                  >
                    Register
                  </v-btn>

                  <v-spacer />
                  Already have an account?
                  <v-btn color="primary" href="/login" style="margin-left: 10px">
                    Login
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <!-- ✅ 弹窗提示（成功/错误） -->
      <v-snackbar v-model="snackbar.show" :timeout="2000">
        {{ snackbar.text }}
        <template v-slot:actions>
          <v-btn text @click="snackbar.show = false">Close</v-btn>
        </template>
      </v-snackbar>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Register',
  data: () => ({
    valid: true,
    loading: false,

    name: '',
    email: '',
    password: '',
    password2: '',

    nameRules: [
      v => !!v || 'Name is required',
      v => /^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$/.test(v) || 'Name must contain only letters',
    ],
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
    ],
    passwordRules: [
      v => !!v || 'Password is required',
    ],

    snackbar: {
      show: false,
      text: '',
    },
  }),

  computed: {
    nameErrors() {
      return this.nameRules
        .filter(rule => rule(this.name) !== true)
        .map(rule => rule(this.name))
    },
    emailErrors() {
      return this.emailRules
        .filter(rule => rule(this.email) !== true)
        .map(rule => rule(this.email))
    },
    passwordErrors() {
      return this.passwordRules
        .filter(rule => rule(this.password) !== true)
        .map(rule => rule(this.password))
    },
    password2Errors() {
      const rules = this.getPassword2Rules()
      return rules
        .filter(rule => rule(this.password2) !== true)
        .map(rule => rule(this.password2))
    }
  },

  methods: {
    showMsg(text) {
      this.snackbar.text = text
      this.snackbar.show = true
    },

    getPassword2Rules() {
      return [
        v => !!v || 'Confirm Password is required',
        v => v === this.password || 'Passwords must match'
      ]
    },

    async register() {
      // ✅ 兼容 Vuetify 2 / 3：validate() 有的返回 boolean，有的返回 { valid }
      const res = await this.$refs.formRef.validate()
      const isValid = typeof res === 'boolean' ? res : res.valid

      if (!isValid) {
        this.showMsg('请检查输入内容')
        return
      }

      this.loading = true
      try {
        const params = new URLSearchParams()
        params.append('username', this.name.trim())
        params.append('email', this.email.trim())
        params.append('password', this.password)
        params.append('confirm_password', this.password2)

        const resp = await axios.post('/api/user/register', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })

        // ✅ 成功提示
        this.showMsg(resp?.data?.message || '注册成功！2秒后跳转登录')
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)

      } catch (error) {
        // ✅ 错误提示：根据状态码 + 后端 detail 精确显示
        const status = error?.response?.status
        const detail = error?.response?.data?.detail || ''

        if (status === 400) {
          if (detail.includes('Username already existed')) {
            this.showMsg('注册失败：用户名已被使用')
          } else if (detail.includes('Email is already used')) {
            this.showMsg('注册失败：邮箱已被使用')
          } else if (detail.includes('different')) {
            this.showMsg('注册失败：两次密码不一致')
          } else {
            this.showMsg(`注册失败：${detail || '请求参数错误'}`)
          }
        } else if (status === 422) {
          // FastAPI 表单字段缺失/类型不对，经常是 422，不是 400
          this.showMsg('注册失败：请求参数缺失或格式不对（422）')
        } else if (!error?.response) {
          this.showMsg('注册失败：无法连接服务器（检查后端/代理/跨域）')
        } else {
          this.showMsg(`注册失败：${detail || '服务器错误'}`)
        }

      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
/* 你原来的样式保持不动即可（省略也行） */
html, body { height: 100%; margin: 0; }
.app-container { position: relative; height: 100%; }
.background,.background1 { position: absolute; inset: 0; z-index: 1; overflow: hidden; }
.background{ background-image: url('@/assets/ex2.png'); background-size: 30vh 30vh; background-repeat: repeat; animation: moveBackground 30s linear infinite; filter: blur(2px); }
.background1{ background-image: url('@/assets/ex3.png'); background-size: 30vh 30vh; background-repeat: repeat; animation: moveBackground 20s linear infinite; opacity: 0.4; }
@keyframes moveBackground { 0% { background-position: 0% 0%; } 100% { background-position: 100% 100%; } }
.background2 { position: absolute; inset: 0; background: linear-gradient(to bottom, rgba(138, 43, 226, 0.8),rgba(70, 130, 180, 0.8)); z-index: 2; }
.content { position: relative; z-index: 3; }
.login-card { max-width: 400px; margin: 0 auto; padding: 30px; border-radius: 15px; background-color: rgba(255, 255, 255, 0.8); }
.logo { width: 120px; position: relative; left: 32%; }
.v-row { height: 100vh; }
.v-btn { width: 100%; margin-bottom: 10px; }
</style>
