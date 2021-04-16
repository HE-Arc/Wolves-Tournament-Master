<template>
  <v-container style="margin-top:30px;">
    <!-- Check if user is admin -->
    <v-card tile style="padding-left:30px;margin-bottom:10px;">
      <h1 style="color:#01002a;">
        Administration
      </h1>
    </v-card>

    <v-card tile height="55px" flat>
      <v-bottom-navigation
        v-model="bottomNav"
        :value="true"
        color="#01002a"
        absolute
      >
        <v-btn value="Users">
          <span>Users</span>
          <v-icon>mdi-account</v-icon>
        </v-btn>

        <v-btn value="Teams">
          <span>Teams</span>
          <v-icon>mdi-account-multiple</v-icon>
        </v-btn>
      </v-bottom-navigation>
    </v-card>

    <component v-bind:is="bottomNav"></component>

    <!-- <div v-if="$userService.user.role != 'ADMIN'">
      <v-alert :value="true" type="warning">
        You need to be an administrator to access this page !
      </v-alert>
    </div> -->
  </v-container>
</template>

<script>
import Users from '@/components/administration/Users.vue'
import Teams from '@/components/administration/Teams.vue'

export default {
  components: {
    Users,
    Teams
  },
  data: () => ({
    bottomNav: 'Users'
  })
}
</script>
