<template>
  <div style="padding:30px;" class="home">
    <TournamentDialog ref="tournamentDialog" />
    <v-row>
      <v-col
        v-show="$store.state.authUser.isAuthenticated"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card
          @click="OpenTournamentDialog"
          style="padding:10px;"
        >
          <v-icon large>mdi-plus</v-icon>
        </v-card>
      </v-col>
      <v-col
        v-for="tournament in tournaments"
        :key="tournament.name"
        cols="12"
        sm="6"
        md="4"
      >
        <v-card style="padding:10px;">
          <iframe
            width="100%"
            height="auto"
            :src="tournament.streamURL"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
          <v-card-title>{{ tournament.name }}</v-card-title>
          <v-card-text class="text-sm-left">
            {{ tournament.gameName }}
          </v-card-text>
          <v-card-actions>
            <v-btn tile block outlined>
              Voir les résultats du tournoi
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
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
    async OpenTournamentDialog() {
      this.$refs.tournamentDialog.show()
    },
    async GetTournaments() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'tournaments/'
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
