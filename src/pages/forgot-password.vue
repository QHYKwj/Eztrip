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
                    label="New Password"
                    required
                    :rules="passwordRules"
                    type="password"
                  />
                  <v-btn style="margin-bottom: 10px" @click="resetPassword">Save</v-btn>
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
  import axios from 'axios'

  export default {
    data () {
      return {
        valid: true,
        name: '',
        email: '',
        password: '',

        nameRules: [
          v => !!v || 'Name is required',
        ],

        emailRules: [
          v => !!v || 'E-mail is required',
          v => /.+@.+\..+/.test(v) || 'E-mail must be valid',
        ],

        passwordRules: [
          v => !!v || 'Password is required',
          v => v.length >= 6 || 'Password must be at least 6 characters long',
        ],
      }
    },

    computed: {
      nameErrors () {
        return this.nameRules
          .filter(rule => rule(this.name) !== true)
          .map(rule => rule(this.name))
      },
      emailErrors () {
        return this.emailRules
          .filter(rule => rule(this.email) !== true)
          .map(rule => rule(this.email))
      },
      passwordErrors () {
        return this.passwordRules
          .filter(rule => rule(this.password) !== true)
          .map(rule => rule(this.password))
      },
    },

    methods: {
      async resetPassword () {
        const { valid } = await this.$refs.form.validate()
        if (!valid) {
          alert('Please check your input.')
          return
        }

        const formData = new URLSearchParams()
        formData.append('username', this.name)
        formData.append('email', this.email)
        formData.append('new_password', this.password)

        try {
          // Ensure that your backend URL is correct
          const response = await axios.post(
            '/api/user/change_password',
            formData,
            {
              headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
              },
            },
          )

          alert(response.data.message || 'Password changed successfully. Please log in again.')
          this.$router.push('/')
        } catch (error) {
          console.error(error)
          if (error.response && error.response.data) {
            alert(error.response.data.detail || 'Failed to reset password. Please try again later.')
          } else {
            alert('An unknown error occurred. Please try again later.')
          }
        }
      },
    },
  }
</script>

<style scoped>
/* Background styles */
html, body {
  height: 100%;
  margin: 0;
}

.app-container {
  position: relative;
  height: 100%;
}

.background, .background1 {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  overflow: hidden;
}

.background {
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

.background1 {
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
  background: linear-gradient(to bottom, rgba(138, 43, 226, 0.8), rgba(70, 130, 180, 0.8));
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
