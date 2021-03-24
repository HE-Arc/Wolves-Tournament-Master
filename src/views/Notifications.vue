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
              <v-btn class="ma-2" color="red darken-4">
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
import NotificationService from '@/services/NotificationService'
import TeamService from '@/services/TeamService'

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

      let response = await NotificationService.GetNotifications(
        this.$store.state.token,
        this.$store.state.authUserId
      )

      if (response.isSuccess) {
        this.notifications = response.result
      } else {
        this.$snotify.error(
          'Unable to get notifications ...'
        )
      }
      this.loading = false
    },
    async UpdateNotification(notification) {
      notification.seen = true
      let response = await NotificationService.UpdateNotification(
        this.$store.state.token,
        notification
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
    },
    async AcceptTeamInvitation(notification) {
      console.log(
        "yo j'ai accepté de rejoindre " + notification.team
      )
      let response = await TeamService.GetTeamById(
        notification.team
      )
      if (response.isSuccess) {
        console.log(response.result)
        //response.result.users.add()
      } else {
        this.$snotify.error('Unable to get teams...')
      }
    }
  }
}
</script>
