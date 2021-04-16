import axios from 'axios'

export default {
  // Generic axios request
  Request(method, url, data = null, header = null) {
    return new Promise(resolve => {
      axios({
        method: method, // 'get', 'post', 'put', 'delete'
        url: url, // this.$store.state.apiUrl + '/teams/',
        data: data, // { firstName: 'Fred', lastName: 'Flintstone'}
        headers: header // this.$store.getters.getAxiosHeader
      })
        .then(response => {
          resolve({ isSuccess: true, result: response.data })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  },

  // Request to get notifications and compute the number of unseen one
  GetNotifications(url, header) {
    return new Promise(resolve => {
      axios({
        method: 'get',
        url: url,
        headers: header
      })
        .then(response => {
          let notifNumber = response.data.filter(n => n.seen == false).length

          resolve({
            isSuccess: true,
            result: response.data,
            counter: notifNumber
          })
        })
        .catch(error => {
          resolve({ isSuccess: false, result: error })
        })
    })
  }
}
