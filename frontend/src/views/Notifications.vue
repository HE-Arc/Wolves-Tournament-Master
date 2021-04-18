<template>
  <v-container style="margin-top:30px;">
    <v-card tile style="margin-bottom:30px;">
      <v-card-text>
        <h1 style="color:#01002a;">
          Notifications
        </h1>
      </v-card-text>
    </v-card>
    <v-card tile>
      <v-card-text>
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
        <v-alert v-show="notifications.length <= 0" outlined type="info">
          You have no notification yet...
        </v-alert>
        <template v-for="notification in notifications">
          <v-list-item
            :key="notification.id"
            style="margin-top:10px;margin-bottom:10px;"
          >
            <v-row align="center" wrap>
              <v-col xs="12">
                <v-row wrap>
                  <v-list-item-avatar @click="UpdateNotification(notification)">
                    <v-icon v-if="!notification.seen" class="red lighten-1" dark
                      >mdi-bell</v-icon
                    >
                    <v-icon v-else class="grey lighten-1" dark>
                      mdi-bell
                    </v-icon>
                  </v-list-item-avatar>

                  <v-list-item-content>
                    <v-list-item-title
                      class="text-sm-left"
                      v-text="notifiType[notification.notificationType]"
                    ></v-list-item-title>

                    <v-list-item-subtitle
                      class="text-sm-left"
                      v-text="notification.message"
                    ></v-list-item-subtitle>
                  </v-list-item-content>
                </v-row>
              </v-col>
              <v-col xs="12">
                <v-list-item-action
                  v-if="notification.notificationType == 'INVITATION'"
                >
                  <v-row>
                    <v-btn
                      class="ma-2"
                      @click="AcceptTeamInvitation(notification)"
                      color="success"
                      tile
                      outlined
                    >
                      Accept
                    </v-btn>
                    <v-btn
                      class="ma-2"
                      color="error"
                      @click="RejectTeamInvitation(notification)"
                      tile
                      outlined
                    >
                      Decline
                    </v-btn>
                  </v-row>
                </v-list-item-action>
              </v-col>
            </v-row>
          </v-list-item>
          <v-divider :key="notification.message"></v-divider>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  components: {},
  metaInfo: {
    title: 'Notifications'
  },
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
    // Get current authenticated user's notifications
    async GetNotifications() {
      this.loading = true

      const response = await WtmApi.GetNotifications(
        this.$store.state.apiUrl +
          'notifications?uid=' +
          this.$store.state.authUser.id,
        this.$store.getters.getAxiosHeader
      )

      if (response.isSuccess) {
        this.notifications = response.result
        this.SortNotificationsByCreationDate()
        this.$store.commit('updateNotif', response.counter)
      } else {
        this.$snotify.error('Unable to get notifications ...')
      }
      this.loading = false
    },

    /**
     * Update notitification
     *
     * @param {Object} notification notification to update
     */
    async UpdateNotification(notification) {
      if (notification.notificationType != 'INVITATION') {
        notification.seen = true

        const response = await WtmApi.Request(
          'put',
          this.$store.state.apiUrl + 'notifications/' + notification.id + '/',
          notification,
          this.$store.getters.getAxiosHeader
        )

        if (response.isSuccess) {
          this.$store.commit('updateNotif', this.$store.state.nbrNotif - 1)
        } else {
          this.$snotify.error('Unable to update notifications ...')
        }
      }
    },

    /**
     * Accept a notification (invitation in a team)
     *
     * @param {Object} notification notification to accept
     */
    async AcceptTeamInvitation(notification) {
      let data = {
        userid: this.$store.state.authUser.id,
        notificationid: notification.id
      }

      const response = await WtmApi.Request(
        'post',
        this.$store.state.apiUrl + 'teams/' + notification.team + '/adduser/',
        data,
        this.$store.getters.getAxiosHeader
      )
      if (response.isSuccess) {
        this.GetNotifications()
        this.$snotify.success('User added!')
      } else {
        this.$snotify.error('Unable to get teams...')
      }
    },

    /**
     * Reject a notification (invitation in a team)
     *
     * @param {Object} notification notification to reject
     */
    async RejectTeamInvitation(notification) {
      notification.notificationType = 'MESSAGE'
      notification.seen = true
      notification.message = '[Declined] ' + notification.message

      const response = await WtmApi.Request(
        'put',
        this.$store.state.apiUrl + 'notifications/' + notification.id + '/',
        notification,
        this.$store.getters.getAxiosHeader
      )

      if (response.isSuccess) {
        this.GetNotifications()
        this.$snotify.success('You refused to join the team')
      } else {
        this.$snotify.error('Cannot decline team invitation...')
      }
    },
    async SortNotificationsByCreationDate() {
      this.notifications.sort((n1, n2) => {
        let date1 = new Date(n1.creationDate).getTime()
        let date2 = new Date(n2.creationDate).getTime()

        if (date1 < date2) {
          return 1
        } else if (date1 > date2) {
          return -1
        }

        return 0
      })
    }
  }
}
</script>
