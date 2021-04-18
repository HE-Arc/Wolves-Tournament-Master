<template>
  <div>
    <LoginDialog ref="loginDialog" />
    <v-app-bar app color="#01002a" dark>
      <v-app-bar-nav-icon
        v-if="$store.state.authUser.isAuthenticated"
        @click="$store.commit('setNavigationDrawer')"
      ></v-app-bar-nav-icon>
      <router-link to="/">
        <img alt="WTM Logo" src="@/assets/wtm.png" width="auto" height="50" />
      </router-link>

      <v-spacer></v-spacer>

      <v-btn v-if="$store.state.authUser.isAuthenticated" tile text>
        <span class="mr-2">
          {{ $store.state.authUser.name }}
        </span>
        <v-icon>mdi-account</v-icon>
      </v-btn>
      <v-btn v-else tile text @click="Login">
        <span class="mr-2">Sign in</span>
        <v-icon>mdi-account</v-icon>
      </v-btn>
    </v-app-bar>
  </div>
</template>

<script>
import LoginDialog from '@/components/dialogs/LoginDialog'

export default {
  components: {
    LoginDialog
  },

  methods: {
    // To show the login dialog
    async Login() {
      this.$refs.loginDialog.show()
    }
  }
}
</script>
