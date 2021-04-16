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
  metaInfo: {
    title: 'Tournament'
  },
  components: {
    Bracket
  },
  watch: {
    '$store.state.updateTournamentBracket': function() {
      this.GetTeamsByTournament()
    }
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

        if (this.matches.length === 0) {
          // create matchs, check result and run the function
          let baseMatches = TournamentService.CreateBaseMatches(
            this.teams,
            this.tournamentId
          )
          let created = this.CreateBaseMatches(baseMatches)

          if (created) {
            this.matches = baseMatches
          }
        }

        this.SortMatchesArray() // sort by id in tournament

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

        if (this.teams.length > 2) {
          this.GetMatchesbyTournament()
        } else {
          this.$snotify.error(
            this.teams.length +
              " team(s) participate in this tournament. That's not enough to init the tournament."
          )
          this.$router.push('/')
        }
      } else {
        this.$snotify.error('Unable to get matches...')
      }

      this.loading = false
    },
    async CreateBaseMatches(baseMatches) {
      /*
        Create all base matches to init the tournament bracket
      */
      let allCreated = true

      await Promise.all(
        baseMatches.map(async match => {
          const response = await WtmApi.Request(
            'post',
            this.$store.state.apiUrl + 'matchs/',
            match,
            this.$store.getters.getAxiosHeader
          )
          allCreated = allCreated && response.isSuccess
        })
      )

      if (allCreated) {
        this.$snotify.success('Tournament matches created successfully !')
      } else {
        this.$snotify.error(
          'Unable to create tournament matches..\nPlease try later...'
        )
      }

      return allCreated
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
