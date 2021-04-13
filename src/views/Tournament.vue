<template>
  <bracket style="margin:20px;" :rounds="rounds">
    <template slot="player" slot-scope="{ player }">
      {{ player.name }}
    </template>
  </bracket>
</template>

<script>
import Bracket from '@/components/bracket/Bracket'
import TournamentService from '@/services/TournamentService'
import WtmApi from '@/services/WtmApiService'

export default {
  props: ['tournamentId'],
  components: {
    Bracket
  },
  mounted() {
    this.GetTeamsByTournament()
  },
  data() {
    return {
      teams: [],
      matches: [],
      rounds: []
    }
  },
  methods: {
    async GetMatchesbyTournament() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'matchs/getmatchsbytournament?tid=' +
          this.tournamentId
      )

      if (response.isSuccess) {
        this.matches = response.result

        this.SortMatchesArray() // sort by id in tournament

        // TODO place it elsewhere
        this.rounds = TournamentService.CreateRounds(this.matches, this.teams)
      } else {
        this.$snotify.error('Unable to get matches...')
      }

      this.loading = false
    },
    async GetTeamsByTournament() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'teams/getteamsbytournament?tid=' +
          this.tournamentId
      )

      if (response.isSuccess) {
        this.teams = response.result

        // Create matches in DB. TODO move it on tournament creation.
        let matches = TournamentService.CreateBaseMatches(
          this.teams,
          this.tournamentId
        )
        console.log(matches)

        this.GetMatchesbyTournament()
      } else {
        this.$snotify.error('Unable to get matches...')
      }

      this.loading = false
    },
    SortMatchesArray() {
      this.matches.sort((m1, m2) => {
        if (m1.idInTournament > m2.idInTournament) {
          return 1
        }
        if (m1.idInTournament < m2.idInTournament) {
          return -1
        }
        return 0 //shloudn't happen
      })
    }
  }
}
</script>
