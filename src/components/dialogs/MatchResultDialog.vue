<template>
  <v-dialog
    v-model="isVisible"
    max-width="500px"
    @keydown.esc="hide"
  >
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>Add a result</v-toolbar-title>
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
            v-model="result"
            label="Result"
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
        <v-btn tile color="success">
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
export default {
  data: () => ({
    isVisible: false,
    loading: false,
    error: false,

    id: null,
    result: null
  }),
  methods: {
    // To show the dialog
    show() {
      this.isVisible = true
    },
    hide() {
      this.error = false
      this.$refs.form.reset()
      this.isVisible = false
    }
  }
}
</script>
