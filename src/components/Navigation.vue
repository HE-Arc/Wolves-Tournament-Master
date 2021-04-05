<template>
  <v-navigation-drawer
    v-if="$store.state.authUser.isAuthenticated"
    v-model="$store.state.navigationDrawer"
    app
  >
    <template v-slot:prepend>
      <v-list-item two-line>
        <v-list-item-avatar>
          <img src="https://randomuser.me/api/portraits/women/81.jpg" />
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
      <v-list-item v-for="item in items" :key="item.title">
        <v-list-item-icon>
          <v-badge
            v-if="item.title == 'Notifications' && $store.state.nbrNotif > 0"
            overlap
            color="red"
            :content="$store.state.nbrNotif"
          >
            <v-icon>{{ item.icon }}</v-icon>
          </v-badge>
          <v-icon v-else>{{ item.icon }}</v-icon>
        </v-list-item-icon>

        <router-link style="text-decoration:none;color:gray;" :to="item.path">
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
</template>

<script>
export default {
  data: () => ({
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
    Logout() {
      this.$store.commit('logout')
      this.$router.push('/')
    }
  }
}
</script>
