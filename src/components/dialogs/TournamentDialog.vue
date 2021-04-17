<template>
  <v-dialog
    v-model="isVisible"
    max-width="500px"
    @keydown.esc="hide"
    @click:outside="hide"
    @keydown.enter="CreateTournament"
  >
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title v-if="!isDisabled">
          Create a tournament
        </v-toolbar-title>
        <v-toolbar-title v-else-if="!isLeader || isParticipating">
          Tournament information
        </v-toolbar-title>
        <v-toolbar-title v-else>Register for this tournament</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn icon dark @click="hide">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-title></v-card-title>
      <v-card-text>
        <v-form ref="form" style="padding: 10px">
          <v-text-field
            v-model="name"
            :disabled="isDisabled"
            label="Name"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="name"
            :error-messages="errors.collect('name')"
          ></v-text-field>
          <v-text-field
            v-model="game"
            :disabled="isDisabled"
            label="Game"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="game"
            :error-messages="errors.collect('game')"
          ></v-text-field>
          <v-text-field
            v-model="duration"
            :disabled="isDisabled"
            label="Round duration (in minutes)"
            dense
            outlined
            clearable
            v-validate="'required|numeric'"
            data-vv-name="duration"
            :error-messages="errors.collect('duration')"
          ></v-text-field>
          <v-text-field
            v-model="pause"
            :disabled="isDisabled"
            label="Pause between two round (in minutes)"
            dense
            outlined
            clearable
            v-validate="'required|numeric'"
            data-vv-name="pause"
            :error-messages="errors.collect('pause')"
          ></v-text-field>
          <v-menu
            ref="menu"
            :disabled="isDisabled"
            v-model="menu"
            :close-on-content-click="false"
            :return-value.sync="limitDate"
            transition="scale-transition"
            offset-y
            min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-combobox
                :disabled="isDisabled"
                chips
                small-chips
                prepend-inner-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                v-model="limitDate"
                label="Limit date for registration"
                dense
                outlined
                clearable
                v-validate="'required'"
                data-vv-name="limit date"
                :error-messages="errors.collect('limit date')"
              ></v-combobox>
            </template>
            <v-date-picker
              v-model="limitDate"
              no-title
              scrollable
              :min="new Date().toISOString().slice(0, 10)"
            >
              <v-spacer></v-spacer>
              <v-btn text color="#01002a" @click="menu = false">
                Cancel
              </v-btn>
              <v-btn text color="#01002a" @click="$refs.menu.save(limitDate)">
                OK
              </v-btn>
            </v-date-picker>
          </v-menu>

          <v-text-field
            v-model="nbrTeams"
            :disabled="isDisabled"
            label="Number of teams"
            dense
            outlined
            clearable
            hint="Must be between 4 and 16"
            v-validate="'required|numeric|min_value:4|max_value:16'"
            data-vv-name="number of teams"
            :error-messages="errors.collect('number of teams')"
          ></v-text-field>

          <v-select
            v-if="!isDisabled"
            v-model="referees"
            :items="users"
            item-text="username"
            item-value="id"
            chips
            label="Referees"
            multiple
            outlined
            v-validate="'required'"
            data-vv-name="referees"
            :error-messages="errors.collect('referees')"
          ></v-select>

          <v-text-field
            v-if="!isDisabled"
            v-model="streamUrl"
            label="Stream URL"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="stream URL"
            :error-messages="errors.collect('stream URL')"
          ></v-text-field>
          <v-select
            v-if="isDisabled && isLeader && !isParticipating"
            v-model="registeredTeam"
            :items="teams"
            item-text="name"
            item-value="id"
            label="Team to register"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="team to register"
            :error-messages="errors.collect('team to register')"
          ></v-select>

          <!-- Display error  -->
          <v-alert
            v-show="error"
            v-model="error"
            dismissible
            outlined
            type="error"
          >
            An error occured... Please try later!
          </v-alert>
        </v-form>
      </v-card-text>

      <!-- Save button -->
      <v-card-actions v-show="!loading">
        <v-spacer></v-spacer>
        <v-btn
          tile
          color="success"
          @click="CreateTournament"
          v-if="!isDisabled"
        >
          Save
          <v-icon right> mdi-content-save </v-icon>
        </v-btn>
        <v-btn
          tile
          color="success"
          @click="AddTeam"
          v-else-if="isDisabled && isLeader && !isParticipating"
        >
          Participate
          <v-icon right> mdi-content-save </v-icon>
        </v-btn>
      </v-card-actions>
      <v-card-actions v-show="loading">
        <v-spacer></v-spacer>
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import WtmApi from '@/services/WtmApiService'

export default {
  data: () => ({
    isVisible: false,
    parent: undefined,
    loading: false,
    error: false,
    menu: false,
    disabledDates: {
      to: new Date(Date.now() - 8640000)
    },
    users: [],

    // tournament: {
    //   name: null
    // },
    id: null,
    name: null,
    game: null,
    duration: null,
    pause: null,
    limitDate: null,
    nbrTeams: null,
    referees: null,
    streamUrl: null,

    // edit or readonly
    idTournament: -1,
    isDisabled: false,

    // register a team to a tournament
    registeredTeam: null,
    isLeader: false,
    isParticipating: false,
    teams: []
  }),
  methods: {
    show(parent) {
      this.parent = parent
      if (this.idTournament !== -1) {
        this.DisplayTournament()
        this.GetTeamsByLeader()
      } else {
        this.isDisabled = false
      }
      this.isVisible = true
      this.GetUsers()
    },
    hide() {
      this.error = false
      this.$refs.form.reset()
      this.isVisible = false
      this.idTournament = -1
    },
    async GetUsers() {
      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'users/',
        null,
        this.$store.getters.getAxiosHeader
      )

      if (response.isSuccess) {
        this.users = response.result
      } else {
        this.$snotify.error('Unable to get users...')
      }
    },
    async CreateTournament() {
      const result = await this.$validator.validate()

      if (result) {
        this.loading = true

        let tournament = {
          name: this.name,
          gameName: this.game,
          matchDuration: this.duration,
          breakDuration: this.pause,
          deadLineDate: this.limitDate,
          nbTeam: this.nbrTeams,
          streamURL: this.streamUrl,
          organizer: this.$store.state.authUser.name,
          referees: this.referees
        }

        const response = await WtmApi.Request(
          'post',
          this.$store.state.apiUrl + 'tournaments/',
          tournament,
          this.$store.getters.getAxiosHeader
        )

        if (response.isSuccess) {
          this.$refs.form.reset()
          this.$snotify.success(tournament.name + ' created successfuly!')
          this.isVisible = false
          this.parent.GetTournaments()
        } else {
          this.$snotify.error(
            'Unable to save this team...\nPlease try later...'
          )
          this.error = true
        }

        this.loading = false
      }
    },
    async DisplayTournament() {
      this.isDisabled = true

      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl + 'tournaments/' + this.idTournament,
        null,
        this.$store.getters.getAxiosConfig
      )

      if (response.isSuccess) {
        let tournament = response.result

        this.id = tournament.id
        this.name = tournament.name
        this.game = tournament.gameName
        this.duration = tournament.matchDuration
        this.pause = tournament.breakDuration
        this.limitDate = tournament.deadLineDate
        this.nbrTeams = tournament.nbTeam
        this.streamUrl = tournament.streamURL
      } else {
        this.$snotify.error(
          'Unable to get tournament information...\nPlease try later...'
        )
        this.error = true
      }

      this.loading = false
    },
    async GetTeamsByLeader() {
      this.loading = true

      const response = await WtmApi.Request(
        'get',
        this.$store.state.apiUrl +
          'teams/' +
          this.$store.state.authUser.id +
          '/getteamsbyleader'
      )

      if (response.isSuccess) {
        this.teams = response.result
      } else {
        this.$snotify.error('Unable to get teams...')
      }
      this.loading = false
    },
    async AddTeam() {
      this.loading = true

      let data = {
        teamid: this.registeredTeam
      }

      const response = await WtmApi.Request(
        'post',
        this.$store.state.apiUrl +
          'tournaments/' +
          this.idTournament +
          '/addTeam/',
        data,
        this.$store.getters.getAxiosConfig
      )

      if (response.isSuccess) {
        let team = response.result
        this.parent.GetTournaments()
        this.$snotify.success(
          'Team ' + team.name + ' registered successfully to this tournament !'
        )
      } else {
        this.$snotify.error('Unable to register the team to this tournament...')
      }
      this.isVisible = false
      this.loading = false
    }
  }
}
</script>
