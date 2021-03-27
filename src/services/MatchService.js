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
  CreateMatchs(matches) {
    /*
        Insert tournament tree into the db
    */
    matches.forEach(match => {
      if (match != null) {
        console.log(match.team1)
        console.log(match.team2)
        //first match is always null
        this.CreateMatch(match)
      }
    })
  }
}
