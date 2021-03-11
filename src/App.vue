<template>  
  <v-app>
    <LoginDialog ref="loginDialog" /> 
    <vue-snotify></vue-snotify>

    <v-navigation-drawer
      v-model="drawer"
      app
    >
       <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-avatar>
            <img src="https://randomuser.me/api/portraits/women/81.jpg">
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title>Jane Smith</v-list-item-title>
            <v-list-item-subtitle>Logged In</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </template>

      <v-divider></v-divider>

      <v-list dense>
        <v-list-item
          v-for="item in items"
          :key="item.title"
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <router-link style="text-decoration:none;color:gray;" :to=item.path>
            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
          </router-link>
          
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar
      app
      color="#01002a"
      dark
    > 
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <router-link to="/">
        <img
          alt="WTM Logo"
          src="@/assets/wtm.png"
          width="auto"
          height="50"
        />
      </router-link>

      <v-spacer></v-spacer>

      <v-btn
        text
        @click="Login"
      >
        <span class="mr-2">Sign in</span>
        <v-icon>mdi-account</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view></router-view>
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
    drawer: null,
    items: [
      { title: 'Home', icon: 'mdi-home', path:"/" },
      { title: 'My account', icon: 'mdi-account', path:"/" },
      { title: 'Teams', icon: 'mdi-account-multiple', path:"/teams" },
      { title: 'Tournaments', icon: 'mdi-google-controller', path:"/tournament" }
    ],
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
</style>
