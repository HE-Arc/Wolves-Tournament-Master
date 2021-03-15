<template>
  <div class="teams">
    <TeamDialog ref="teamDialog" />
    <DeleteModal ref="deleteTeam" :action="DeleteTeam" />

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
            :items="teams"
            sort-by="calories"
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
                  dark
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
import TeamService from "@/services/TeamService";
import TeamDialog from "@/components/dialogs/TeamDialog";
import DeleteModal from "@/components/modals/Delete";

export default {
  components: {
    TeamDialog,
    DeleteModal
  },

  data: () => ({
    teams: [],
    loading: false,
    headers: [
      { text: "ID", value: "id" },
      { text: "Name", value: "name" },
      { text: "Leader ID", value: "leader" },
      { text: "Actions", value: "actions", sortable: false }
    ],
    showteamDialog: false
  }),
  mounted: function() {
    this.GetTeams();
  },
  methods: {
    async CreateTeam() {
      this.$refs.teamDialog.show(this, "Add a new team", null, false);
    },
    async UpdateTeam(team) {
      this.$refs.teamDialog.show(this, "Update team", team, true);
    },
    async GetTeams() {
      this.loading = true;

      let result = await TeamService.GetTeams(this.$store.state.token);

      if (result) {
        this.teams = result;
      } else {
        this.$snotify.error("Unable to get teams...");
      }

      this.loading = false;
    },
    async OpenDeleteModal(team) {
      this.$refs.deleteTeam.show(team);
    },
    async DeleteTeam(team) {
      let result = await TeamService.DeleteTeam(this.$store.state.token, team);

      if (result) {
        this.$snotify.success("team '" + team.name + "' deleted successfuly");
        this.$refs.deleteTeam.hide();
        this.GetTeams();
      } else {
        this.$snotify.error("Unable to delete this team...");
        this.$refs.deleteTeam.loading = false;
        this.$refs.deleteTeam.hide();
      }
    }
  }
};
</script>
