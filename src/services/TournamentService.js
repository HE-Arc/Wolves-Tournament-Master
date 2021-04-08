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
    /*
        just create a game (node) for the bracket    
    */
    return {
      player1: { id: p1Id, name: p1Name, winner: isP1Win },
      player2: { id: p2Id, name: p2Name, winner: isP2Win }
    }
  },
  createRounds(matches, teams) {
    /*
        Generate brackets from matches.
    */
    let rounds = []
    let nbRounds = parseInt(Math.sqrt(matches.length)) + 1

    // the match array should be sorted according to idInTournament at this stage
    let matchId = 0

    // get every match from every round. To display the brackets correctly,
    // the matches of the same round should be in the same subarray
    for (let round = nbRounds - 1; round >= 0; --round) {
      let games = []
      for (
        let matchInRound = 0;
        matchInRound < Math.pow(2, round);
        ++matchInRound
      ) {
        if (matchId < matches.length) {
          // go through all matches on each round
          let currentMatch = matches[matchId]
          let emptyTeam = {
            id: 0,
            name: 'none'
          }

          // prepare teams
          let team1 =
            currentMatch.team1 != null
              ? teams[currentMatch.team1 - 1]
              : emptyTeam

          let team2 =
            currentMatch.team2 != null
              ? teams[currentMatch.team2 - 1]
              : emptyTeam

          // add teams into the game
          games.push(
            this.createGame(
              team1.id,
              team2.id,
              team1.name,
              team2.name,
              true, //TODO put results here !
              true //TODO put results here !
            )
          ) // get teams to put team name here !

          ++matchId
        }
      }

      // add matches of this round in the brackets
      rounds.push({
        games: games
      })
    }

    return rounds
  },
  createBaseMatches(teams, tournamentId) {
    /*
        Create matches objects with the teams. Fill only the leaf matches.
        They'll be pushed in the DB at tournament creation
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
      for (
        let matchInRound = 0;
        matchInRound < Math.pow(2, round);
        ++matchInRound
      ) {
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
