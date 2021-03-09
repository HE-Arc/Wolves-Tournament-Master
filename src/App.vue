<template>  
  <v-app>
    <LoginDialog ref="loginDialog" /> 

    <vue-snotify>
      
    </vue-snotify>
    <v-app-bar
      app
      color="primary"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />

        <v-img
          alt="Vuetify Name"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-name-dark.png"
          width="100"
        />
      </div>

      <v-spacer></v-spacer>

      <v-btn
        target="_blank"
        text
        @click="Login"
      >
        <span class="mr-2">Login</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <div id="nav">
        <router-link to="/">Home</router-link> |
        <router-link to="/teams">Teams</router-link> |
        <router-link to="/about">About</router-link>
      </div>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import LoginDialog from "@/components/dialogs/Login";

export default {
  name: 'App',

  components: {
    LoginDialog
  },

  data: () => ({
    //
  }),

   methods: {
    async Login() {
      this.$refs.loginDialog.show();
    },
    Logout() {
      this.$store.commit('removeToken')
    }
   }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
