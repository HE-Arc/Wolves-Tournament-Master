<template>
  <bracket :rounds="rounds">
    <template slot="player" slot-scope="{ player }">
      {{ player.name }}
    </template>
  </bracket>
</template>

<script>
import Bracket from 'vue-tournament-bracket'
import MatchService from '@/services/MatchService'
import TournamentService from '@/services/TournamentService'

const teams = [
  {
    id: 1,
    name: 'A'
  },
  {
    id: 2,
    name: 'B'
  },
  {
    id: 3,
    name: 'C'
  },
  {
    id: 4,
    name: 'D'
  },
  {
    id: 5,
    name: 'E'
  },
  {
    id: 6,
    name: 'F'
  },
  {
    id: 7,
    name: 'G'
  }
]

export default {
  components: {
    Bracket
  },
  mounted() {
    // TODO only for tests, remove it after first matchs creation
    // let matches = TournamentService.createBaseMatches(teams)
    // MatchService.CreateMatches(matches)
  },
  data() {
    return {
      teams: teams,
      rounds: TournamentService.createRounds(teams)
    }
  }
}
</script>
