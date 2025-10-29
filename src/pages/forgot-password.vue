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
              <v-card-title class="text-center">Reset Password</v-card-title>
              <v-card-text>
                <v-form ref="form" v-model="valid" lazy-validation>
                  <v-text-field
                    v-model="name"
                    :counter="10"
                    :error-messages="nameErrors"
                    label="Name"
                    required
                    :rules="nameRules"
                    type="name"
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
                    label="New Password"
                    required
                    :rules="passwordRules"
                    type="password"
                  />
                  <v-btn style="margin-bottom: 10px" type="submit" @click="register">Save</v-btn>
                  <v-spacer />
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>
<script>
  export default {
    data: () => ({
      valid: true,
      email: '123@123.com',
      emailRules: [
        v => !!v || 'E-mail is required',
        v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
      ],
      password: '',
      checkbox: false,
      name: 'zhangsan',
      nameRules: [
        v => !!v || 'Name is required',
        v => /^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$/.test(v) || 'Name must contain only letters',
      ],
    }),
    computed: {
      nameErrors () {
        return this.nameRules.filter(rule => !rule(this.name)).map(rule => rule(this.name))
      },
      emailErrors () {
        return this.emailRules.filter(rule => !rule(this.email)).map(rule => rule(this.email))
      },
    },
    methods: {
      register () {
        if (this.$refs.form.validate()) {
          if (!this.email || !this.password || !this.name) {
            alert('Login failed. Please check your email, password, and agree to the terms.')
          } else {
            console.log('Logging in with email:', this.email)
          // TODO: Implement login functionality
          }
        } else {
          alert('Login failed. Please check your email, password, and agree to the terms.')
        }
      },
    },
  }
</script>
<style scoped>
/* 背景部分 */
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
  position: absolute; /* 确保它覆盖在 background 上 */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(138, 43, 226, 0.8),rgba(70, 130, 180, 0.8)); /* 蓝紫渐变色 */
  z-index: 2; /* 在背景和内容之间 */
}

/* 让登录框居中并变成正方形 */
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
  background-color: rgba(255, 255, 255, 0.8); /* 半透明白色背景 */
  flex-direction: column; /* 垂直排列元素 */
  align-items: center; /* 水平居中对齐 */
  justify-content: center; /* 垂直居中对齐 */
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

/* 其他样式 */
.v-btn {
  width: 100%;
  margin-bottom: 10px;
}
</style>
