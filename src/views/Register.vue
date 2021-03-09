<template>
    <v-card>
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
            v-model="email"
            label="Email"
            dense
            outlined
            :type="'email'"
            clearable
            v-validate="'required'"
            data-vv-name="Email"
            :error-messages="errors.collect('Email')"
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
          <v-text-field
            v-model="confirmpwd"
            label="Confrim your password"
            outlined
            dense
            :type="'password'"
            clearable
            v-validate="'required'"
            data-vv-name="Confirm password"
            :error-messages="errors.collect('Confirm password')"
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
          Register
          <v-icon right> mdi-content-save </v-icon>
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
</template>

<script>
import UserService from "@/services/UserService";

export default {
  data: () => ({
    loading: false,
    error: false,

    id: null,
    username: "",
    email: "",
    pwd: "",
    confirmpwd: "",
  }),

  methods: {
    // To show the dialog
    async Register() {
      const result = await this.$validator.validate();

      if (result && this.pwd == this.confirmpwd) {
        this.loading = true;

        let user = {
          username: this.username,
          email: this.email,
          password: this.pwd
        };

        const result = await UserService.CreateUser(user);

        if (result) {
          this.$router.push({name: 'Home'})

          this.$refs.form.reset();
          this.$snotify.info(user.username + " registered successfuly!");
          this.isVisible = false;
        } else {
          this.$snotify.error(
            "Unable to register...\nPlease try later..."
          );
          this.error = true;
        }

        this.loading = false;
      }
    }
  }
};
</script>
