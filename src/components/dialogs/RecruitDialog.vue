<template>
  <v-dialog
    v-model="isVisible"
    max-width="800px"
    @keydown.esc="hide"
    @click:outside="hide"
  >
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>
          Recruit a new member
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn icon dark @click="hide">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-title></v-card-title>
      <v-card-text>
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
                  <v-icon small class="mr-2" @click="Recruit(item)">
                    mdi-account-plus
                  </v-icon>
                </template>
              </v-data-table>
            </template>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  data: () => ({
    isVisible: false,
    loading: false,
    error: false,

    users: [],
    headers: [
      { text: 'Username', value: 'username' },
      { text: 'Email', value: 'email' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]
  }),
  methods: {
    // To show the dialog
    show() {
      this.isVisible = true
      this.GetUsers()
    },
    hide() {
      this.error = false
      this.isVisible = false
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
    },
    async Recruit(user) {
      console.log(user)
    }
  }
}
</script>
