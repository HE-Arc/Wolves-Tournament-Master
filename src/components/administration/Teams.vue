<template>
  <div class="teams">
    <TeamDialog ref="teamDialog" />
    <DeleteModal ref="deleteTeam" :action="DeleteTeam" />

    <v-layout style="margin:20px;">
      <v-flex xs12>
        <!-- Loading alert -->
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

        <!-- Teams table -->
        <template>
          <v-data-table
            v-show="!loading"
            :headers="headers"
            :items="teams"
            sort-by="name"
            class="elevation-1"
          >
            <template v-slot:top>
              <v-toolbar flat>
                <v-toolbar-title>TEAMS</v-toolbar-title>
                <v-divider class="mx-4" inset vertical></v-divider>
                <v-spacer></v-spacer>
                <v-btn
                  @click.stop="CreateTeam"
                  outlined
                  color="#01002a"
                  tile
                  class="mb-2"
                >
                  New Item
                </v-btn>
              </v-toolbar>
            </template>
            <template v-slot:[`item.actions`]="{ item }">
              <v-icon small class="mr-2" @click="UpdateTeam(item)">
                mdi-pencil
              </v-icon>
              <v-icon small @click="OpenDeleteModal(item)">
                mdi-delete
              </v-icon>
            </template>
          </v-data-table>
        </template>
      </v-flex>
    </v-layout>
  </div>
</template>

<script>
import TeamDialog from '@/components/dialogs/TeamDialog'
import WtmApi from '@/services/WtmApiService'
import DeleteModal from '@/components/modals/Delete'

export default {
  components: {
    TeamDialog,
    DeleteModal
  },
  metaInfo: {
    title: 'Administation - teams'
  },
  data: () => ({
    teams: [],
    loading: false,
    headers: [
      { text: 'ID', value: 'id' },
      { text: 'Name', value: 'name' },
      { text: 'Leader ID', value: 'leader' },
      { text: 'Actions', value: 'actions', sortable: false }
    ]
  }),
  mounted: function() {
    this.GetTeams()
  },
  methods: {
    // Open team dialog to create a new team
    async CreateTeam() {
      this.$refs.teamDialog.show(this, 'Add a new team', null, false)
    },

    /**
     * Open team dialog to update a existing team
     *
     * @param {Object}  team team to update
     */
    async UpdateTeam(team) {
      this.$refs.teamDialog.show(this, 'Update team', team, true)
    },

    // Get all teams
    async GetTeams() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'teams/'
      )

      if (response.isSuccess) {
        this.teams = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    },

    /**
     * Open delete modal to delete a team
     *
     * @param {Object}  team team to delete
     */
    async OpenDeleteModal(team) {
      this.$refs.deleteTeam.show(team)
    },

    /**
     * Action for the delete modal to delete a team
     *
     * @param {Object}  team team to delete
     */
    async DeleteTeam(team) {
      const response = await WtmApi.Request(
        'delete',
        this.$store.state.apiUrl + 'teams/' + team.id + '/',
        null,
        this.$store.getters.getAxiosHeader
      )

      if (response.isSuccess) {
        this.$snotify.success('team ' + team.name + ' deleted successfuly')
        this.$refs.deleteTeam.hide()
        this.GetTeams()
      } else {
        this.$snotify.error('Unable to delete this team...')
        this.$refs.deleteTeam.loading = false
        this.$refs.deleteTeam.hide()
      }
    }
  }
}
</script>
