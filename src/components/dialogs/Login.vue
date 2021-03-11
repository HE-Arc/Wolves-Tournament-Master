<template>
  <v-dialog v-model="isVisible" max-width="500px" @keydown.esc="hide">
    <v-card>
      <v-toolbar dark color="primary">
        <v-toolbar-title>Sign in</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn icon dark @click="hide">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-title></v-card-title>
      <v-card-text>
        <v-form ref="form" style="padding:10px;">
          <v-text-field
            v-model="username"
            label="Username"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="Username"
            :error-messages="errors.collect('Username')"
          ></v-text-field>
          <v-text-field
            v-model="pwd"
            label="Password"
            outlined
            dense
            :type="'password'"
            clearable
            v-validate="'required'"
            data-vv-name="Password"
            :error-messages="errors.collect('Password')"
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
        <router-link @click.native="hide" to="/register">Sign up for free !</router-link> 
        <v-spacer></v-spacer>
        <v-btn tile color="success" @click="Login">Sign in</v-btn>
      </v-card-actions>
      <v-card-actions v-show="loading">
        <v-spacer></v-spacer>
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import UserService from "@/services/UserService";

export default {
  data: () => ({
    isVisible: false,
    loading: false,
    error: false,

    id: null,
    username: "",
    pwd: ""
  }),

  methods: {
    // To show the dialog
    show() {
      this.isVisible = true;
    },
    hide() {
      this.$refs.form.reset();
      this.isVisible = false;
    },
    async Login() {
      const result = await this.$validator.validate();

      if (result) {
        this.loading = true;

        let user = {
          username: this.username,
          password: this.pwd
        };

        const result = await UserService.Login(user);

        if (result) {
          this.$store.commit('updateToken', result.token)
          // this.$store.commit("setAuthUser",
          //   {authUserId: result.user_id, authUserEmail: result.email, isAuthenticated: true}
          // )
          //this.$router.push({name: 'Home'})

          this.$refs.form.reset();
          this.$snotify.info(user.username + " logged in successfuly!");
          this.isVisible = false;
        } else {
          this.$snotify.error(
            "Unable to login...\nPlease try later..."
          );
          this.error = true;
        }

        this.loading = false;
      }
    }
  }
};
</script>
