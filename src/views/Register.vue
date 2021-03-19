<template>
  <v-col xs="12" offset-sm="3" sm="6" offset-md="4" md="4">
    <v-card>
      <v-card-title>Sign up</v-card-title>
      <v-card-text>
        <v-form ref="form" style="padding:10px;">
          <v-text-field
            v-model="username"
            label="Username"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="username"
            :error-messages="errors.collect('username')"
          ></v-text-field>
          <v-text-field
            v-model="email"
            label="Email"
            dense
            outlined
            :type="'email'"
            clearable
            v-validate="'required|email'"
            data-vv-name="email"
            :error-messages="errors.collect('email')"
          ></v-text-field>
          <v-text-field
            :append-icon="
              showPwd ? 'mdi-eye' : 'mdi-eye-off'
            "
            v-model="pwd"
            label="Password"
            outlined
            dense
            :type="showPwd ? 'text' : 'password'"
            clearable
            v-validate="'required|min:8'"
            data-vv-name="password"
            :error-messages="errors.collect('password')"
            hint="At least 8 characters"
            @click:append="showPwd = !showPwd"
          ></v-text-field>
          <v-text-field
            :append-icon="
              showPwd ? 'mdi-eye' : 'mdi-eye-off'
            "
            v-model="confirmpwd"
            label="Confrim your password"
            outlined
            dense
            :type="showPwd ? 'text' : 'password'"
            clearable
            v-validate="'required|min:8'"
            data-vv-name="confirm password"
            :error-messages="
              errors.collect('confirm password')
            "
            @click:append="showPwd = !showPwd"
          ></v-text-field>
          <v-alert
            v-show="error"
            v-model="error"
            dismissible
            outlined
            type="error"
          >
            An error occured... Please try later!
          </v-alert>
        </v-form>
      </v-card-text>
      <v-card-actions v-show="!loading">
        <v-spacer></v-spacer>
        <v-btn tile color="success" @click="Register">
          Sign up
          <v-icon right> mdi-account-plus </v-icon>
        </v-btn>
      </v-card-actions>
      <v-card-actions v-show="loading">
        <v-spacer></v-spacer>
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </v-card-actions>
    </v-card>
  </v-col>
</template>

<script>
import UserService from '@/services/UserService'

export default {
  data: () => ({
    loading: false,
    error: false,
    showPwd: false,

    id: null,
    username: '',
    email: '',
    pwd: '',
    confirmpwd: ''
  }),

  methods: {
    async Register() {
      const result = await this.$validator.validate()

      if (result && this.pwd == this.confirmpwd) {
        this.loading = true

        let user = {
          username: this.username,
          email: this.email,
          password: this.pwd
        }

        const response = await UserService.CreateUser(user)

        if (response.isSuccess) {
          this.$refs.registerForm.reset()
          this.$snotify.success(
            this.username + ' registered successfuly!'
          )
          this.$router.push({ name: 'Home' })
        } else {
          this.$snotify.error(this.errorMessage)
          this.error = true
        }

        this.loading = false
      } else {
        this.errorMessage =
          this.pwd == this.confirmpwd
            ? this.errorMessage
            : "Passwords doesn't match !"
        this.$snotify.error(this.errorMessage)
        this.error = true
      }
    }
  }
}
</script>
