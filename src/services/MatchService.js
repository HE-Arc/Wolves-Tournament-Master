export default {
  apiurl: 'http://localhost:8000/api/',

  CreateMatchs(matches) {
    /*
        Insert tournament tree into the db
    */
    console.log(matches)
  },
  CreateMatch(match) {
    console.log(match)
    // return new Promise(resolve => {
    //     axios
    //       .post(this.apiurl + 'match/', team)
    //       .then(response => {
    //         resolve({
    //           isSuccess: true,
    //           result: response.data
    //         })
    //       })
    //       .catch(error => {
    //         resolve({ isSuccess: false, result: error })
    //       })
    //   })
  }
}
