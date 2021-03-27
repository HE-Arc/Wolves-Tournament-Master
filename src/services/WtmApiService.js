import axios from 'axios'

export default {

  // Generic axios request
  Request(method, url, data, config) {
    return new Promise(resolve => {
      axios({
        method: method, // get, post, put, delete
        url: url, // this.$store.state.apiUrl + '/teams/',
        data: data, // { firstName: 'Fred', lastName: 'Flintstone'}
        config: config // this.$store.state.axiosConfig
      })
      .then(response => {
        resolve({ isSuccess: true, result: response.data })
      })
      .catch(error => {
        resolve({ isSuccess: false, result: error })
      })
    })
  }
}