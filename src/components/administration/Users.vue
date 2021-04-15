<template>
  <div class="teams">
    <v-layout style="margin:20px;">
      <v-flex xs12>
        <v-alert
          class="text-xs-center"
          v-show="loading"
          outlined
          v-model="loading"
          type="info"
        >
          <v-progress-circular
            indeterminate
            color="#01002a"
          ></v-progress-circular>
        </v-alert>
        <template>
          <v-data-table
            v-show="!loading"
            :headers="headers"
            :items="users"
            sort-by="username"
            class="elevation-1"
          >
            <template v-slot:top>
              <v-toolbar flat>
                <v-toolbar-title>USERS</v-toolbar-title>
                <v-divider class="mx-4" inset vertical></v-divider>
              </v-toolbar>
            </template>
            <template v-slot:[`item.actions`]="{ item }">
              <v-icon small class="mr-2" @click="UpdateTeam(item)">
                mdi-cancel
              </v-icon>
            </template>
          </v-data-table>
        </template>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  metaInfo: {
    title: 'Administation - users'
  },
  data: () => ({
    users: [],
    loading: false,
    headers: [
      { text: 'ID', value: 'id' },
      { text: 'Username', value: 'username' },
      { text: 'Email', value: 'email' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]
  }),
  mounted: function() {
    this.GetUsers()
  },
  methods: {
    async UpdateTeam(team) {
      console.log(team)
      //this.$refs.teamDialog.show(this, 'Update team', team, true)
    },
    async GetUsers() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'users/',
        null,
        this.$store.getters.getAxiosHeader
      )

      if (response.isSuccess) {
        this.users = response.result
      } else {
        this.$snotify.error('Unable to get users...')
      }

      this.loading = false
    }
  }
}
</script>
