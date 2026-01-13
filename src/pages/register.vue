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
                <v-form ref="formRef" v-model="valid" lazy-validation> 
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
                  <v-btn style="margin-bottom: 10px" type="submit" @click="register">register</v-btn>
                  <v-spacer />
                  Already have an account?
                  <v-btn color="primary" href="/login" style="margin-left: 10px">
                    login
                  </v-btn>
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
import axios from 'axios'

export default {
  name: 'Register', 
  data: () => ({
    currentUser: JSON.parse(localStorage.getItem('currentUser')) || null,
    valid: true,
    email: '',
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
    ],
    password: '',
    passwordRules: [
      v => !!v || 'Password is required',
    ],
    password2: '',
    name: '',
    nameRules: [
      v => !!v || 'Name is required',
      v => /^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$/.test(v) || 'Name must contain only letters',
    ],
  }),
  computed: {
    nameErrors() {
      return this.nameRules.filter(rule => !rule(this.name)).map(rule => rule(this.name))
    },
    emailErrors() {
      return this.emailRules.filter(rule => !rule(this.email)).map(rule => rule(this.email))
    },
    passwordErrors() {
      return this.passwordRules.filter(rule => !rule(this.password)).map(rule => rule(this.password))
    },
    password2Errors() {
      const rules = this.getPassword2Rules()
      return rules.filter(rule => !rule(this.password2)).map(rule => rule(this.password2))
    }
  },
  methods: {
    getPassword2Rules() {
      return [
        v => !!v || 'Confirm Password is required',
        v => v === this.password || 'Passwords must match'
      ]
    },
    async register() {
      const isFormValid = await this.$refs.formRef.validate()
      if (!isFormValid) {
        alert('Please fill in the form correctly!')
        return
      }

      try {
        const params = new URLSearchParams()
        params.append('username', this.name)
        params.append('email', this.email)
        params.append('password', this.password)
        params.append('confirm_password', this.password2)

        const response = await axios.post('/api/user/register', params, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })

        alert('Register successful! Please login.')
        window.location.href = '/login'

      } catch (error) {
        let errorMsg = 'Register failed! '
        if (error.response) {
          errorMsg += error.response.data.detail || 'Unknown error'
        } else if (error.request) {
          errorMsg += 'Cannot connect to server'
        } else {
          errorMsg += error.message
        }
        alert(errorMsg)
      }
    },
  },
}
</script>

<style scoped>

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