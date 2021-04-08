<template>
  <bracket :rounds="rounds">
    <template slot="player" slot-scope="{ player }">
      {{ player.name }}
    </template>
  </bracket>
</template>

<script>
import Bracket from 'vue-tournament-bracket'

const rounds = [
  //quarter finals
  // {
  //   games: [
  //     {
  //       player1: { id: '1', name: 'A', winner: false },
  //       player2: { id: '4', name: 'B', winner: true }
  //     },
  //     {
  //       player1: { id: '5', name: 'C', winner: false },
  //       player2: { id: '8', name: 'D', winner: true }
  //     },
  //     {
  //       player1: { id: '5', name: 'E', winner: true },
  //       player2: { id: '0', name: 'none', winner: false }
  //     },
  //     {
  //       player1: { id: '5', name: 'E', winner: true },
  //       player2: { id: '0', name: 'none', winner: false }
  //     }
  //   ]
  // },
  //Semi finals
  // {
  //   games: [
  //     {
  //       player1: { id: '4', name: 'B', winner: false },
  //       player2: { id: '8', name: 'D', winner: true }
  //     },
  //     {
  //       player1: { id: '5', name: 'E', winner: false },
  //       player2: { id: '0', name: 'None', winner: true }
  //     }
  //   ]
  // },
  // //Final
  // {
  //   games: [
  //     {
  //       player1: { id: '0', name: 'tbd', winner: false },
  //       player2: { id: '0', name: 'tbd', winner: true }
  //     }
  //   ]
  // }
]

export default {
  components: {
    Bracket
  },
  mounted() {
    this.createRounds()
  },
  data() {
    return {
      rounds: rounds,
      nbTeams: 7,
      teams: [
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
    }
  },
  methods: {
    createGame(p1Id, p2Id, p1Name, p2Name, isP1Win, isP2Win) {
      return {
        player1: { id: p1Id, name: p1Name, winner: isP1Win },
        player2: { id: p2Id, name: p2Name, winner: isP2Win }
      }
    },
    createRounds() {
      let nbMatches = parseInt((this.nbTeams + 1) / 2)
      let nbRounds = Math.sqrt(nbMatches) + 1

      // create first matches with teams
      let teamGames = []
      for (let teamId = 0; teamId < this.nbTeams; teamId += 2) {
        let team1 = this.teams[teamId]
        let team2 = {
          id: 0,
          name: 'none'
        }

        if (teamId + 1 < this.nbTeams) {
          team2 = this.teams[teamId + 1]
        }

        teamGames.push(
          this.createGame(
            team1.id.toString(),
            team2.id.toString(),
            team1.name,
            team2.name,
            true,
            true
          )
        )
      }

      rounds.push({
        games: teamGames
      })

      console.log(nbRounds)

      // create other empty matches
      for (let round = nbRounds - 2; round >= 0; --round) {
        let games = []

        for (let match = 0; match < Math.pow(2, round); ++match) {
          games.push(this.createGame('-1', '-1', 'tbd', 'tbd', true, true))
        }

        rounds.push({
          games: games
        })
      }
      // let games2 = []
      // games2.push(this.createGame('1', '2', 'A', 'B', true))
      // games2.push(this.createGame('3', '4', 'C', 'D', true))

      // let games1 = []
      // games1.push(this.createGame('1', '4', 'A', 'D', false))

      // rounds.push({
      //   games: games2
      // })

      // rounds.push({
      //   games: games1
      // })
    }
  }
}
</script>
