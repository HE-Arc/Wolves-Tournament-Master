import axios from 'axios'

export default {
  apiurl: 'http://localhost:8000/api/',

  CreateMatch(match) {
    return new Promise(resolve => {
      axios
        .post(this.apiurl + 'matchs/', match)
        .then(response => {
          resolve({
            isSuccess: true,
            result: response.data
          })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  },
  CreateMatches(matches) {
    /*
        Insert tournament tree into the db
    */
    matches.forEach(match => {
      if (match != null) {
        this.CreateMatch(match)
      }
    })
  },
  GetMatchesByTournament(tournamentId) {
    return new Promise(resolve => {
      axios
        .get(this.apiurl + 'matchs?tid=' + tournamentId)
        .then(response => {
          resolve({
            isSuccess: true,
            result: response.data
          })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  }
}
