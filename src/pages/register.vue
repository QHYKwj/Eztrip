<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title>Register</v-card-title>
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
                    label="Password"
                    required
                    :rules="passwordRules"
                    type="password"
                  />
                  <v-text-field
                    v-model="password2"
                    :error-messages="password2Errors"
                    label="Password2"
                    required
                    :rules="password2Rules"
                    type="password2"
                  />
                  <v-btn style="margin-bottom: 10px" type="submit" @click="register">register</v-btn>
                  <v-spacer />
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
    </v-main>
  </v-app>
</template>
<script>
  import API from '@/config/api'
  export default {
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
      checkbox: false,
      password2: '',
      password2Rules: [
        v => !!v || 'Password is required',
        function (v) {
          return v === this.password || 'Passwords must match'
        }, // 使用普通函数而不是箭头函数
      ],
      name: '',
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
      passwordErrors () {
        return this.passwordRules.filter(rule => !rule(this.password)).map(rule => rule(this.password))
      },
    },
    // mounted () {
    //   const savedUser = localStorage.getItem('currentUser');
    //   if (savedUser) {
    //     this.currentUser = JSON.parse(savedUser);
    //     updateUserInfo.call(this);
    //     showPage.call(this, 'mainPage');
    //     initWebSocket.call(this);
    //   }
    //   document.querySelector('#registerPage form').addEventListener('submit', function (e) {
    //     e.preventDefault();
    //     this.register();
    //   }.bind(this));
    // },
    methods: {
      async register () {
        if (this.$refs.form.validate() && (!this.email || !this.password || !this.password2 || !this.name)) {
          alert('注册失败。请检查您的邮箱、密码和用户名。')
        }
      },
    },
  }
</script>
