<template>
  <div class="notifications">
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
          <v-list-item
            v-for="notification in notifications"
            :key="notification.id"
          >
            <v-list-item-avatar
              @click="UpdateNotification(notification)"
            >
              <v-icon
                v-if="!notification.seen"
                class="grey lighten-1"
                dark
              >
                mdi-bell
              </v-icon>
            </v-list-item-avatar>

            <v-list-item-content>
              <v-list-item-title
                class="text-sm-left"
                v-text="
                  notifiType[notification.notificationType]
                "
              ></v-list-item-title>

              <v-list-item-subtitle
                class="text-sm-left"
                v-text="notification.message"
                >" ></v-list-item-subtitle
              >
            </v-list-item-content>

            <v-list-item-action
              v-if="
                notification.notificationType ==
                  'INVITATION'
              "
            >
              <v-btn
                class="ma-2"
                @click="AcceptTeamInvitation(notification)"
                color="success"
              >
                Accepter
                <template v-slot:loader>
                  <span>Loading...</span>
                </template>
              </v-btn>
            </v-list-item-action>

            <v-list-item-action
              v-if="
                notification.notificationType ==
                  'INVITATION'
              "
            >
              <v-btn
                class="ma-2"
                color="red darken-4"
                @click="RejectTeamInvitation(notification)"
              >
                Refuser
                <template v-slot:loader>
                  <span>Loading...</span>
                </template>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </template>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  components: {},

  data: () => ({
    notifications: [],
    loading: false,
    headers: [
      { text: 'ID', value: 'id' },
      { text: 'User', value: 'user' },
      { text: 'Seen', value: 'seen' },
      { text: 'Message', value: 'message', sortable: false }
    ],
    notifiType: {
      MESSAGE: 'Information',
      INVITATION: 'Invitation'
    }
  }),
  mounted: function() {
    this.GetNotifications()
  },
  methods: {
    async GetNotifications() {
      this.loading = true

      const response = await WtmApi.GetNotifications(
        this.$store.state.apiUrl +
          'notifications?uid=' +
          this.$store.state.authUser.id,
        this.$store.getters.getAxiosConfig
      )

      if (response.isSuccess) {
        this.notifications = response.result
        this.notifications.sort(function(n1, n2) {
          return n1 === n2 ? 0 : n1 ? -1 : 1
        })

        this.$store.commit('updateNotif', response.counter)
      } else {
        this.$snotify.error(
          'Unable to get notifications ...'
        )
      }
      this.loading = false
    },
    async UpdateNotification(notification) {
      if (notification.notificationType != 'INVITATION') {
        notification.seen = true

        const response = await WtmApi.Request(
          'put',
          this.$store.state.apiurl +
            'notifications/' +
            notification.id +
            '/',
          notification,
          this.$store.getters.getAxiosConfig
        )

        if (response.isSuccess) {
          this.$store.commit(
            'updateNotif',
            this.$store.state.nbrNotif - 1
          )
        } else {
          this.$snotify.error(
            'Unable to update notifications ...'
          )
        }
      }
    },
    async AcceptTeamInvitation(notification) {
      let data = {
        userid: this.$store.state.authUser.id,
        notificationid: notification.id
      }

      const response = await WtmApi.Request(
        'post',
        this.$store.state.apiUrl +
          'teams/' +
          notification.team +
          '/adduser/',
        data,
        this.$store.getters.getAxiosConfig
      )
      if (response.isSuccess) {
        console.log(response.result)
        this.GetNotifications()
        this.$snotify.success('User added!')
      } else {
        this.$snotify.error('Unable to get teams...')
      }
    },
    async RejectTeamInvitation(notification) {
      notification.notificationType = 'MESSAGE'
      notification.seen = true
      notification.message =
        '[Declined] ' + notification.message

      const response = await WtmApi.Request(
        'put',
        this.$store.state.apiUrl +
          'notifications/' +
          notification.id +
          '/',
        notification,
        this.$store.getters.getAxiosConfig
      )

      if (response.isSuccess) {
        this.GetNotifications()
        this.$snotify.success(
          'You refused to join the team'
        )
      } else {
        this.$snotify.error(
          'Cannot decline team invitation...'
        )
      }
    }
  }
}
</script>
