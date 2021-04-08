<template>
  <bracket :rounds="rounds">
    <template slot="player" slot-scope="{ player }">
      {{ player.name }}
    </template>
  </bracket>
</template>

<script>
import Bracket from 'vue-tournament-bracket'
import MatchService from '@/services/MatchService'
import TournamentService from '@/services/TournamentService'

const teams = [
  {
    id: 1,
    name: 'A'
  },
  {
    id: 2,
    name: 'B'
  },
  {
    id: 3,
    name: 'C'
  },
  {
    id: 4,
    name: 'D'
  },
  {
    id: 5,
    name: 'E'
  },
  {
    id: 6,
    name: 'F'
  },
  {
    id: 7,
    name: 'G'
  }
]

export default {
  components: {
    Bracket
  },
  mounted() {
    // TODO move it on tournament creation.
    // The tells should come from the DB --> getTournamentTeams
    // let matches = TournamentService.createBaseMatches(teams, this.tournamentId)
    // MatchService.CreateMatches(matches)
    this.GetMatchesbyTournament()
  },
  data() {
    return {
      teams: teams,
      tournamentId: 1, // TODO remove hardcoded id
      matches: [],
      rounds: []
    }
  },
  methods: {
    async GetMatchesbyTournament() {
      this.loading = true

      let response = await MatchService.GetMatchesByTournament(
        this.tournamentId
      )

      if (response.isSuccess) {
        this.matches = response.result
        this.SortMatchesArray() // sort by id in tournament

        // TODO place it elsewhere
        this.rounds = TournamentService.createRounds(this.matches, this.teams)
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
