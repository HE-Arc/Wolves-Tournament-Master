<template>
  <v-dialog
    v-model="isVisible"
    max-width="500px"
    @keydown.esc="hide"
    @click:outside="hide"
  >
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>
          Add a result : {{ item.player1.name }} VS
          {{ item.player2.name }}
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn icon dark @click="hide">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-title></v-card-title>
      <v-card-text>
        <v-form ref="form" style="padding:10px;">
          <v-text-field
            v-model="item.match.score1"
            :label="'Score: ' + item.player1.name"
            dense
            outlined
            clearable
            v-validate="'required|numeric'"
            data-vv-name="result"
            :error-messages="errors.collect('result')"
          ></v-text-field>
          <v-text-field
            v-model="item.match.score2"
            :label="'Score: ' + item.player2.name"
            dense
            outlined
            clearable
            v-validate="'required|numeric'"
            data-vv-name="result"
            :error-messages="errors.collect('result')"
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
        <v-btn tile color="success" @click="UpdateMatch">
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

    item: {
      team1: '',
      team2: ''
    }
  }),
  methods: {
    // To show the dialog
    show(item) {
      this.isVisible = true
      this.item = item
    },
    hide() {
      this.error = false
      this.$refs.form.reset()
      this.isVisible = false
    },
    async UpdateMatch() {
      const result = await this.$validator.validate()

      if (result) {
        this.loading = true

        const response = await WtmApi.Request(
          'put',
          this.$store.state.apiUrl +
            'matchs/' +
            this.item.match.id +
            '/updatematchscores/',
          this.item.match,
          this.$store.getters.getAxiosHeader
        )

        if (response.isSuccess) {
          this.$refs.form.reset()
          this.$snotify.success('Scores updated successfuly!')

          this.$store.commit('setUpdateTournamentBracket')

          this.isVisible = false
        } else {
          this.$snotify.error(
            'Unable to update this match...\nPlease try later...'
          )
          this.error = true
        }
        this.loading = false
      }
    }
  }
}
</script>
