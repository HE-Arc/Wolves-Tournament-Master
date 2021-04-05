<template>
  <v-dialog v-model="isVisible" max-width="500px" @keydown.esc="hide">
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>Create a tournament</v-toolbar-title>
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
            v-model="menu"
            :close-on-content-click="false"
            :return-value.sync="limitDate"
            transition="scale-transition"
            offset-y
            min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-combobox
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
            label="Number of teams"
            dense
            outlined
            clearable
            hint="Must be between 2 and 16"
            v-validate="'required|numeric|min_value:2|max_value:16'"
            data-vv-name="number of teams"
            :error-messages="errors.collect('number of teams')"
          ></v-text-field>

          <v-text-field
            v-model="streamUrl"
            label="Stream URL"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="stream URL"
            :error-messages="errors.collect('stream URL')"
          ></v-text-field>
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
      <v-card-actions v-show="!loading">
        <v-spacer></v-spacer>
        <v-btn tile color="success" @click="CreateTournament">
          Save
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
    loading: false,
    error: false,
    menu: false,
    disabledDates: {
      to: new Date(Date.now() - 8640000)
    },

    id: null,
    name: null,
    game: null,
    duration: null,
    pause: null,
    limitDate: null,
    nbrTeams: null,
    streamUrl: null
  }),
  methods: {
    show() {
      this.isVisible = true
    },
    hide() {
      this.error = false
      this.$refs.form.reset()
      this.isVisible = false
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
          organizer: this.$store.state.authUser.name
        }

        const response = await WtmApi.Request(
          'post',
          this.$store.state.apiUrl + 'tournaments/',
          tournament,
          this.$store.getters.getAxiosConfig
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
    }
  }
}
</script>
