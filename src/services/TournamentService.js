import axios from 'axios'

export default {
  apiurl: 'http://localhost:8000/api/',

  /*
    Backend access
  */
  GetTournaments() {
    return new Promise(resolve => {
      axios
        .get(this.apiurl + 'tournaments/')
        .then(response => {
          resolve({ isSuccess: true, result: response.data })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  },
  CreateTournament(tournament) {
    return new Promise(resolve => {
      axios
        .post(this.apiurl + 'tournaments/', tournament)
        .then(response => {
          resolve({ isSuccess: true, result: response.data })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  },
  /*
    Tournament tree logic
  */
  createGame(p1Id, p2Id, p1Name, p2Name, isP1Win, isP2Win) {
    return {
      player1: { id: p1Id, name: p1Name, winner: isP1Win },
      player2: { id: p2Id, name: p2Name, winner: isP2Win }
    }
  },
  createRounds(teams) {
    /*
        Generate base matches "all in code", without interactions with the DB
        and display the tournament brackets
    */

    let rounds = []
    let nbMatches = parseInt((teams.length + 1) / 2)
    let nbRounds = Math.sqrt(nbMatches) + 1

    // create first matches with teams
    let teamGames = []
    for (let teamId = 0; teamId < teams.length; teamId += 2) {
      let team1 = teams[teamId]
      let team2 = {
        id: 0,
        name: 'none'
      }

      if (teamId + 1 < teams.length) {
        team2 = teams[teamId + 1]
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

    return rounds
  },
  createBaseMatches(teams, tournamentId) {
    /*
        Create matches objects with the base matches. They'll be pushed in the DB
    */

    let nbMatches = parseInt((teams.length + 1) / 2)
    let nbRounds = Math.sqrt(nbMatches) + 1

    // create first matches with teams

    let idInTournament = 1 // child have lower id than parents, the rounds start from the bottom (leafs)
    let matches = []
    for (let teamId = 0; teamId < teams.length; teamId += 2) {
      let team1 = teams[teamId]
      let team2 = {
        id: null,
        name: 'tbd'
      }

      if (teamId + 1 < teams.length) {
        team2 = teams[teamId + 1]
      }

      matches.push({
        team1: team1.id,
        team2: team2.id,
        tournament: tournamentId,
        score1: null,
        score2: null,
        idInTournament: idInTournament,
        idParent: null //still usefull ? Perhaps for the update, check it later
      })

      ++idInTournament
    }

    // create other matches. They're all empty at tournament creation
    // TODO optimize it
    for (let round = nbRounds - 2; round >= 0; --round) {
      for (let match = 0; match < Math.pow(2, round); ++match) {
        matches.push({
          team1: null,
          team2: null,
          tournament: tournamentId,
          score1: null,
          score2: null,
          idInTournament: idInTournament,
          idParent: null //still usefull ? Perhaps for the update, check it later
        })
        ++idInTournament
      }
    }

    return matches
  }
}
