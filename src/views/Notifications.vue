<template>
    <div class="notifications">
        <v-layout style="margin:20px;">
            <v-flex xs12>
                <v-alert class="text-xs-center" v-show="loading" outlined v-model="loading" type="info">
                    <v-progress-circular indeterminate color="#01002a"></v-progress-circular>
                </v-alert>
                <template>
                    <v-data-table
                        v-show="!loading"
                        :headers="headers"
                        :items="notifications"
                        sort-by="calories"
                        class="elevation-1"
                    >
                        <template v-slot:top>
                            <v-toolbar flat>
                                <v-toolbar-title>NOTIFICATIONS</v-toolbar-title>
                                <v-divider class="mx-4" inset vertical></v-divider>
                                <v-spacer></v-spacer>
                            </v-toolbar>
                        </template>
                    </v-data-table>
                </template>
            </v-flex>
        </v-layout>
    </div>
</template>

<script>
import NotificationService from '@/services/NotificationService'

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
        ]
    }),
    mounted: function() {
        this.GetNotifications()
    },
    methods: {
        async GetNotifications() {
            this.loading = true

            let response = await NotificationService.GetNotifications(this.$store.state.token)

            if (response.isSuccess) {
                this.notifications = response.result
            } else {
                this.$snotify.error('Unable to get notifications ...')
            }
            this.loading = false
        }
    }
}
</script>
