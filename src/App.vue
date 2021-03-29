<template>
  <v-app>
    <LoginDialog ref="loginDialog" />
    <vue-snotify></vue-snotify>

    <v-navigation-drawer
      v-if="$store.state.authUser.isAuthenticated"
      v-model="drawer"
      app
    >
      <template v-slot:prepend>
        <v-list-item two-line>
          <v-list-item-avatar>
            <img
              src="https://randomuser.me/api/portraits/women/81.jpg"
            />
          </v-list-item-avatar>

          <v-list-item-content>
            <v-list-item-title>
              {{ $store.state.authUser.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              Logged In
            </v-list-item-subtitle>
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
            <v-badge
              v-if="
                item.title == 'Notifications' &&
                  $store.state.nbrNotif > 0
              "
              overlap
              color="red"
              :content="$store.state.nbrNotif"
            >
              <v-icon>{{ item.icon }}</v-icon>
            </v-badge>
            <v-icon v-else>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <router-link
            style="text-decoration:none;color:gray;"
            :to="item.path"
          >
            <v-list-item-content>
              <v-list-item-title>
                {{ item.title }}
              </v-list-item-title>
            </v-list-item-content>
          </router-link>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-btn
        style="margin-top:10px;"
        color="#01002a"
        block
        tile
        dark
        @click="Logout"
      >
        Logout
      </v-btn>
    </v-navigation-drawer>

    <v-app-bar app color="#01002a" dark>
      <v-app-bar-nav-icon
        v-if="$store.state.authUser.isAuthenticated"
        @click="drawer = !drawer"
      ></v-app-bar-nav-icon>
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
        v-if="$store.state.authUser.isAuthenticated"
        tile
        text
      >
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

    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import LoginDialog from '@/components/dialogs/LoginDialog'

export default {
  name: 'App',

  components: {
    LoginDialog
  },

  data: () => ({
    drawer: null,
    items: [
      {
        title: 'Home',
        icon: 'mdi-home',
        path: '/'
      },
      {
        title: 'My account',
        icon: 'mdi-account',
        path: '/'
      },
      {
        title: 'Teams',
        icon: 'mdi-account-multiple',
        path: '/teams'
      },
      {
        title: 'Team',
        icon: 'mdi-account-multiple',
        path: '/team'
      },
      {
        title: 'Tournaments',
        icon: 'mdi-google-controller',
        path: '/tournament'
      },
      {
        title: 'Notifications',
        icon: 'mdi-bell',
        path: '/notifications'
      }
    ]
  }),

  methods: {
    async Login() {
      this.$refs.loginDialog.show()
    },
    Logout() {
      this.$store.commit('logout')
      this.$router.push('/')
    }
  }
}
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
