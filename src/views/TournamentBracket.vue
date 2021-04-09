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
import TeamService from '@/services/TeamService'

// const teams = [
//   {
//     id: 1,
//     name: 'A'
//   },
//   {
//     id: 2,
//     name: 'B'
//   },
//   {
//     id: 3,
//     name: 'C'
//   },
//   {
//     id: 4,
//     name: 'D'
//   },
//   {
//     id: 5,
//     name: 'E'
//   },
//   {
//     id: 6,
//     name: 'F'
//   },
//   {
//     id: 7,
//     name: 'G'
//   }
// ]

export default {
  components: {
    Bracket
  },
  mounted() {
    // this.GetMatchesbyTournament()
    this.GetTeamsByTournament()
  },
  data() {
    return {
      teams: [],
      tournamentId: 2, // TODO remove hardcoded id
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
    async GetTeamsByTournament() {
      this.loading = true

      let response = await TeamService.GetTeamsByTournament(
        this.$store.state.token,
        this.tournamentId
      )

      if (response.isSuccess) {
        this.teams = response.result

        // Create matches in DB. TODO move it on tournament creation.
        // let matches = TournamentService.createBaseMatches(
        //   this.teams,
        //   this.tournamentId
        // )
        // MatchService.CreateMatches(matches)
        // console.log(matches)

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
