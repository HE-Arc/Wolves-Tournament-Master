<template>
  <v-dialog v-model="isVisible" persistent max-width="500px">
    <v-card>
      <v-toolbar dark color="#01002a">
        <v-toolbar-title>Delete {{ item.name }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn v-show="!loading" icon dark @click="hide">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-card-title></v-card-title>
      <v-card-text>
        You realy want to delete "
        <span style="font-size:15px;font-weight:bold;">{{ item.name }}</span
        >" ?
      </v-card-text>
      <v-card-actions v-show="!loading">
        <v-spacer></v-spacer>
        <v-btn tile color="error" @click="hide">
          Cancel
          <v-icon right> mdi-close </v-icon>
        </v-btn>
        <v-btn tile color="success" @click="yes">
          Delete
          <v-icon right> mdi-delete </v-icon>
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
    title: '',
    message: 'An error occured... Please try later',
    loading: false,
    isVisible: false,
    item: {
      name: ''
    },
    error: false
  }),
  props: {
    action: { type: Function, required: true }
  },
  methods: {
    /**
     * To show the modal
     *
     * @param {Object} item item to delete
     */
    show(item) {
      this.isVisible = true
      this.item = item
    },

    // To hide the modal
    hide() {
      this.loading = false
      this.error = false
      this.isVisible = false
    },

    // Action to do when the logged user want to delete an item
    yes() {
      this.loading = true
      this.action(this.item)
    }
  }
}
</script>
