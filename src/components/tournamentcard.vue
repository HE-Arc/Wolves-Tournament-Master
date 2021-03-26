<template>
  <v-card>
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-header>
          {{ this.teamName }}
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <p>Match 1 : {{ this.scoreMatch1 }}</p>
          <p>Match 2 : {{ this.scoreMatch2 }}</p>
          <v-btn tile outlined>Ajouter un résultat</v-btn>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
export default {
  props: {
    idMatch: {
      type: Number,
      required: true
    },
    teamName: {
      type: String,
      required: true
    },
    scoreMatch1: {
      type: String // score team 1 - score team 2
    },
    scoreMatch2: {
      type: String // score team 1 - score team 2
    }
  },
  components: {},
  data: () => ({
    // empty
  }),
  mounted: function() {
    // initialize components
  },
  watch: {
    // watch a prop modified from the outside
  },
  methods: {
    // empty
  }
}
</script>
