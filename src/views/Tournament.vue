<template>
  <v-container style="margin-top:30px;">
    <v-card tile>
      <v-row
        style="color:#01002a;margin-left:16px;margin-right:16px;"
        align="center"
      >
        <h1>{{ tournament.name }}</h1>
        <h3 class="ml-10">{{ tournament.gameName }}</h3>
      </v-row>
    </v-card>
    <v-card tile style="margin-top:30px;">
      <v-flex xs12 style="overflow:auto;padding:30px;margin:15px;">
        <bracket :rounds="rounds">
          <template slot="player" slot-scope="{ player }">
            {{ player.name }}
          </template>
        </bracket>
      </v-flex>
    </v-card>
  </v-container>
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
    this.GetTournament()
    this.GetTournamentReferees()
  },
  data: () => ({
    referees: undefined,
    teams: [],
    matches: [],
    rounds: [],
    tournament: {
      name: '',
      gameName: ''
    }
  }),
  methods: {
    async GetTournament() {
      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'tournaments/' + this.tournamentId + '/'
      )
      console.log(response.result)
      if (response.isSuccess) {
        this.tournament = response.result
      } else {
        this.$snotify.error('Unable to get tournament informations ...')
      }
    },
    async GetTournamentReferees() {
      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'users/' +
          this.tournamentId +
          '/gettournamentreferees'
      )

      if (response.isSuccess) {
        this.referees = response.result
        this.GetTeamsByTournament()
      } else {
        this.$snotify.error('Unable to get referees for this tournament ...')
      }
    },
    async GetMatchesbyTournament() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'matchs/getmatchsbytournament?tid=' +
          this.tournamentId
      )

      let tournamentInit = false
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
            tournamentInit = true
            this.matches = baseMatches
          } else {
            this.$snotify.error('Unable to init tournament...')
          }
        }

        // the matches needs to be loaded from the DB to allow their score update
        // (otherwise the match id is not avaible)
        if (!tournamentInit) {
          console.log('YO')
          this.SortMatchesArray() // sort by id in tournament

          this.rounds = TournamentService.CreateRounds(
            this.matches,
            this.teams,
            this.referees
          )
        } else {
          // get matches form DB
          this.GetTeamsByTournament()
        }
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
              ' team(s) participate in ' +
              this.tournament.name +
              " tournament. That's not enough to init the tournament."
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
        } else if (m1.idInTournament < m2.idInTournament) {
          return -1
        }
        return 0 //shloudn't happen
      })
    }
  }
}
</script>
