<template>
  <v-dialog
    v-model="isVisible"
    max-width="500px"
    @keydown.esc="hide"
    @click:outside="hide"
    @keydown.enter="SaveTeam"
  >
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>{{ title }}</v-toolbar-title>
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
            v-model="name"
            label="Name"
            dense
            outlined
            clearable
            v-validate="'required'"
            data-vv-name="Name"
            :error-messages="errors.collect('Name')"
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
        <v-btn tile color="success" @click="SaveTeam">
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
    parent: undefined,
    title: '',
    item: [],
    isUpdate: false,
    loading: false,
    error: false,

    id: null,
    name: '',
    leader: ''
  }),

  mounted() {},

  methods: {
    /**
     * To show the dialog
     *
     * @param {Object} parent parent who call the dialog
     * @param {String} titel title of the dialog
     * @param {Object} item team to update (if not null)
     * @param {Boolean} isUpdate to know if we want to update a team or not
     */

    show(parent, title, item, isUpdate) {
      this.parent = parent
      this.title = title
      this.item = item
      this.isUpdate = isUpdate

      if (isUpdate) {
        this.name = item.name
        this.leader = item.leader
      }

      this.isVisible = true
    },

    // To hide the dialog
    hide() {
      this.error = false
      this.$refs.form.reset()
      this.isVisible = false
    },

    // Determine the method to call on team save
    SaveTeam() {
      if (this.isUpdate) this.UpdateTeam()
      else this.CreateTeam()
    },

    // Create a new team
    async CreateTeam() {
      const result = await this.$validator.validate()

      if (result) {
        this.loading = true

        let team = {
          name: this.name,
          leader: this.$store.state.authUser.name
        }

        const response = await WtmApi.Request(
          'post',
          this.$store.state.apiUrl + 'teams/',
          team,
          this.$store.getters.getAxiosHeader
        )

        if (response.isSuccess) {
          this.$refs.form.reset()
          this.$snotify.success(team.name + ' added successfuly!')
          this.isVisible = false
          this.parent.GetTeams()
        } else {
          this.$snotify.error(
            'Unable to save this team...\nPlease try later...'
          )
          this.error = true
        }

        this.loading = false
      }
    },

    // Update the current team
    async UpdateTeam() {
      const result = await this.$validator.validate()

      if (result) {
        this.loading = true

        this.item.name = this.name
        this.item.leader = this.$store.state.authUser.name

        const response = await WtmApi.Request(
          'put',
          this.$store.state.apiUrl + 'teams/' + this.item.id + '/',
          this.item,
          this.$store.getters.getAxiosHeader
        )

        if (response.isSuccess) {
          this.$refs.form.reset()
          this.$snotify.success(this.item.name + ' updated successfuly!')
          this.isVisible = false
          this.parent.GetTeams()
        } else {
          this.$snotify.error(
            'Unable to update this formation...\nPlease try later...'
          )
          this.error = true
        }

        this.loading = false
      }
    }
  }
}
</script>
