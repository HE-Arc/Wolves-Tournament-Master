<template>
  <v-card>
    <MatchResultDialog ref="matchResultDialog" />
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-header>
          {{ this.teamName }}
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <p>Match 1 : {{ this.scoreMatch1 }}</p>
          <p>Match 2 : {{ this.scoreMatch2 }}</p>
          <v-btn tile outlined @click="OpenMatchResultDialog"
            >Ajouter un résultat</v-btn
          >
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-card>
</template>

<script>
import MatchResultDialog from '@/components/dialogs/MatchResultDialog'

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
    },
    match: {
      type: Object
    }
  },
  components: { MatchResultDialog },
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
    async OpenMatchResultDialog(match) {
      this.$refs.matchResultDialog.show(match)
    }
  }
}
</script>
