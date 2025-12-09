<template>
  <div class="app-container">
    <div class="background" />
    <div class="background1" />
    <div class="background2" />
    <div class="content">
      <v-container style="margin-top: 12%">
        <v-row class="d-flex justify-center align-center fill-height">
          <v-col cols="12" lg="4" md="6">
            <v-card class="login-card">
              <img alt="Logo" class="logo" src="@/assets/logo2.svg">
              <v-card-text>
                <v-form ref="form" v-model="valid" lazy-validation>
                  <!-- 修改部分开始：将 Email 改为 Username -->
                  <v-text-field
                    v-model="username"
                    :error-messages="usernameErrors"
                    label="Username"
                    required
                    :rules="usernameRules"
                    type="text"
                  />
                  <!-- 修改部分结束 -->

                  <v-text-field
                    v-model="password"
                    :error-messages="passwordErrors"
                    label="Password"
                    required
                    :rules="passwordRules"
                    type="password"
                  />
                </v-form>
                <v-btn style="margin-bottom: 10px" type="submit" @click="login">Login</v-btn>
                <v-spacer />
                <v-btn color="primary" href="/forgot-password" style="margin-bottom: 10px">
                  Forgot Password?
                </v-btn>
                <v-spacer />
                <v-btn color="primary" href="/register">
                  Register
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'

  export default {
    data: () => ({
      valid: true,
      username: '',
      usernameRules: [
        v => !!v || 'Username is required',
      ],
      password: '',
      passwordRules: [
        v => !!v || 'Password is required',
      ],
    }),
    computed: {
      usernameErrors () {
        return this.usernameRules
          .filter(rule => !rule(this.username))
          .map(rule => rule(this.username))
      },
      passwordErrors () {
        return this.passwordRules
          .filter(rule => !rule(this.password))
          .map(rule => rule(this.password))
      },
    },
    methods: {
      async login () {
        // 表单验证
        if (!this.$refs.form.validate()) {
          alert('请检查输入是否正确')
          return
        }

        try {
          const formData = new FormData()
          formData.append('username', this.username)
          formData.append('password', this.password)

          const res = await axios.post('/api/login', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          })

          // 后端返回: { message, username, user_id, admin_id }
          console.log(res.data)
          alert(res.data.message || '登录成功')

          const user = {
            username: res.data.username,
            user_id: res.data.user_id,
            admin_id: res.data.admin_id, // 普通用户为 null
          }

          // 存到 localStorage
          localStorage.setItem('user', JSON.stringify(user))

          // 根据 admin_id 决定跳转页面
          // 注意这里判断 null/undefined 均视为“普通用户”
          if (user.admin_id !== null && user.admin_id !== undefined) {
            // 管理员
            this.$router.push('/admin')
          } else {
            // 普通用户
            this.$router.push('/home')
          }
        } catch (error) {
          if (error.response && error.response.status === 401) {
            alert('登录失败：用户名或密码错误')
          } else {
            console.error(error)
            alert('登录失败，请检查网络或服务器')
          }
        }
      },
    },
  }
</script>

<style scoped>
/* 背景部分保持不变 */
html, body {
  height: 100%;
  margin: 0;
}

.app-container {
  position: relative;
  height: 100%;
}
.background,.background1 {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  overflow: hidden;
}
.background{
  content: '';
  position: absolute;
  top: 0%;
  left: 0%;
  right: 0%;
  bottom: 0%;
  background-image: url('@/assets/ex2.png');
  background-position: center center;
  background-size: 30vh 30vh;
  background-repeat: repeat;
  animation: moveBackground 30s linear infinite;
  filter: blur(2px);
}
.background1{
  content: '';
  position: absolute;
  top: 0%;
  left: 0%;
  right: 0%;
  bottom: 0%;
  background-image: url('@/assets/ex3.png');
  background-position: center center;
  background-size: 30vh 30vh;
  background-repeat: repeat;
  animation: moveBackground 20s linear infinite;
  filter: blur(0px);
  opacity: 0.4;
}
@keyframes moveBackground {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 100% 100%;
  }
}

.background2 {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(138, 43, 226, 0.8),rgba(70, 130, 180, 0.8));
  z-index: 2;
}

.content {
  position: relative;
  z-index: 3;
}

.login-card {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  padding: 30px;
  border-radius: 15px;
  background-color: rgba(255, 255, 255, 0.8);
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.logo {
  position: relative;
  width: 120px;
  height: auto;
  left: 32%;
}

.v-row {
  height: 100vh;
}

.v-btn {
  width: 100%;
  margin-bottom: 10px;
}
</style>
