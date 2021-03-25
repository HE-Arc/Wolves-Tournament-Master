+<template>
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

<style lang="scss">
$side-margin: 50px;
$vertical-margin: 10px;
$line-color: black;

.wrapper {
  display: flex;
  height: auto;
  width: 100%;
  justify-content: center;
}

.item {
  display: flex;
  flex-direction: row-reverse;

  &-parent {
    position: relative;
    margin-left: $side-margin;
    display: flex;
    align-items: center;
    &:after {
      position: absolute;
      content: '';
      width: $side-margin/2;
      height: 2px;
      left: 0;
      top: 50%;
      background-color: $line-color;
      transform: translateX(-100%);
    }
  }
  &-childrens {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  &-child {
    display: flex;
    align-items: flex-start;
    justify-content: flex-end;
    margin-top: $vertical-margin;
    margin-bottom: $vertical-margin;
    position: relative;
    &:before {
      content: '';
      position: absolute;
      background-color: $line-color;
      right: 0;
      top: 50%;
      transform: translateX(100%);
      width: 25px;
      height: 2px;
    }
    &:after {
      content: '';
      position: absolute;
      background-color: $line-color;
      right: -$side-margin / 2;
      height: calc(50% + 22px);
      width: 2px;
      top: 50%;
    }
    &:last-child {
      &:after {
        transform: translateY(-100%);
      }
    }
    &:only-child:after {
      display: none;
    }
  }
}
</style>
