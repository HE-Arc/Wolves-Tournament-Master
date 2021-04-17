<template>
  <v-container style="margin-top:30px;">
    <TournamentDialog ref="tournamentDialog" />
    <v-row>
      <v-col
        v-show="$store.state.authUser.isAuthenticated"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card tile @click="OpenTournamentDialog" style="padding:10px;">
          <v-card-title></v-card-title>
          <v-card-text class="text-center">
            <v-icon large>mdi-plus</v-icon>
          </v-card-text>
          <v-card-actions></v-card-actions>
        </v-card>
      </v-col>
      <v-col
        v-for="tournament in tournaments"
        :key="tournament.name"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card tile style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            :src="tournament.streamURL"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
          <v-card-title style="color:#01002a;">
            {{ tournament.name }}
          </v-card-title>
          <v-card-text style="color:#01002a;" class="text-sm-left">
            {{ tournament.gameName }}
          </v-card-text>

          <!-- Different button content -->
          <v-card-actions>
            <v-btn
              v-if="tournament.isDeadLineOver"
              @click="$router.push('/tournament/' + tournament.id)"
              tile
              block
              outlined
              color="#01002a"
            >
              See results
            </v-btn>
            <v-btn
              v-else-if="
                (tournament.isParticipating && !tournament.isDeadLineOver) ||
                  (!tournament.isParticipating &&
                    !tournament.isDeadLineOver &&
                    !tournament.isLeader)
              "
              @click="
                OpenTournamentDialog(
                  tournament.id,
                  tournament.isParticipating,
                  tournament.isLeader
                )
              "
              tile
              block
              outlined
            >
              More information
              <!-- Le tournois commencera le {{ tournament.deadLineDate }} -->
            </v-btn>
            <v-btn
              v-else-if="
                !tournament.isParticipating &&
                  !tournament.isDeadLineOver &&
                  tournament.isLeader
              "
              @click="
                OpenTournamentDialog(
                  tournament.id,
                  tournament.isParticipating,
                  tournament.isLeader
                )
              "
              tile
              block
              outlined
            >
              Register your team
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import TournamentDialog from '@/components/dialogs/TournamentDialog'
import WtmApi from '@/services/WtmApiService'

export default {
  name: 'Home',
  components: {
    TournamentDialog
  },
  metaInfo: {
    title: 'Home'
  },
  data: () => ({
    loading: false,
    error: false,
    showPwd: false,

    tournaments: []
  }),
  mounted: function() {
    this.GetTournaments()
  },
  methods: {
    async OpenTournamentDialog(
      idTournament = -1,
      isParticipating = false,
      isLeader = false
    ) {
      if (idTournament !== -1 && typeof idTournament == 'number') {
        this.$refs.tournamentDialog.idTournament = idTournament
        this.$refs.tournamentDialog.isLeader = isLeader
        this.$refs.tournamentDialog.isParticipating = isParticipating
      }

      this.$refs.tournamentDialog.show(this)
    },
    async GetTournaments() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'tournaments/tournamentsforhome?uid=' +
          this.$store.state.authUser.id
      )

      if (response.isSuccess) {
        this.tournaments = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }

      this.loading = false
    }
  }
}
</script>
